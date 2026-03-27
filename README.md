# 🚀 ColabMCP CLI

A powerful command-line tool to run Jupyter Notebooks (`.ipynb`) with **streaming output per cell**. Built as a CLI version of [colabmcp](https://github.com/ctz168/colabmcp).

## ✨ Features

- 📓 **Run Jupyter Notebooks locally** - Execute `.ipynb` files directly from CLI
- 🌐 **Remote execution** - Run notebooks on ColabMCP servers (Google Colab / ModelScope)
- 📊 **Streaming output** - See each cell's output in real-time as it executes
- 🔧 **IPython magic support** - Handle `%` and `!` commands locally
- 🔄 **Variable persistence** - Variables persist between cells
- ⏱️ **Execution timing** - Track execution time for each cell
- 🛑 **Error handling** - Stop on error or continue execution
- 📝 **Notebook conversion** - Convert `.ipynb` to `.py` scripts
- 🔍 **Notebook inspection** - View notebook structure and metadata

## 📦 Installation

### From Source

```bash
cd colabmcp-cli
pip install -e .
```

### Dependencies

```bash
pip install requests rich click ipython
```

## 🚀 Quick Start

### Run a Notebook Locally

```bash
# Basic usage
colabmcp run notebook.ipynb

# With options
colabmcp run notebook.ipynb --start 5 --end 10 --verbose
```

### Run on Remote Server

```bash
# Execute on ColabMCP server
colabmcp remote notebook.ipynb --url https://your-server.modelscope.cn

# With timeout
colabmcp remote notebook.ipynb -u https://xxx.ngrok-free.app -t 600
```

### Other Commands

```bash
# View notebook info
colabmcp info notebook.ipynb

# List cells
colabmcp cells notebook.ipynb

# Convert to Python
colabmcp convert notebook.ipynb -o script.py

# Check server health
colabmcp health --url https://your-server.modelscope.cn

# Interactive REPL
colabmcp repl
```

## 📖 Commands Reference

### `colabmcp run`

Run a Jupyter Notebook locally with streaming output.

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

**Example:**
```bash
colabmcp run analysis.ipynb --start 2 --end 8 -o results.json
```

### `colabmcp remote`

Run a Jupyter Notebook on a remote ColabMCP server.

```bash
colabmcp remote NOTEBOOK --url URL [OPTIONS]

Options:
  -u, --url TEXT              ColabMCP server URL [required]
  -s, --start INTEGER         Start from cell index [default: 0]
  -e, --end INTEGER           End at cell index
  --show-code / --no-show-code  Show code before execution
  --stop-on-error / --continue-on-error  [default: stop-on-error]
  -t, --timeout INTEGER       Timeout in seconds [default: 300]
  -V, --verbose               Verbose output
```

**Example:**
```bash
colabmcp remote ml-training.ipynb -u https://colab-server.ngrok-free.app -t 600
```

### `colabmcp convert`

Convert a Jupyter Notebook to a Python script.

```bash
colabmcp convert NOTEBOOK [OPTIONS]

Options:
  -o, --output PATH           Output Python file
```

### `colabmcp info`

Show information about a Jupyter Notebook.

```bash
colabmcp info NOTEBOOK
```

### `colabmcp cells`

List and preview cells in a notebook.

```bash
colabmcp cells NOTEBOOK [OPTIONS]

Options:
  -s, --start INTEGER         Start from cell index [default: 0]
  -e, --end INTEGER           End at cell index
  -V, --verbose               Verbose output (show metadata)
```

### `colabmcp health`

Check health of a ColabMCP server.

```bash
colabmcp health --url URL
```

### `colabmcp repl`

Start an interactive Python REPL.

```bash
colabmcp repl
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
# Check server
colabmcp health --url https://your-colab.ngrok-free.app

# Run GPU-intensive notebook
colabmcp remote train_model.ipynb -u https://your-colab.ngrok-free.app -t 3600
```

### CI/CD Integration

```bash
# In your CI pipeline
colabmcp run tests.ipynb --continue-on-error -o test_results.json

# Check exit code
if [ $? -eq 0 ]; then
    echo "All tests passed!"
else
    echo "Some tests failed"
fi
```

## 🔧 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      ColabMCP CLI                           │
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

## 📝 Output Format

### Console Output

```
━━━ Cell [0] ━━━
┌──────────────────────────────────────┐
│ print("Hello, World!")               │
│ for i in range(3):                   │
│     print(f"Count: {i}")             │
└──────────────────────────────────────┘
⏳ Running...
Hello, World!
Count: 0
Count: 1
Count: 2
✅ Done (45ms)
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
      "stderr": "",
      "execution_time": 0.045,
      "variables": ["data"]
    }
  ]
}
```

## 🤝 Integration with ColabMCP Server

This CLI works seamlessly with the [ColabMCP server](https://github.com/ctz168/colabmcp):

1. **Deploy the server** on Google Colab or ModelScope
2. **Get the public URL** (ngrok or ModelScope URL)
3. **Run notebooks remotely** using `colabmcp remote`

## 🔒 Security Notes

- **Local execution**: Code runs with your user permissions
- **Remote execution**: Code runs on the remote server with full access
- **No authentication**: ColabMCP servers have no built-in auth - keep URLs private

## 📄 License

MIT License - See [LICENSE](LICENSE) file.

## 🙏 Credits

- Based on [colabmcp](https://github.com/ctz168/colabmcp)
- Built with [Click](https://click.palletsprojects.com/), [Rich](https://github.com/Textualize/rich), and [IPython](https://ipython.org/)
