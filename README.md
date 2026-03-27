# 🚀 ColabCLI

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ctz168/colabcli/blob/main/colab_server.ipynb)
[![GitHub](https://img.shields.io/badge/GitHub-ctz168%2Fcolabcli-blue?logo=github)](https://github.com/ctz168/colabcli)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-2.1.0-green.svg)](https://github.com/ctz168/colabcli)

A powerful command-line tool to run Jupyter Notebooks (`.ipynb`) with **streaming output per cell** and **real-time SSE streaming** for long-running tasks.

## 🎯 Quick Start

### 1. Deploy Server on Google Colab

Click the badge below to open the server notebook in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ctz168/colabcli/blob/main/colab_server.ipynb)

Follow the instructions in the notebook to:
1. Set your ngrok token
2. Start the server
3. Get the public URL

### 2. Install CLI Locally

```bash
pip install git+https://github.com/ctz168/colabcli.git
```

### 3. Run Notebooks Remotely

```bash
# Check server health
colabmcp health --url https://your-ngrok-url.ngrok-free.app

# Run notebook remotely (batch mode)
colabmcp remote notebook.ipynb --url https://your-ngrok-url.ngrok-free.app

# Run notebook with REAL-TIME streaming output (NEW!)
colabmcp stream notebook.ipynb --url https://your-ngrok-url.ngrok-free.app
```

## ✨ Features

### Core Features
- 📓 **Run Jupyter Notebooks locally** - Execute `.ipynb` files directly from CLI
- 🌐 **Remote execution** - Run notebooks on Google Colab with GPU support
- 📊 **Streaming output** - See each cell's output in real-time as it executes
- 🔧 **IPython magic support** - Full support for `%cd`, `%env`, `!cmd`, `%%bash`, etc.
- 🔄 **Variable persistence** - Variables persist between cells
- ⏱️ **Execution timing** - Track execution time for each cell
- 🛑 **Error handling** - Stop on error or continue execution

### v2.1.0 New Features 🆕
- 🌊 **Real-time SSE Streaming** - Live output for long-running tasks (bots, training, etc.)
- 👀 **Watch Mode** - Monitor server status in real-time
- ⏹️ **Interrupt execution** - Stop long-running code without killing the server
- 📊 **Status tracking** - Know current directory, running status, command history
- 📜 **Command history** - View past executions and their results
- 🚫 **Duplicate detection** - Skip redundant `cd` commands automatically

### Other Features
- 📝 **Notebook conversion** - Convert `.ipynb` to `.py` scripts
- 🔍 **Notebook inspection** - View notebook structure and metadata

## 📦 Installation

### From GitHub

```bash
pip install git+https://github.com/ctz168/colabcli.git
```

### From Source

```bash
git clone https://github.com/ctz168/colabcli.git
cd colabcli
pip install -e .
```

### Dependencies

```bash
pip install requests rich click ipython
```

## 🚀 Usage

### Run a Notebook Locally

```bash
# Basic usage
colabmcp run notebook.ipynb

# With options
colabmcp run notebook.ipynb --start 5 --end 10 --verbose

# Save output to JSON
colabmcp run notebook.ipynb -o results.json
```

### Run on Remote Server (Google Colab)

```bash
# Check server status
colabmcp health --url https://your-ngrok-url.ngrok-free.app

# Execute notebook remotely (batch mode - waits for completion)
colabmcp remote notebook.ipynb --url https://your-ngrok-url.ngrok-free.app

# With timeout (for long-running tasks)
colabmcp remote train_model.ipynb -u https://your-server.ngrok-free.app -t 3600
```

### 🆕 Real-Time Streaming (v2.1.0)

Perfect for long-running tasks like training, bots, or continuous processes:

```bash
# Stream notebook output in REAL-TIME
colabmcp stream notebook.ipynb -u https://your-server.ngrok-free.app

# Stream specific cells only
colabmcp stream bot.ipynb -u https://your-server.ngrok-free.app --start 3 --end 4

# Watch server status in real-time
colabmcp watch -u https://your-server.ngrok-free.app -d 300
```

**When to use `stream` vs `remote`:**
- Use `remote` for short tasks (data processing, quick scripts)
- Use `stream` for long-running tasks (training, bots, servers)

### Other Commands

```bash
# View notebook info
colabmcp info notebook.ipynb

# List and preview cells
colabmcp cells notebook.ipynb

# Convert to Python script
colabmcp convert notebook.ipynb -o script.py

# Interactive REPL
colabmcp repl
```

---

## 📖 Commands Reference

### 命令概览

| 命令 | 描述 | 用途 |
|------|------|------|
| `colabmcp run` | 本地执行 notebook | 快速测试、本地开发 |
| `colabmcp remote` | 远程批量执行 | 短时间任务、数据处理 |
| `colabmcp stream` | 🆕 远程流式执行 | 长时间任务、Bot、训练 |
| `colabmcp watch` | 🆕 监控服务器状态 | 查看远程执行进度 |
| `colabmcp health` | 检查服务器健康状态 | 验证连接 |
| `colabmcp status` | 获取执行状态 | 查看当前目录和状态 |
| `colabmcp interrupt` | 中断当前执行 | 停止运行中的代码 |
| `colabmcp history` | 查看命令历史 | 调试、回溯 |
| `colabmcp info` | 查看 notebook 信息 | 了解 notebook 结构 |
| `colabmcp cells` | 列出 cell 内容 | 预览代码 |
| `colabmcp convert` | 转换为 Python 脚本 | 导出代码 |
| `colabmcp repl` | 交互式 Python REPL | 本地测试 |

---

### `colabmcp run` - 本地执行

在本地执行 Jupyter Notebook，支持实时输出。

```bash
colabmcp run NOTEBOOK [OPTIONS]
```

**参数说明：**

| 参数 | 简写 | 默认值 | 说明 |
|------|------|--------|------|
| `--start` | `-s` | 0 | 起始 cell 索引（从哪个 cell 开始执行） |
| `--end` | `-e` | 最后一个 | 结束 cell 索引（不包含该索引，类似 Python slice） |
| `--show-code` | - | True | 执行前显示代码 |
| `--show-markdown` | - | False | 显示 markdown cell |
| `--stop-on-error` | - | True | 遇到错误时停止 |
| `--continue-on-error` | - | False | 遇到错误时继续 |
| `--verbose` | `-V` | False | 详细输出 |
| `--output` | `-o` | - | 保存结果到 JSON 文件 |

**示例：**

```bash
# 执行整个 notebook
colabmcp run notebook.ipynb

# 只执行 cell 5 到 cell 9（不包含 cell 10）
colabmcp run notebook.ipynb --start 5 --end 10

# 执行从 cell 3 开始到结尾
colabmcp run notebook.ipynb -s 3

# 只执行 cell 0（第一个 cell）
colabmcp run notebook.ipynb --end 1

# 错误时继续执行
colabmcp run notebook.ipynb --continue-on-error

# 保存执行结果
colabmcp run notebook.ipynb -o results.json
```

---

### `colabmcp remote` - 远程批量执行

在远程服务器上执行 notebook，等待所有 cell 完成后返回结果。

```bash
colabmcp remote NOTEBOOK --url URL [OPTIONS]
```

**参数说明：**

| 参数 | 简写 | 默认值 | 必需 | 说明 |
|------|------|--------|------|------|
| `--url` | `-u` | - | ✅ | ColabMCP 服务器 URL |
| `--start` | `-s` | 0 | - | 起始 cell 索引 |
| `--end` | `-e` | 最后一个 | - | 结束 cell 索引（不包含） |
| `--stop-on-error` | - | True | - | 遇到错误时停止 |
| `--continue-on-error` | - | False | - | 遇到错误时继续 |
| `--timeout` | `-t` | 300 | - | 超时时间（秒） |
| `--verbose` | `-V` | False | - | 详细输出 |

**示例：**

```bash
# 基本远程执行
colabmcp remote notebook.ipynb -u https://xxx.ngrok-free.app

# 执行特定 cell（cell 3 到 cell 7）
colabmcp remote notebook.ipynb -u https://xxx.ngrok-free.app --start 3 --end 8

# 只执行第 4 个 cell（索引为 3）
colabmcp remote notebook.ipynb -u https://xxx.ngrok-free.app -s 3 -e 4

# 长时间任务（设置 1 小时超时）
colabmcp remote train.ipynb -u https://xxx.ngrok-free.app -t 3600

# 详细模式（显示每个 cell 的代码）
colabmcp remote notebook.ipynb -u https://xxx.ngrok-free.app -V
```

---

### `colabmcp stream` 🆕 - 远程流式执行

使用 SSE (Server-Sent Events) 实时推送输出，**适合长时间运行的任务**。

```bash
colabmcp stream NOTEBOOK --url URL [OPTIONS]
```

**参数说明：**

| 参数 | 简写 | 默认值 | 必需 | 说明 |
|------|------|--------|------|------|
| `--url` | `-u` | - | ✅ | ColabMCP 服务器 URL |
| `--start` | `-s` | 0 | - | 起始 cell 索引 |
| `--end` | `-e` | 最后一个 | - | 结束 cell 索引（不包含） |
| `--timeout` | `-t` | 600 | - | 流式超时时间（秒） |
| `--verbose` | `-V` | False | - | 显示代码 |

**使用场景：**
- 🤖 运行 Telegram/Discord Bot
- 🧠 模型训练（实时查看进度）
- 📊 数据处理（查看中间输出）
- 🔄 持续运行的监控脚本

**示例：**

```bash
# 流式执行整个 notebook
colabmcp stream bot.ipynb -u https://xxx.ngrok-free.app

# 只执行 Bot 启动的 cell（假设是 cell 4）
colabmcp stream bot.ipynb -u https://xxx.ngrok-free.app -s 4 -e 5

# 执行 cell 3 到 cell 5（跳过前面的安装和环境设置）
colabmcp stream bot.ipynb -u https://xxx.ngrok-free.app --start 3 --end 6

# 详细模式（显示代码和输出）
colabmcp stream bot.ipynb -u https://xxx.ngrok-free.app -V

# 长时间运行（设置 2 小时超时）
colabmcp stream bot.ipynb -u https://xxx.ngrok-free.app -t 7200
```

**中断执行：** 按 `Ctrl+C` 可中断执行，服务器保持运行。

---

### `colabmcp watch` 🆕 - 服务器监控

实时监控远程服务器的状态。

```bash
colabmcp watch --url URL [OPTIONS]
```

**参数说明：**

| 参数 | 简写 | 默认值 | 说明 |
|------|------|--------|------|
| `--url` | `-u` | - (必需) | ColabMCP 服务器 URL |
| `--duration` | `-d` | 300 | 监控时长（秒），设为 0 无限监控 |

**示例：**

```bash
# 监控 5 分钟
colabmcp watch -u https://xxx.ngrok-free.app

# 无限监控（按 Ctrl+C 退出）
colabmcp watch -u https://xxx.ngrok-free.app -d 0

# 监控 1 小时
colabmcp watch -u https://xxx.ngrok-free.app -d 3600
```

---

### `colabmcp interrupt` - 中断执行

中断远程服务器上正在执行的代码，**不会停止服务器本身**。

```bash
colabmcp interrupt --url URL
```

**参数说明：**

| 参数 | 简写 | 默认值 | 说明 |
|------|------|--------|------|
| `--url` | `-u` | - (必需) | ColabMCP 服务器 URL |

**使用场景：**
- Bot 运行时想要停止，但不想重新启动服务器
- 训练过程中发现参数错误，需要中断
- 死循环代码需要强制停止

**示例：**

```bash
# 中断当前执行
colabmcp interrupt -u https://xxx.ngrok-free.app

# 简写形式
colabmcp interrupt --url https://xxx.ngrok-free.app
```

**注意：** 中断后可以继续发送新的执行命令，服务器保持运行。

---

### `colabmcp status` - 获取执行状态

查看远程服务器的当前状态。

```bash
colabmcp status --url URL
```

**参数说明：**

| 参数 | 简写 | 默认值 | 说明 |
|------|------|--------|------|
| `--url` | `-u` | - (必需) | ColabMCP 服务器 URL |

**返回信息：**
- `is_executing` - 是否正在执行代码
- `current_directory` - 当前工作目录
- `last_command` - 最后执行的命令
- `last_execution_time` - 最后执行耗时
- `recent_history` - 最近 5 条命令

**示例：**

```bash
colabmcp status -u https://xxx.ngrok-free.app
```

---

### `colabmcp history` - 查看命令历史

查看远程服务器上的命令执行历史。

```bash
colabmcp history --url URL [OPTIONS]
```

**参数说明：**

| 参数 | 简写 | 默认值 | 说明 |
|------|------|--------|------|
| `--url` | `-u` | - (必需) | ColabMCP 服务器 URL |
| `--limit` | `-l` | 20 | 显示的历史条数 |

**示例：**

```bash
# 查看最近 20 条历史
colabmcp history -u https://xxx.ngrok-free.app

# 查看最近 50 条历史
colabmcp history -u https://xxx.ngrok-free.app -l 50
```

---

### `colabmcp health` - 健康检查

检查远程服务器的健康状态。

```bash
colabmcp health --url URL
```

**返回信息：**
- 服务器状态和运行时间
- 内存使用情况
- GPU 可用性
- 当前工作目录

**示例：**

```bash
colabmcp health -u https://xxx.ngrok-free.app
```

---

### `colabmcp cells` - 列出 Cell

列出 notebook 中的 cell 内容，用于预览代码。

```bash
colabmcp cells NOTEBOOK [OPTIONS]
```

**参数说明：**

| 参数 | 简写 | 默认值 | 说明 |
|------|------|--------|------|
| `--start` | `-s` | 0 | 起始 cell 索引 |
| `--end` | `-e` | 最后一个 | 结束 cell 索引（不包含） |
| `--verbose` | `-V` | False | 显示元数据 |

**示例：**

```bash
# 查看所有 cell
colabmcp cells notebook.ipynb

# 查看 cell 3 到 cell 7
colabmcp cells notebook.ipynb -s 3 -e 8

# 查看第一个 cell
colabmcp cells notebook.ipynb -e 1
```

---

### `colabmcp info` - Notebook 信息

显示 notebook 的基本信息。

```bash
colabmcp info NOTEBOOK
```

**返回信息：**
- 文件路径和格式版本
- 总 cell 数量（代码 cell 和 markdown cell）
- 内核信息
- Cell 概览表格

---

### `colabmcp convert` - 转换为 Python

将 notebook 转换为 Python 脚本。

```bash
colabmcp convert NOTEBOOK [OPTIONS]
```

**参数说明：**

| 参数 | 简写 | 默认值 | 说明 |
|------|------|--------|------|
| `--output` | `-o` | notebook同名.py | 输出文件路径 |

**示例：**

```bash
# 转换（输出到同名 .py 文件）
colabmcp convert notebook.ipynb

# 指定输出文件
colabmcp convert notebook.ipynb -o script.py
```

---

## 🔧 Cell 索引详解

### 索引规则

Cell 索引从 **0** 开始，`--end` 参数是**不包含**的（类似 Python 的 slice）。

```
Notebook 结构:
Cell 0: # 导入库        ← Markdown
Cell 1: import numpy    ← 代码
Cell 2: # 数据加载      ← Markdown  
Cell 3: load_data()     ← 代码
Cell 4: # 模型训练      ← Markdown
Cell 5: train_model()   ← 代码
```

### 执行范围示例

| 命令 | 执行的 Cell | 说明 |
|------|-------------|------|
| `-s 0 -e 6` 或省略 | 1, 3, 5 | 全部代码 cell（跳过 markdown） |
| `-s 3 -e 6` | 3, 5 | 从 cell 3 开始 |
| `-s 5 -e 6` | 5 | 只执行 cell 5 |
| `-s 1 -e 4` | 1, 3 | 执行 cell 1 和 3 |
| `-s 3` | 3, 5 | 从 cell 3 到结尾 |
| `-e 3` | 1 | 只执行第一个代码 cell |

### 常用场景

```bash
# 场景 1: 跳过安装和环境设置，直接运行核心逻辑
colabmcp stream bot.ipynb -u $URL --start 4

# 场景 2: 只运行某个特定 cell（假设是 cell 3）
colabmcp remote notebook.ipynb -u $URL -s 3 -e 4

# 场景 3: 调试某个范围的问题
colabmcp run notebook.ipynb --start 5 --end 8 -V

# 场景 4: 先预览再执行
colabmcp cells notebook.ipynb -s 4 -e 6
colabmcp stream notebook.ipynb -u $URL -s 4 -e 6
```

---

## 🔧 Supported IPython Magic Commands

| Magic Command | Example | Description |
|--------------|---------|-------------|
| `%cd` | `%cd /content/project` | Change directory |
| `%pwd` | `%pwd` | Print working directory |
| `%env` | `%env`, `%env VAR` | Show/get environment variables |
| `%set_env` | `%set_env VAR value` | Set environment variable |
| `%pip` | `%pip install package` | Install Python package |
| `!cmd` | `!git clone URL` | Execute shell command |
| `%%writefile` | `%%writefile file.py` | Write cell content to file |
| `%%bash` | `%%bash` | Run cell as bash script |
| `%time` | `%time func()` | Time execution |
| `%who` | `%who` | List variables |

## 📝 Output Example

### Console Output

```
━━━ Cell [0] ━━━
╭──────────────────────────────────────────────────────────────────────────────╮
│ print("Hello, World!")                                                       │
│ for i in range(3):                                                           │
│     print(f"Count: {i}")                                                     │
╰──────────────────────────────────────────────────────────────────────────────╯
⏳ Running...
Hello, World!
Count: 0
Count: 1
Count: 2
✅ Done (45ms)

━━━ Cell [1] ━━━
...
```

### Streaming Output (v2.1.0)

```
━━━ Cell [3] ━━━
⏳ Streaming...
📌 执行: python main.py --mode telegram
[Bot] Token: 7983263905:AAFs...
[Bot] 启动中...
按 Ctrl+C 停止 Bot
============================================================
[心跳] 14:32:15 - 服务运行中 | 目录: /content/stdpbrain
[Bot] 收到消息: 你好
[Bot] 回复: 你好！我是类人脑AI...
[心跳] 14:32:45 - 服务运行中 | 目录: /content/stdpbrain
...
⏹️ Execution interrupted by user

📊 Streaming Summary:
Total Time      5m 32.1s
Output Lines    127
```

### JSON Output (with `-o` option)

```json
{
  "notebook": "analysis.ipynb",
  "total_time": 2.345,
  "results": [
    {
      "cell_index": 0,
      "status": "success",
      "stdout": "Hello, World!\nCount: 0\nCount: 1\nCount: 2\n",
      "execution_time": 0.045,
      "variables": ["data"]
    }
  ]
}
```

## 🎯 Use Cases

### Data Analysis Pipeline

```bash
# Run data preprocessing
colabmcp run preprocess.ipynb

# Run analysis (skip first 3 cells)
colabmcp run analysis.ipynb --start 3

# Generate report
colabmcp run report.ipynb -o report_output.json
```

### Remote GPU Computation

```bash
# Deploy server on Colab (with GPU runtime)
# Then run locally:
colabmcp remote train_model.ipynb -u https://your-colab.ngrok-free.app -t 3600
```

### 🆕 Long-Running Bot/Server

```bash
# Stream bot output in real-time
colabmcp stream telegram_bot.ipynb -u https://your-colab.ngrok-free.app --start 3

# Watch server while bot runs
colabmcp watch -u https://your-colab.ngrok-free.app -d 0
```

### CI/CD Integration

```bash
# In your CI pipeline
colabmcp run tests.ipynb --continue-on-error -o test_results.json

# Check exit code
if [ $? -eq 0 ]; then
    echo "All tests passed!"
fi
```

## 🔧 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      ColabCLI v2.1.0                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────┐   │
│  │   CLI       │   │  Notebook   │   │   Execution     │   │
│  │   (click)   │──▶│   Parser    │──▶│   Engine        │   │
│  └─────────────┘   └─────────────┘   └─────────────────┘   │
│                                              │              │
│                          ┌──────────────────┼─────────────┐ │
│                          ▼                  ▼             │ │
│                   ┌───────────┐      ┌───────────┐       │ │
│                   │  Local    │      │  Remote   │       │ │
│                   │  Engine   │      │  Engine   │       │ │
│                   └───────────┘      └───────────┘       │ │
│                          │                  │             │ │
│                          ▼                  ▼             │ │
│                   ┌─────────────────────────────────────┐ │ │
│                   │      Streaming Output Display       │ │ │
│                   │    (rich console + SSE support)     │ │ │
│                   └─────────────────────────────────────┘ │ │
└─────────────────────────────────────────────────────────────┘
```

## 🤝 Integration with Google Colab

This CLI works seamlessly with Google Colab:

1. **Open the server notebook** in Colab using the badge above
2. **Set your ngrok token** ([get one free](https://dashboard.ngrok.com/get-started/your-authtoken))
3. **Run all cells** to start the server
4. **Copy the public URL** and use it with `colabmcp remote` or `colabmcp stream`

## 📋 Changelog

### v2.1.0 (Latest)
- 🆕 Added `/execute_stream` SSE endpoint for real-time output
- 🆕 Added `colabmcp stream` command for streaming execution
- 🆕 Added `colabmcp watch` command for server monitoring
- ✨ Improved interrupt handling for streaming tasks
- 🐛 Fixed shell command output streaming

### v2.0.0
- 🆕 Added `/interrupt` endpoint - stop code without killing server
- 🆕 Added `/status` endpoint - track current directory and execution state
- 🆕 Added `/history` endpoint - view command execution history
- ✨ Smart duplicate detection for `cd` commands

### v1.0.0
- Initial release
- Basic notebook execution (local and remote)
- IPython magic command support
- Streaming output per cell

## 🔒 Security Notes

- **Local execution**: Code runs with your user permissions
- **Remote execution**: Code runs on the remote server with full access
- **No authentication**: ColabMCP servers have no built-in auth - keep URLs private

## 📄 License

MIT License - See [LICENSE](LICENSE) file.

## 🙏 Credits

- Original idea: [colabmcp](https://github.com/ctz168/colabmcp)
- Built with [Click](https://click.palletsprojects.com/), [Rich](https://github.com/Textualize/rich), and [IPython](https://ipython.org/)
