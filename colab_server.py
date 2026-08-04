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
import queue
import re
from datetime import datetime
from flask import Flask, request, jsonify, Response
import psutil

# ============== i18n ==============
_LANG = os.environ.get('COLABMCP_LANG', 'en').lower()
if _LANG not in ('en', 'zh'):
    _LANG = 'en'

def t(key, **kwargs):
    """Get translated string by key, with optional format arguments."""
    translations = {
        'en': {
            'server_starting': '🚀 ColabCLI server starting...',
            'server_version': 'Version: {version}',
            'server_features': 'Features: {features}',
            'server_optimization': 'Optimization: {optimization}',
            'server_stopped': 'Stop signal received, shutting down...',
            'server_internal_error': 'Internal server error: {error}',
            'server_start_failed': '[Error] Flask failed to start: {error}',
            'no_code_provided': 'No code provided',
            'execution_interrupted': 'Execution interrupted by user',
            'execution_interrupted_msg': '⚠️ Execution interrupted by user',
            'interrupt_sent': 'Interrupt signal sent',
            'interrupt_failed_msg': 'Interrupt failed, please try again later',
            'interrupt_processed': 'Interrupt request processed',
            'no_running_task': 'No running task',
            'user_interrupt': 'User interrupt',
            'server_busy': 'Another code is executing, please try again later',
            'executing_shell': 'Executing: {cmd}',
            'executing_python': 'Executing Python code...',
            'complete_shell': '✅ Done (exit code: {code}, time: {time}s)',
            'complete_python': '✅ Done (time: {time}s)',
            'error_prefix': '❌ Error: {error}',
            'interrupt_history': 'Interrupted',
            'signal_received': '[Signal] Stop signal received, shutting down...',
            'interrupt_attempt_failed': '[Interrupt] Failed to interrupt: {error}',
            'heartbeat': '[Heartbeat] {time} - Running | Directory: {directory}{exec_flag}',
            'heartbeat_error': '[Heartbeat Error] {error}',
            'interrupt_flag': ' [Executing]',
            'gpu_no_available': 'No GPU available',
            'memory_cleaned': 'Memory cleaned',
        },
        'zh': {
            'server_starting': '🚀 ColabCLI 服务器启动中...',
            'server_version': '版本: {version}',
            'server_features': '功能: {features}',
            'server_optimization': '优化: {optimization}',
            'server_stopped': '收到停止信号，正在关闭...',
            'server_internal_error': '服务器内部错误: {error}',
            'server_start_failed': '[错误] Flask 启动失败: {error}',
            'no_code_provided': '未提供代码',
            'execution_interrupted': '执行被用户中断',
            'execution_interrupted_msg': '⚠️ 执行被用户中断',
            'interrupt_sent': '已发送中断信号',
            'interrupt_failed_msg': '中断失败，请稍后重试',
            'interrupt_processed': '中断请求已处理',
            'no_running_task': '当前没有正在执行的任务',
            'user_interrupt': '用户中断',
            'server_busy': '另一个代码正在执行中，请稍后重试',
            'executing_shell': '执行: {cmd}',
            'executing_python': '执行 Python 代码...',
            'complete_shell': '✅ 完成 (退出码: {code}, 耗时: {time}s)',
            'complete_python': '✅ 完成 (耗时: {time}s)',
            'error_prefix': '❌ 错误: {error}',
            'interrupt_history': '中断',
            'signal_received': '[信号] 收到停止信号，正在关闭...',
            'interrupt_attempt_failed': '[中断] 尝试中断失败: {error}',
            'heartbeat': '[心跳] {time} - 运行中 | 目录: {directory}{exec_flag}',
            'heartbeat_error': '[心跳错误] {error}',
            'interrupt_flag': ' [执行中]',
            'gpu_no_available': '无可用 GPU',
            'memory_cleaned': '内存已清理',
        },
    }
    template = translations.get(_LANG, translations['en']).get(key, key)
    if kwargs:
        try:
            return template.format(**kwargs)
        except (KeyError, IndexError):
            return template
    return template

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

# 流式输出队列
stream_output_queue = None
stream_active = False

# 创建 Flask 应用
app = Flask(__name__)

# ============== 心跳保活线程 ==============
def heartbeat_thread():
    """心跳线程，防止 Colab 休眠"""
    last_ping = time.time()

    while keep_running:
        try:
            current_time = time.strftime("%H:%M:%S")
            is_exec = execution_state['is_executing']
            exec_flag = t('interrupt_flag') if is_exec else ""
            print(t('heartbeat', time=current_time, directory=execution_state['current_directory'], exec_flag=exec_flag), flush=True)

            # 不再请求 /health 端点，避免与执行锁冲突
            # Colab 自身有保活机制，只需打印日志即可
            last_ping = time.time()

            time.sleep(60)  # 30→60秒，减少心跳频率
        except Exception as e:
            print(t('heartbeat_error', error=str(e)), flush=True)
            time.sleep(30)

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
            print(t('interrupt_attempt_failed', error=str(e)), flush=True)
    return True

# ============== API Endpoints ==============
@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "name": "ColabCLI Server",
        "version": "2.2.0",
        "status": "running",
        "uptime_minutes": round((time.time() - start_time) / 60, 2),
        "current_directory": execution_state["current_directory"],
        "is_executing": execution_state["is_executing"],
        "endpoints": ["/health", "/probe", "/execute", "/execute_stream", "/interrupt", "/status", "/history", "/variables", "/files", "/cleanup"]
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
        return jsonify({"success": True, "message": t('no_running_task')})

    interrupt_requested = True

    if current_execution_thread and current_execution_thread.is_alive():
        success = _interrupt_thread(current_execution_thread)
        if success:
            execution_state["is_executing"] = False
            execution_state["last_error"] = t('user_interrupt')
            return jsonify({"success": True, "message": t('interrupt_sent')})
        else:
            return jsonify({"success": False, "message": t('interrupt_failed_msg')})

    return jsonify({"success": True, "message": t('interrupt_processed')})

@app.route('/probe', methods=['GET'])
def probe_environment():
    gpu_info = ""
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,memory.free', '--format=csv'],
                              capture_output=True, text=True, timeout=10)
        gpu_info = result.stdout
    except:
        gpu_info = t('gpu_no_available')

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
        return jsonify({"success": False, "error": t('server_busy')})

    interrupt_requested = False
    current_execution_thread = threading.current_thread()

    try:
        data = request.get_json()
        code = data.get('code', '')
        timeout = min(data.get('timeout', 600), 1800)

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
                raise KeyboardInterrupt(t('execution_interrupted'))

            exec(code, exec_globals, exec_locals)

            if interrupt_requested:
                raise KeyboardInterrupt(t('execution_interrupted'))

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
            execution_state["last_error"] = t('user_interrupt')
            return jsonify({
                "success": False,
                "error": t('execution_interrupted'),
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
            "error": t('server_internal_error', error=str(e)),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        })

    finally:
        execution_lock.release()
        current_execution_thread = None

@app.route('/execute_stream', methods=['POST'])
def execute_code_stream():
    """
    流式执行代码 - 使用 SSE 实时推送输出。
    支持：
    1. shell 命令 (!cmd) - 使用 Popen 实时读取
    2. Python 代码 - 使用线程实时推送 stdout
    """
    global stream_output_queue, stream_active, interrupt_requested

    def generate_sse(output_queue):
        """SSE 生成器"""
        try:
            while True:
                try:
                    msg = output_queue.get(timeout=0.5)
                    if msg is None:  # 结束信号
                        break
                    yield f"data: {json.dumps(msg, ensure_ascii=False)}\n\n"
                except queue.Empty:
                    # 发送心跳保持连接
                    yield f": heartbeat\n\n"
                    continue
        except GeneratorExit:
            pass

    # 创建输出队列
    stream_output_queue = queue.Queue()
    stream_active = True
    interrupt_requested = False

    data = request.get_json()
    code = data.get('code', '')
    timeout = min(data.get('timeout', 600), 1800)

    if not code:
        stream_output_queue.put({"type": "error", "content": "No code provided"})
        stream_output_queue.put(None)
        return Response(generate_sse(stream_output_queue), mimetype='text/event-stream')

    execution_state["is_executing"] = True
    execution_state["last_command"] = code[:200] + "..." if len(code) > 200 else code

    # 检测是否是 shell 命令
    stripped_code = code.strip()

    # 情况1: 单独的 shell 命令 (以 ! 开头)
    shell_match = re.match(r'^import subprocess; result = subprocess\.run\([\'"](.+?)[\'"], shell=True', stripped_code)
    if shell_match:
        shell_cmd = shell_match.group(1)

        def run_shell_command():
            global stream_active
            start_time = time.time()
            stream_output_queue.put({"type": "status", "content": t('executing_shell', cmd=shell_cmd)})

            try:
                process = subprocess.Popen(
                    shell_cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,  # 行缓冲
                    cwd=execution_state["current_directory"]
                )

                # 实时读取输出
                import select
                while True:
                    if interrupt_requested:
                        process.terminate()
                        stream_output_queue.put({"type": "error", "content": t('execution_interrupted')})
                        break

                    # 检查进程是否结束
                    retcode = process.poll()
                    read_ready, _, _ = select.select([process.stdout, process.stderr], [], [], 0.1)

                    for stream in read_ready:
                        if stream == process.stdout:
                            line = process.stdout.readline()
                            if line:
                                stream_output_queue.put({"type": "stdout", "content": line})
                        elif stream == process.stderr:
                            line = process.stderr.readline()
                            if line:
                                stream_output_queue.put({"type": "stderr", "content": line})

                    if retcode is not None:
                        # 读取剩余输出
                        remaining_stdout, remaining_stderr = process.communicate()
                        if remaining_stdout:
                            stream_output_queue.put({"type": "stdout", "content": remaining_stdout})
                        if remaining_stderr:
                            stream_output_queue.put({"type": "stderr", "content": remaining_stderr})
                        break

                elapsed = time.time() - start_time
                stream_output_queue.put({
                    "type": "complete",
                    "content": t('complete_shell', code=process.returncode, time=f"{elapsed:.2f}")
                })
                _add_to_history(code, f"shell: {shell_cmd}", success=True)
                execution_state["last_execution_time"] = elapsed

            except Exception as e:
                stream_output_queue.put({"type": "error", "content": str(e)})
                _add_to_history(code, str(e), success=False)
            finally:
                stream_output_queue.put(None)  # 结束信号
                stream_active = False
                execution_state["is_executing"] = False

        thread = threading.Thread(target=run_shell_command, daemon=True)
        thread.start()

    # 情况2: Python 代码执行
    else:
        class StreamingOutput:
            """流式输出捕获器"""
            def __init__(self, q, stream_type):
                self.queue = q
                self.stream_type = stream_type
                self.buffer = []

            def write(self, text):
                if text:
                    self.buffer.append(text)
                    self.queue.put({"type": self.stream_type, "content": text})

            def flush(self):
                pass

            def getvalue(self):
                return ''.join(self.buffer)

        def run_python_code():
            global stream_active
            start_time = time.time()
            stream_output_queue.put({"type": "status", "content": t('executing_python')})

            old_stdout = sys.stdout
            old_stderr = sys.stderr
            stdout_capture = StreamingOutput(stream_output_queue, 'stdout')
            stderr_capture = StreamingOutput(stream_output_queue, 'stderr')
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture

            exec_globals = {'__builtins__': __builtins__, **runtime_variables}
            exec_locals = {}

            try:
                if interrupt_requested:
                    raise KeyboardInterrupt(t('execution_interrupted'))

                exec(code, exec_globals, exec_locals)

                if interrupt_requested:
                    raise KeyboardInterrupt(t('execution_interrupted'))

                # 保存变量
                for key, value in exec_locals.items():
                    if not key.startswith('_'):
                        try:
                            runtime_variables[key] = value
                        except:
                            pass

                _update_directory_from_code(code)
                elapsed = time.time() - start_time
                stream_output_queue.put({
                    "type": "complete",
                    "content": t('complete_python', time=f"{elapsed:.2f}"),
                    "variables": list(exec_locals.keys())
                })
                _add_to_history(code, ''.join(stdout_capture.buffer)[:200], success=True)
                execution_state["last_execution_time"] = elapsed

            except KeyboardInterrupt:
                stream_output_queue.put({"type": "error", "content": t('execution_interrupted_msg')})
                _add_to_history(code, t('interrupt_history'), success=False)
            except Exception as e:
                stream_output_queue.put({
                    "type": "error",
                    "content": t('error_prefix', error=f"{type(e).__name__}: {str(e)}")
                })
                _add_to_history(code, str(e), success=False)
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                stream_output_queue.put(None)  # 结束信号
                stream_active = False
                execution_state["is_executing"] = False

        thread = threading.Thread(target=run_python_code, daemon=True)
        thread.start()

    return Response(generate_sse(stream_output_queue), mimetype='text/event-stream')

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
        "message": t('memory_cleaned'),
        "memory_available_gb": round(mem.available / (1024**3), 2)
    })

def signal_handler(sig, frame):
    global keep_running
    print("\n" + t('signal_received'))
    keep_running = False
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("\n" + "="*60)
    print(t('server_starting'))
    print("="*60)
    print(t('server_version', version='2.2.0'))
    print(t('server_features', features='Heartbeat + Error isolation + Interrupt + Status tracking + SSE streaming'))
    print(t('server_optimization', optimization='Long-task stability + Non-blocking heartbeat + 600s timeout'))
    print("="*60 + "\n")

    heartbeat = threading.Thread(target=heartbeat_thread, daemon=True)
    heartbeat.start()

    try:
        app.run(port=5000, host='0.0.0.0', threaded=True)
    except Exception as e:
        print(t('server_start_failed', error=str(e)))
        raise
