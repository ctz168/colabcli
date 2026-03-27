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

## 📖 Commands Reference

| Command | Description |
|---------|-------------|
| `colabmcp run` | Run notebook locally with streaming output |
| `colabmcp remote` | Run notebook on remote ColabMCP server (batch mode) |
| `colabmcp stream` | 🆕 Run notebook with REAL-TIME SSE streaming output |
| `colabmcp watch` | 🆕 Monitor server status in real-time |
| `colabmcp health` | Check remote server health and environment |
| `colabmcp status` | Get current execution status and directory |
| `colabmcp interrupt` | Interrupt current execution (keeps server running) |
| `colabmcp history` | View command execution history |
| `colabmcp info` | Show notebook information |
| `colabmcp cells` | List and preview cells |
| `colabmcp convert` | Convert notebook to Python script |
| `colabmcp repl` | Start interactive Python REPL |

### `colabmcp run`

```bash
colabmcp run NOTEBOOK [OPTIONS]

Options:
  -s, --start INTEGER         Start from cell index [default: 0]
  -e, --end INTEGER           End at cell index
  --show-code / --no-show-code  Show code before execution [default: True]
  --show-markdown             Show markdown cells
  --stop-on-error / --continue-on-error  [default: stop-on-error]
  -V, --verbose               Verbose output
  -o, --output PATH           Save output to JSON file
```

### `colabmcp remote`

```bash
colabmcp remote NOTEBOOK --url URL [OPTIONS]

Options:
  -u, --url TEXT              ColabMCP server URL [required]
  -s, --start INTEGER         Start from cell index [default: 0]
  -e, --end INTEGER           End at cell index
  --stop-on-error / --continue-on-error  [default: stop-on-error]
  -t, --timeout INTEGER       Timeout in seconds [default: 300]
  -V, --verbose               Verbose output
```

### `colabmcp stream` 🆕

```bash
colabmcp stream NOTEBOOK --url URL [OPTIONS]

Options:
  -u, --url TEXT              ColabMCP server URL [required]
  -s, --start INTEGER         Start from cell index [default: 0]
  -e, --end INTEGER           End at cell index (exclusive)
  -t, --timeout INTEGER       Timeout in seconds [default: 600]
  -V, --verbose               Verbose output (show code)

# Stream bot execution
colabmcp stream bot.ipynb -u https://your-server.ngrok-free.app

# Stream specific cell with verbose output
colabmcp stream train.ipynb -u https://your-server.ngrok-free.app --start 5 --end 6 -V
```

### `colabmcp watch` 🆕

```bash
colabmcp watch --url URL [OPTIONS]

Options:
  -d, --duration INTEGER      Duration to watch in seconds [default: 300]
                             Use 0 for infinite watching

# Watch server for 5 minutes
colabmcp watch -u https://your-server.ngrok-free.app

# Watch indefinitely
colabmcp watch -u https://your-server.ngrok-free.app -d 0
```

### `colabmcp interrupt`

```bash
colabmcp interrupt --url URL

# Interrupt the current execution without stopping the server
colabmcp interrupt -u https://your-server.ngrok-free.app
```

### `colabmcp status`

```bash
colabmcp status --url URL

# Get current directory, execution status, and recent commands
colabmcp status -u https://your-server.ngrok-free.app
```

### `colabmcp history`

```bash
colabmcp history --url URL [OPTIONS]

Options:
  -l, --limit INTEGER         Number of entries to show [default: 20]

# View command execution history
colabmcp history -u https://your-server.ngrok-free.app
colabmcp history -u https://your-server.ngrok-free.app --limit 50
```

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
