# 🚀 ColabCLI

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ctz168/colabcli/blob/main/colab_server.ipynb)
[![GitHub](https://img.shields.io/badge/GitHub-ctz168%2Fcolabcli-blue?logo=github)](https://github.com/ctz168/colabcli)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-2.1.0-green.svg)](https://github.com/ctz168/colabcli)

A powerful command-line tool to run Jupyter Notebooks with streaming output.

一个强大的命令行工具，用于运行 Jupyter Notebook，支持流式输出。

## 📖 Documentation

- **[English](README_en.md)** - Full documentation in English
- **[中文](README_zh.md)** - 完整中文文档

## 🎯 Quick Start

### English
1. Deploy server on Google Colab (open [colab_server.ipynb](colab_server.ipynb))
2. Install CLI: `pip install git+https://github.com/ctz168/colabcli.git`
3. Run: `colabmcp stream notebook.ipynb -u https://aitun.cc/your-code`

### 中文
1. 在 Google Colab 上部署服务器（打开 [colab_server.ipynb](colab_server.ipynb)）
2. 安装 CLI：`pip install git+https://github.com/ctz168/colabcli.git`
3. 运行：`colabmcp stream notebook.ipynb -u https://aitun.cc/your-code`

## 📄 License

MIT License - See [LICENSE](LICENSE) file.

## 🙏 Credits

- Original idea: [colabmcp](https://github.com/ctz168/colabmcp)
- Built with [Click](https://click.palletsprojects.com/), [Rich](https://github.com/Textualize/rich), and [IPython](https://ipython.org/)