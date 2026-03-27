import os
import sys
import json
import time
import traceback
import subprocess
import gc
import threading
import signal
import ctypes
from datetime import datetime
from flask import Flask, request, jsonify, Response
import psutil

# ============== 全局状态 ==============
runtime_variables = {}
start_time = time.time()
execution_lock = threading.Lock()
keep_running = True

# 执行状态跟踪
execution_state = {
    "current_directory": "/content",
    "is_executing": False,
    "last_command": "",
    "last_execution_time": 0,
    "last_error": None,
    "command_history": [],
    "installed_packages": set()
}

# 当前执行的线程引用
current_execution_thread = None
interrupt_requested = False

# 创建 Flask 应用
app = Flask(__name__)

# ============== 心跳保活线程 ==============
def heartbeat_thread():
    """心跳线程，防止 Colab 休眠"""
    import requests
    last_ping = time.time()

    while keep_running:
        try:
            current_time = time.strftime("%H:%M:%S")
            print(f"[心跳] {current_time} - 服务运行中 | 目录: {execution_state['current_directory']}", flush=True)

            if time.time() - last_ping > 300:
                try:
                    requests.get('http://localhost:5000/health', timeout=10)
                    last_ping = time.time()
                except:
                    pass

            time.sleep(30)
        except Exception as e:
            print(f"[心跳错误] {e}", flush=True)
            time.sleep(10)

# ============== 辅助函数 ==============
def _check_gpu():
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def _add_to_history(command, output_preview="", success=True):
    """添加命令到历史记录"""
    entry = {
        "command": command[:500],
        "output_preview": output_preview[:200],
        "timestamp": time.time(),
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "directory": execution_state["current_directory"],
        "success": success
    }
    execution_state["command_history"].append(entry)
    if len(execution_state["command_history"]) > 100:
        execution_state["command_history"] = execution_state["command_history"][-100:]

def _update_directory_from_code(code):
    """从代码中提取目录变化"""
    import re
    match = re.search(r"os\.chdir\(['\"]([^'\"]+)['\"]\)", code)
    if match:
        new_dir = match.group(1)
        execution_state["current_directory"] = new_dir
        return new_dir
    return None

def _interrupt_thread(thread):
    """尝试中断线程中的执行"""
    global interrupt_requested
    interrupt_requested = True
    if thread and thread.is_alive():
        try:
            thread_id = thread.ident
            if thread_id:
                exc = KeyboardInterrupt()
                ctypes.pythonapi.PyThreadState_SetAsyncExc(
                    ctypes.c_long(thread_id),
                    ctypes.py_object(exc)
                )
        except Exception as e:
            print(f"[中断] 尝试中断失败: {e}", flush=True)
    return True

# ============== API Endpoints ==============
@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "name": "ColabCLI Server",
        "version": "2.0.0",
        "status": "running",
        "uptime_minutes": round((time.time() - start_time) / 60, 2),
        "current_directory": execution_state["current_directory"],
        "is_executing": execution_state["is_executing"],
        "endpoints": ["/health", "/probe", "/execute", "/interrupt", "/status", "/history", "/variables", "/files", "/cleanup"]
    })

@app.route('/health', methods=['GET'])
def health_check():
    mem = psutil.virtual_memory()
    return jsonify({
        "status": "ok",
        "uptime_minutes": round((time.time() - start_time) / 60, 2),
        "memory_available_gb": round(mem.available / (1024**3), 2),
        "memory_total_gb": round(mem.total / (1024**3), 2),
        "memory_used_pct": round(mem.percent, 2),
        "gpu_available": _check_gpu(),
        "current_directory": execution_state["current_directory"],
        "is_executing": execution_state["is_executing"]
    })

@app.route('/status', methods=['GET'])
def get_status():
    """获取详细执行状态"""
    return jsonify({
        "status": "ok",
        "current_directory": execution_state["current_directory"],
        "is_executing": execution_state["is_executing"],
        "last_command": execution_state["last_command"],
        "last_execution_time": execution_state["last_execution_time"],
        "last_error": execution_state["last_error"],
        "recent_history": [h["command"] for h in execution_state["command_history"][-5:]],
        "uptime_minutes": round((time.time() - start_time) / 60, 2)
    })

@app.route('/history', methods=['GET'])
def get_history():
    """获取命令历史"""
    limit = request.args.get('limit', 20, type=int)
    limit = min(limit, 100)
    history = execution_state["command_history"][-limit:]
    return jsonify({"history": history, "total": len(execution_state["command_history"])})

@app.route('/interrupt', methods=['POST'])
def interrupt_execution():
    """中断当前执行（不停止服务器）"""
    global interrupt_requested, current_execution_thread

    if not execution_state["is_executing"]:
        return jsonify({"success": True, "message": "当前没有正在执行的任务"})

    interrupt_requested = True

    if current_execution_thread and current_execution_thread.is_alive():
        success = _interrupt_thread(current_execution_thread)
        if success:
            execution_state["is_executing"] = False
            execution_state["last_error"] = "用户中断"
            return jsonify({"success": True, "message": "已发送中断信号"})
        else:
            return jsonify({"success": False, "message": "中断失败，请稍后重试"})

    return jsonify({"success": True, "message": "中断请求已处理"})

@app.route('/probe', methods=['GET'])
def probe_environment():
    gpu_info = ""
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,memory.free', '--format=csv'],
                              capture_output=True, text=True, timeout=10)
        gpu_info = result.stdout
    except:
        gpu_info = "No GPU available"

    installed_packages = []
    try:
        result = subprocess.run(['pip', 'list', '--format=freeze'], capture_output=True, text=True, timeout=30)
        for line in result.stdout.split('\n'):
            if '==' in line:
                installed_packages.append(line.strip())
    except:
        pass

    mem = psutil.virtual_memory()

    return jsonify({
        "gpu_info": gpu_info,
        "memory_total_gb": round(mem.total / (1024**3), 2),
        "memory_available_gb": round(mem.available / (1024**3), 2),
        "python_version": sys.version,
        "current_directory": execution_state["current_directory"],
        "installed_packages": installed_packages[:100],
        "total_packages": len(installed_packages)
    })

@app.route('/execute', methods=['POST'])
def execute_code():
    """执行 Python 代码，带错误隔离和状态跟踪"""
    global current_execution_thread, interrupt_requested

    if not execution_lock.acquire(blocking=False):
        return jsonify({"success": False, "error": "另一个代码正在执行中，请稍后重试"})

    interrupt_requested = False
    current_execution_thread = threading.current_thread()

    try:
        data = request.get_json()
        code = data.get('code', '')
        timeout = min(data.get('timeout', 300), 600)

        if not code:
            return jsonify({"success": False, "error": "No code provided"})

        execution_state["is_executing"] = True
        execution_state["last_command"] = code[:200] + "..." if len(code) > 200 else code

        exec_globals = {'__builtins__': __builtins__, **runtime_variables}
        exec_locals = {}

        from io import StringIO
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = captured_stdout = StringIO()
        sys.stderr = captured_stderr = StringIO()

        start_exec_time = time.time()

        try:
            if interrupt_requested:
                raise KeyboardInterrupt("执行被用户中断")

            exec(code, exec_globals, exec_locals)

            if interrupt_requested:
                raise KeyboardInterrupt("执行被用户中断")

            for key, value in exec_locals.items():
                if not key.startswith('_'):
                    try:
                        json.dumps({key: str(type(value))})
                        runtime_variables[key] = value
                    except:
                        pass

            _update_directory_from_code(code)
            stdout_val = captured_stdout.getvalue()
            _add_to_history(code, stdout_val, success=True)

            execution_state["last_execution_time"] = time.time() - start_exec_time
            execution_state["last_error"] = None

            return jsonify({
                "success": True,
                "stdout": stdout_val,
                "stderr": captured_stderr.getvalue(),
                "execution_time_sec": round(time.time() - start_exec_time, 3),
                "variables": list(exec_locals.keys()),
                "current_directory": execution_state["current_directory"]
            })

        except KeyboardInterrupt:
            stdout_val = captured_stdout.getvalue()
            _add_to_history(code, stdout_val, success=False)
            execution_state["last_error"] = "用户中断"
            return jsonify({
                "success": False,
                "error": "执行被用户中断",
                "error_type": "KeyboardInterrupt",
                "stdout": stdout_val,
                "stderr": captured_stderr.getvalue(),
                "execution_time_sec": round(time.time() - start_exec_time, 3)
            })

        except Exception as e:
            stdout_val = captured_stdout.getvalue()
            _add_to_history(code, stdout_val, success=False)
            execution_state["last_error"] = str(e)
            return jsonify({
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc(),
                "stdout": stdout_val,
                "stderr": captured_stderr.getvalue(),
                "execution_time_sec": round(time.time() - start_exec_time, 3)
            })

        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            execution_state["is_executing"] = False

    except Exception as e:
        execution_state["is_executing"] = False
        return jsonify({
            "success": False,
            "error": f"服务器内部错误: {str(e)}",
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        })

    finally:
        execution_lock.release()
        current_execution_thread = None

@app.route('/variables', methods=['GET'])
def list_variables():
    vars_info = {}
    for key, value in runtime_variables.items():
        try:
            var_info = {"type": str(type(value).__name__)}
            if hasattr(value, 'shape'):
                var_info["shape"] = list(value.shape) if hasattr(value.shape, '__iter__') else str(value.shape)
            if hasattr(value, '__len__'):
                try:
                    var_info["length"] = len(value)
                except:
                    pass
            vars_info[key] = var_info
        except:
            vars_info[key] = {"type": str(type(value).__name__)}

    return jsonify({
        "variables": vars_info,
        "count": len(vars_info),
        "current_directory": execution_state["current_directory"]
    })

@app.route('/files', methods=['GET'])
def list_files():
    content_dir = execution_state.get("current_directory", "/content")
    dir_param = request.args.get('dir', None)
    if dir_param:
        content_dir = dir_param

    files = []
    try:
        for f in os.listdir(content_dir):
            path = os.path.join(content_dir, f)
            try:
                size = os.path.getsize(path)
                files.append({
                    "name": f,
                    "path": path,
                    "size_bytes": size,
                    "size_readable": f"{size/1024:.1f} KB" if size < 1024*1024 else f"{size/1024/1024:.1f} MB",
                    "is_dir": os.path.isdir(path)
                })
            except:
                pass
    except Exception as e:
        return jsonify({"error": str(e), "files": [], "directory": content_dir})

    return jsonify({"files": files, "count": len(files), "directory": content_dir})

@app.route('/cleanup', methods=['POST'])
def cleanup():
    global runtime_variables
    runtime_variables = {}
    gc.collect()

    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except:
        pass

    mem = psutil.virtual_memory()
    return jsonify({
        "success": True,
        "message": "Memory cleaned",
        "memory_available_gb": round(mem.available / (1024**3), 2)
    })

def signal_handler(sig, frame):
    global keep_running
    print("\n[信号] 收到停止信号，正在关闭...")
    keep_running = False
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("\n" + "="*60)
    print("🚀 ColabCLI 服务器启动中...")
    print("="*60)
    print("版本: 2.0.0")
    print("功能: 心跳保活 + 错误隔离 + 中断支持 + 状态跟踪")
    print("="*60 + "\n")

    heartbeat = threading.Thread(target=heartbeat_thread, daemon=True)
    heartbeat.start()

    try:
        app.run(port=5000, host='0.0.0.0', threaded=True)
    except Exception as e:
        print(f"[错误] Flask 启动失败: {e}")
        raise
