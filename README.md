# 🚀 ColabCLI

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ctz168/colabcli/blob/main/colab_server.ipynb)
[![GitHub](https://img.shields.io/badge/GitHub-ctz168%2Fcolabcli-blue?logo=github)](https://github.com/ctz168/colabcli)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful command-line tool to run Jupyter Notebooks (`.ipynb`) with **streaming output per cell**.

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

# Run notebook remotely
colabmcp remote notebook.ipynb --url https://your-ngrok-url.ngrok-free.app
```

## ✨ Features

- 📓 **Run Jupyter Notebooks locally** - Execute `.ipynb` files directly from CLI
- 🌐 **Remote execution** - Run notebooks on Google Colab with GPU support
- 📊 **Streaming output** - See each cell's output in real-time as it executes
- 🔧 **IPython magic support** - Handle `%` and `!` commands locally
- 🔄 **Variable persistence** - Variables persist between cells
- ⏱️ **Execution timing** - Track execution time for each cell
- 🛑 **Error handling** - Stop on error or continue execution
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

# Execute notebook remotely
colabmcp remote notebook.ipynb --url https://your-ngrok-url.ngrok-free.app

# With timeout (for long-running tasks)
colabmcp remote train_model.ipynb -u https://your-server.ngrok-free.app -t 3600
```

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
| `colabmcp remote` | Run notebook on remote ColabMCP server |
| `colabmcp info` | Show notebook information |
| `colabmcp cells` | List and preview cells |
| `colabmcp convert` | Convert notebook to Python script |
| `colabmcp health` | Check remote server health |
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
│                      ColabCLI                               │
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
│                   │           (rich console)            │ │ │
│                   └─────────────────────────────────────┘ │ │
└─────────────────────────────────────────────────────────────┘
```

## 🤝 Integration with Google Colab

This CLI works seamlessly with Google Colab:

1. **Open the server notebook** in Colab using the badge above
2. **Set your ngrok token** ([get one free](https://dashboard.ngrok.com/get-started/your-authtoken))
3. **Run all cells** to start the server
4. **Copy the public URL** and use it with `colabmcp remote`

## 🔒 Security Notes

- **Local execution**: Code runs with your user permissions
- **Remote execution**: Code runs on the remote server with full access
- **No authentication**: ColabMCP servers have no built-in auth - keep URLs private

## 📄 License

MIT License - See [LICENSE](LICENSE) file.

## 🙏 Credits

- Original idea: [colabmcp](https://github.com/ctz168/colabmcp)
- Built with [Click](https://click.palletsprojects.com/), [Rich](https://github.com/Textualize/rich), and [IPython](https://ipython.org/)
