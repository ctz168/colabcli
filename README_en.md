# 🚀 ColabCLI

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ctz168/colabcli/blob/main/colab_server.ipynb)
[![GitHub](https://img.shields.io/badge/GitHub-ctz168%2Fcolabcli-blue?logo=github)](https://github.com/ctz168/colabcli)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-2.1.0-green.svg)](https://github.com/ctz168/colabcli)

A powerful command-line tool to run Jupyter Notebooks (`.ipynb`) with **streaming output per cell** and **real-time SSE streaming** for long-running tasks.

---

## 🎯 Quick Start

### 1. Deploy Server on Google Colab

Click the badge below to open the server notebook in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ctz168/colabcli/blob/main/colabcli.ipynb)

Follow the instructions in the notebook to:
1. Start the server (aitun tunnel auto-starts, no token needed)
2. Get the public URL

### 2. Install CLI Locally

```bash
pip install git+https://github.com/ctz168/colabcli.git
```

### 3. Run Notebooks Remotely

```bash
# Check server health
colabmcp health --url https://aitun.cc/your-code

# Run notebook remotely (batch mode)
colabmcp remote notebook.ipynb --url https://aitun.cc/your-code

# Run notebook with REAL-TIME streaming output (NEW!)
colabmcp stream notebook.ipynb --url https://aitun.cc/your-code
```

---

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

---

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

---

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
colabmcp health --url https://aitun.cc/your-code

# Execute notebook remotely (batch mode - waits for completion)
colabmcp remote notebook.ipynb --url https://aitun.cc/your-code

# With timeout (for long-running tasks)
colabmcp remote train_model.ipynb -u https://aitun.cc/your-code -t 3600
```

### 🆕 Real-Time Streaming (v2.1.0)

Perfect for long-running tasks like training, bots, or continuous processes:

```bash
# Stream notebook output in REAL-TIME
colabmcp stream notebook.ipynb -u https://aitun.cc/your-code

# Stream specific cells only
colabmcp stream bot.ipynb -u https://aitun.cc/your-code --start 3 --end 4

# Watch server status in real-time
colabmcp watch -u https://aitun.cc/your-code -d 300
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

### Command Overview

| Command | Description | Use Case |
|---------|-------------|----------|
| `colabmcp run` | Execute notebook locally | Quick testing, local development |
| `colabmcp remote` | Execute remotely in batch mode | Short tasks, data processing |
| `colabmcp stream` | 🆕 Remotely stream execution | Long-running tasks, Bots, training |
| `colabmcp watch` | 🆕 Monitor server status | View remote execution progress |
| `colabmcp health` | Check server health | Verify connection |
| `colabmcp status` | Get execution status | View current directory and status |
| `colabmcp interrupt` | Interrupt current execution | Stop running code |
| `colabmcp history` | View command history | Debugging, traceback |
| `colabmcp info` | View notebook info | Understand notebook structure |
| `colabmcp cells` | List cell contents | Preview code |
| `colabmcp convert` | Convert to Python script | Export code |
| `colabmcp repl` | Interactive Python REPL | Local testing |

---

### `colabmcp run` - Local Execution

Execute Jupyter Notebooks locally with real-time output.

```bash
colabmcp run NOTEBOOK [OPTIONS]
```

**Options:**

| Parameter | Short | Default | Description |
|-----------|-------|---------|-------------|
| `--start` | `-s` | 0 | Starting cell index (which cell to start from) |
| `--end` | `-e` | last | Ending cell index (exclusive, like Python slice) |
| `--show-code` | - | True | Show code before execution |
| `--show-markdown` | - | False | Show markdown cells |
| `--stop-on-error` | - | True | Stop on error |
| `--continue-on-error` | - | False | Continue on error |
| `--verbose` | `-V` | False | Verbose output |
| `--output` | `-o` | - | Save results to a JSON file |

**Examples:**

```bash
# Execute the entire notebook
colabmcp run notebook.ipynb

# Execute only cells 5 to 9 (excluding cell 10)
colabmcp run notebook.ipynb --start 5 --end 10

# Execute from cell 3 to the end
colabmcp run notebook.ipynb -s 3

# Execute only cell 0 (first cell)
colabmcp run notebook.ipynb --end 1

# Continue on error
colabmcp run notebook.ipynb --continue-on-error

# Save execution results
colabmcp run notebook.ipynb -o results.json
```

---

### `colabmcp remote` - Remote Batch Execution

Execute the notebook on a remote server, waiting for all cells to complete before returning results.

```bash
colabmcp remote NOTEBOOK --url URL [OPTIONS]
```

**Options:**

| Parameter | Short | Default | Required | Description |
|-----------|-------|---------|----------|-------------|
| `--url` | `-u` | - | ✅ | ColabMCP server URL |
| `--start` | `-s` | 0 | - | Starting cell index |
| `--end` | `-e` | last | - | Ending cell index (exclusive) |
| `--stop-on-error` | - | True | - | Stop on error |
| `--continue-on-error` | - | False | - | Continue on error |
| `--timeout` | `-t` | 300 | - | Timeout in seconds |
| `--verbose` | `-V` | False | - | Verbose output |

**Examples:**

```bash
# Basic remote execution
colabmcp remote notebook.ipynb -u https://aitun.cc/your-code

# Execute specific cells (cells 3 to 7)
colabmcp remote notebook.ipynb -u https://aitun.cc/your-code --start 3 --end 8

# Execute only cell 4 (index 3)
colabmcp remote notebook.ipynb -u https://aitun.cc/your-code -s 3 -e 4

# Long-running task (1 hour timeout)
colabmcp remote train.ipynb -u https://aitun.cc/your-code -t 3600

# Verbose mode (show code for each cell)
colabmcp remote notebook.ipynb -u https://aitun.cc/your-code -V
```

---

### `colabmcp stream` 🆕 - Remote Streaming Execution

Uses SSE (Server-Sent Events) to push output in real-time, **ideal for long-running tasks**.

```bash
colabmcp stream NOTEBOOK --url URL [OPTIONS]
```

**Options:**

| Parameter | Short | Default | Required | Description |
|-----------|-------|---------|----------|-------------|
| `--url` | `-u` | - | ✅ | ColabMCP server URL |
| `--start` | `-s` | 0 | - | Starting cell index |
| `--end` | `-e` | last | - | Ending cell index (exclusive) |
| `--timeout` | `-t` | 600 | - | Streaming timeout in seconds |
| `--verbose` | `-V` | False | - | Show code |

**Use Cases:**
- 🤖 Run a Telegram/Discord Bot
- 🧠 Model training (view progress in real-time)
- 📊 Data processing (view intermediate output)
- 🔄 Continuously running monitoring scripts

**Examples:**

```bash
# Stream the entire notebook
colabmcp stream bot.ipynb -u https://aitun.cc/your-code

# Only execute the Bot startup cell (e.g., cell 4)
colabmcp stream bot.ipynb -u https://aitun.cc/your-code -s 4 -e 5

# Execute cells 3 to 5 (skip previous install/env setup)
colabmcp stream bot.ipynb -u https://aitun.cc/your-code --start 3 --end 6

# Verbose mode (show code and output)
colabmcp stream bot.ipynb -u https://aitun.cc/your-code -V

# Long-running (2 hour timeout)
colabmcp stream bot.ipynb -u https://aitun.cc/your-code -t 7200
```

**Interrupting execution:** Press `Ctrl+C` to interrupt execution; the server keeps running.

---

### `colabmcp watch` 🆕 - Server Monitoring

Monitor the status of a remote server in real-time.

```bash
colabmcp watch --url URL [OPTIONS]
```

**Options:**

| Parameter | Short | Default | Description |
|-----------|-------|---------|-------------|
| `--url` | `-u` | - (required) | ColabMCP server URL |
| `--duration` | `-d` | 300 | Monitoring duration (seconds), set 0 for unlimited |

**Examples:**

```bash
# Monitor for 5 minutes
colabmcp watch -u https://aitun.cc/your-code

# Unlimited monitoring (exit with Ctrl+C)
colabmcp watch -u https://aitun.cc/your-code -d 0

# Monitor for 1 hour
colabmcp watch -u https://aitun.cc/your-code -d 3600
```

---

### `colabmcp interrupt` - Interrupt Execution

Interrupt code currently executing on the remote server, **without stopping the server itself**.

```bash
colabmcp interrupt --url URL
```

**Options:**

| Parameter | Short | Default | Description |
|-----------|-------|---------|-------------|
| `--url` | `-u` | - (required) | ColabMCP server URL |

**Use Cases:**
- Want to stop a running Bot without restarting the server
- Found a parameter error during training and need to interrupt
- A loop is stuck and needs to be force-stopped

**Examples:**

```bash
# Interrupt current execution
colabmcp interrupt -u https://aitun.cc/your-code

# Long form
colabmcp interrupt --url https://aitun.cc/your-code
```

**Note:** After interrupting, you can continue sending new execution commands; the server keeps running.

---

### `colabmcp status` - Get Execution Status

View the current status of the remote server.

```bash
colabmcp status --url URL
```

**Options:**

| Parameter | Short | Default | Description |
|-----------|-------|---------|-------------|
| `--url` | `-u` | - (required) | ColabMCP server URL |

**Returned Information:**
- `is_executing` - whether code is currently executing
- `current_directory` - the current working directory
- `last_command` - the last executed command
- `last_execution_time` - duration of the last execution
- `recent_history` - the last 5 commands

**Example:**

```bash
colabmcp status -u https://aitun.cc/your-code
```

---

### `colabmcp history` - View Command History

View the command execution history on the remote server.

```bash
colabmcp history --url URL [OPTIONS]
```

**Options:**

| Parameter | Short | Default | Description |
|-----------|-------|---------|-------------|
| `--url` | `-u` | - (required) | ColabMCP server URL |
| `--limit` | `-l` | 20 | Number of history entries to show |

**Examples:**

```bash
# View the last 20 history entries
colabmcp history -u https://aitun.cc/your-code

# View the last 50 history entries
colabmcp history -u https://aitun.cc/your-code -l 50
```

---

### `colabmcp health` - Health Check

Check the health status of the remote server.

```bash
colabmcp health --url URL
```

**Returned Information:**
- Server status and uptime
- Memory usage
- GPU availability
- Current working directory

**Example:**

```bash
colabmcp health -u https://aitun.cc/your-code
```

---

### `colabmcp cells` - List Cells

List the cell contents of a notebook, for previewing code.

```bash
colabmcp cells NOTEBOOK [OPTIONS]
```

**Options:**

| Parameter | Short | Default | Description |
|-----------|-------|---------|-------------|
| `--start` | `-s` | 0 | Starting cell index |
| `--end` | `-e` | last | Ending cell index (exclusive) |
| `--verbose` | `-V` | False | Show metadata |

**Examples:**

```bash
# View all cells
colabmcp cells notebook.ipynb

# View cells 3 to 7
colabmcp cells notebook.ipynb -s 3 -e 8

# View the first cell
colabmcp cells notebook.ipynb -e 1
```

---

### `colabmcp info` - Notebook Info

Display basic information about a notebook.

```bash
colabmcp info NOTEBOOK
```

**Returned Information:**
- File path and format version
- Total cell count (code cells and markdown cells)
- Kernel information
- Cell overview table

---

### `colabmcp convert` - Convert to Python

Convert a notebook to a Python script.

```bash
colabmcp convert NOTEBOOK [OPTIONS]
```

**Options:**

| Parameter | Short | Default | Description |
|-----------|-------|---------|-------------|
| `--output` | `-o` | notebook-name.py | Output file path |

**Examples:**

```bash
# Convert (output to same-name .py file)
colabmcp convert notebook.ipynb

# Specify output file
colabmcp convert notebook.ipynb -o script.py
```

---

## 🔧 Cell Index Details

### Index Rules

Cell indices start from **0**, and the `--end` parameter is **exclusive** (similar to Python slice).

```
Notebook structure:
Cell 0: # Import libraries  ← Markdown
Cell 1: import numpy        ← Code
Cell 2: # Data loading      ← Markdown
Cell 3: load_data()         ← Code
Cell 4: # Model training    ← Markdown
Cell 5: train_model()       ← Code
```

### Execution Range Examples

| Command | Executed Cells | Description |
|---------|----------------|-------------|
| `-s 0 -e 6` or omitted | 1, 3, 5 | All code cells (skip markdown) |
| `-s 3 -e 6` | 3, 5 | Start from cell 3 |
| `-s 5 -e 6` | 5 | Execute only cell 5 |
| `-s 1 -e 4` | 1, 3 | Execute cells 1 and 3 |
| `-s 3` | 3, 5 | From cell 3 to the end |
| `-e 3` | 1 | Execute only the first code cell |

### Common Scenarios

```bash
# Scenario 1: Skip install and environment setup, run core logic directly
colabmcp stream bot.ipynb -u $URL --start 4

# Scenario 2: Run only a specific cell (e.g., cell 3)
colabmcp remote notebook.ipynb -u $URL -s 3 -e 4

# Scenario 3: Debug a range of issues
colabmcp run notebook.ipynb --start 5 --end 8 -V

# Scenario 4: Preview first, then execute
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

---

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

---

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
colabmcp remote train_model.ipynb -u https://aitun.cc/your-code -t 3600
```

### 🆕 Long-Running Bot/Server

```bash
# Stream bot output in real-time
colabmcp stream telegram_bot.ipynb -u https://aitun.cc/your-code --start 3

# Watch server while bot runs
colabmcp watch -u https://aitun.cc/your-code -d 0
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

---

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
2. **Run all cells** - aitun tunnel starts automatically (no token needed)
3. **Copy the public URL** and use it with `colabmcp remote` or `colabmcp stream`

---

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

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file.

## 🙏 Credits

- Original idea: [colabmcp](https://github.com/ctz168/colabmcp)
- Built with [Click](https://click.palletsprojects.com/), [Rich](https://github.com/Textualize/rich), and [IPython](https://ipython.org/)