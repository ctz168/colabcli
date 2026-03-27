#!/usr/bin/env python3
"""
ColabMCP CLI - Command Line Interface

Run Jupyter Notebooks (.ipynb) with streaming output per cell.
"""

import json
import sys
import time
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.live import Live
from rich.layout import Layout

from .notebook import NotebookParser, Notebook, NotebookCell, CellType
from .executor import (
    LocalExecutionEngine,
    RemoteExecutionEngine,
    StreamingExecutor,
    CellOutput,
    ExecutionStatus,
    StreamChunk
)


console = Console()


def print_banner():
    """Print CLI banner"""
    banner = """
[bold cyan]╔═══════════════════════════════════════════════════════════════╗
║            🚀 ColabMCP CLI - Notebook Runner                   ║
║         Run .ipynb files with streaming output                 ║
╚═══════════════════════════════════════════════════════════════╝[/bold cyan]
"""
    console.print(banner)


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        mins, secs = divmod(seconds, 60)
        return f"{int(mins)}m {secs:.1f}s"


class StreamingRunner:
    """Run notebook with real-time streaming output display"""

    def __init__(
        self,
        engine,
        show_code: bool = True,
        show_markdown: bool = False,
        show_timing: bool = True,
        verbose: bool = False
    ):
        self.engine = engine
        self.show_code = show_code
        self.show_markdown = show_markdown
        self.show_timing = show_timing
        self.verbose = verbose
        self.results = []

        # Setup callbacks
        self.engine.on_cell_start = self._on_cell_start
        self.engine.on_cell_complete = self._on_cell_complete

    def _on_cell_start(self, cell: NotebookCell):
        """Handle cell start"""
        if cell.is_code:
            console.print(f"\n[bold blue]━━━ Cell [{cell.index}] ━━━[/bold blue]")
            if self.show_code:
                syntax = Syntax(cell.source, "python", theme="monokai", line_numbers=False)
                console.print(Panel(syntax, border_style="blue", padding=(0, 1)))
            console.print("[dim]⏳ Running...[/dim]")

    def _on_cell_complete(self, cell: NotebookCell, output: CellOutput):
        """Handle cell complete"""
        if output.status == ExecutionStatus.SUCCESS:
            # Show output
            if output.stdout:
                console.print(output.stdout, end='')
            if output.stderr:
                console.print(f"[yellow]{output.stderr}[/yellow]", end='')

            # Show timing
            if self.show_timing:
                console.print(f"[dim]✅ Done ({format_duration(output.execution_time)})[/dim]")

        elif output.status == ExecutionStatus.ERROR:
            console.print(f"\n[bold red]❌ Error in Cell [{cell.index}]:[/bold red]")
            if output.error:
                console.print(f"[red]{output.error_type}: {output.error}[/red]")
            if output.traceback and self.verbose:
                console.print(f"\n[dim]{output.traceback}[/dim]")
            if output.stdout:
                console.print(f"[dim]{output.stdout}[/dim]")

        elif output.status == ExecutionStatus.SKIPPED:
            if self.verbose:
                console.print(f"[dim]⏭️ Skipped[/dim]")

        self.results.append(output)

    def run(self, notebook: Notebook, stop_on_error: bool = True) -> list:
        """Run the notebook"""
        self.engine.stop_on_error = stop_on_error
        self.results = []

        for output in self.engine.execute_notebook(
            notebook,
            skip_markdown=not self.show_markdown
        ):
            pass  # Callbacks handle output

        return self.results


@click.group(invoke_without_command=True)
@click.option('--version', '-v', is_flag=True, help='Show version')
@click.pass_context
def main(ctx, version):
    """ColabMCP CLI - Run Jupyter Notebooks with streaming output"""
    if version:
        from . import __version__
        console.print(f"colabmcp-cli version {__version__}")
        return

    if ctx.invoked_subcommand is None:
        # Show help when no subcommand
        console.print(ctx.get_help())


@main.command()
@click.argument('notebook', type=click.Path(exists=True))
@click.option('--start', '-s', default=0, help='Start from cell index')
@click.option('--end', '-e', default=None, type=int, help='End at cell index')
@click.option('--show-code', is_flag=True, default=True, help='Show code before execution')
@click.option('--show-markdown', is_flag=True, help='Show markdown cells')
@click.option('--stop-on-error/--continue-on-error', default=True, help='Stop on error')
@click.option('--verbose', '-V', is_flag=True, help='Verbose output')
@click.option('--output', '-o', type=click.Path(), help='Save output to file')
def run(notebook, start, end, show_code, show_markdown, stop_on_error, verbose, output):
    """
    Run a Jupyter Notebook locally with streaming output.

    Example:
        colabmcp run notebook.ipynb
        colabmcp run notebook.ipynb --start 5 --end 10
        colabmcp run notebook.ipynb --show-markdown
    """
    print_banner()

    # Parse notebook
    notebook_path = Path(notebook)
    console.print(f"[cyan]📖 Loading notebook: {notebook_path.name}[/cyan]")

    try:
        nb = NotebookParser.parse_file(notebook_path)
    except Exception as e:
        console.print(f"[red]❌ Failed to load notebook: {e}[/red]")
        sys.exit(1)

    console.print(f"[green]✓ Found {len(nb.cells)} cells ({len(nb.code_cells)} code cells)[/green]")

    # Create engine and runner
    engine = LocalExecutionEngine()
    runner = StreamingRunner(
        engine,
        show_code=show_code,
        show_markdown=show_markdown,
        verbose=verbose
    )

    # Run notebook
    console.print(f"\n[bold cyan]🚀 Executing notebook...[/bold cyan]\n")

    start_time = time.time()
    results = runner.run(nb, stop_on_error=stop_on_error)
    total_time = time.time() - start_time

    # Summary
    console.print(f"\n[bold]{'─' * 50}[/bold]")
    console.print(f"\n[bold cyan]📊 Execution Summary:[/bold cyan]")

    success_count = sum(1 for r in results if r.status == ExecutionStatus.SUCCESS)
    error_count = sum(1 for r in results if r.status == ExecutionStatus.ERROR)
    skipped_count = sum(1 for r in results if r.status == ExecutionStatus.SKIPPED)

    table = Table(show_header=False, box=None)
    table.add_column("Key", style="cyan")
    table.add_column("Value")
    table.add_row("Total Time", format_duration(total_time))
    table.add_row("Cells Executed", str(len(results)))
    table.add_row("✅ Success", str(success_count))
    if error_count > 0:
        table.add_row("❌ Errors", f"[red]{error_count}[/red]")
    if skipped_count > 0:
        table.add_row("⏭️ Skipped", str(skipped_count))

    console.print(table)

    # Save output if requested
    if output:
        output_data = {
            "notebook": str(notebook_path),
            "total_time": total_time,
            "results": [r.to_dict() for r in results]
        }
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        console.print(f"\n[green]💾 Output saved to: {output}[/green]")

    # Exit with error code if there were errors
    if error_count > 0:
        sys.exit(1)


@main.command()
@click.argument('notebook', type=click.Path(exists=True))
@click.option('--url', '-u', required=True, help='ColabMCP server URL')
@click.option('--start', '-s', default=0, help='Start from cell index')
@click.option('--end', '-e', default=None, type=int, help='End at cell index')
@click.option('--show-code', is_flag=True, default=True, help='Show code before execution')
@click.option('--stop-on-error/--continue-on-error', default=True, help='Stop on error')
@click.option('--timeout', '-t', default=300, help='Timeout in seconds')
@click.option('--verbose', '-V', is_flag=True, help='Verbose output')
def remote(notebook, url, start, end, show_code, stop_on_error, timeout, verbose):
    """
    Run a Jupyter Notebook on a remote ColabMCP server.

    Example:
        colabmcp remote notebook.ipynb --url https://your-server.modelscope.cn
        colabmcp remote notebook.ipynb -u https://xxx.ngrok-free.app -t 600
    """
    print_banner()

    # Parse notebook
    notebook_path = Path(notebook)
    console.print(f"[cyan]📖 Loading notebook: {notebook_path.name}[/cyan]")

    try:
        nb = NotebookParser.parse_file(notebook_path)
    except Exception as e:
        console.print(f"[red]❌ Failed to load notebook: {e}[/red]")
        sys.exit(1)

    console.print(f"[green]✓ Found {len(nb.cells)} cells ({len(nb.code_cells)} code cells)[/green]")

    # Create remote engine
    console.print(f"\n[cyan]🔗 Connecting to: {url}[/cyan]")
    engine = RemoteExecutionEngine(url, timeout=timeout)

    # Health check
    health = engine.health_check()
    if "error" in health:
        console.print(f"[red]❌ Failed to connect: {health['error']}[/red]")
        sys.exit(1)

    console.print(f"[green]✓ Connected! Server uptime: {health.get('uptime_minutes', 'N/A')} min[/green]")

    # Create runner
    runner = StreamingRunner(
        engine,
        show_code=show_code,
        verbose=verbose
    )

    # Run notebook
    console.print(f"\n[bold cyan]🚀 Executing notebook remotely...[/bold cyan]\n")

    start_time = time.time()
    results = runner.run(nb, stop_on_error=stop_on_error)
    total_time = time.time() - start_time

    # Summary
    console.print(f"\n[bold]{'─' * 50}[/bold]")
    console.print(f"\n[bold cyan]📊 Execution Summary:[/bold cyan]")

    success_count = sum(1 for r in results if r.status == ExecutionStatus.SUCCESS)
    error_count = sum(1 for r in results if r.status == ExecutionStatus.ERROR)

    table = Table(show_header=False, box=None)
    table.add_column("Key", style="cyan")
    table.add_column("Value")
    table.add_row("Total Time", format_duration(total_time))
    table.add_row("Cells Executed", str(len(results)))
    table.add_row("✅ Success", str(success_count))
    if error_count > 0:
        table.add_row("❌ Errors", f"[red]{error_count}[/red]")

    console.print(table)

    if error_count > 0:
        sys.exit(1)


@main.command()
@click.argument('notebook', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output Python file')
def convert(notebook, output):
    """
    Convert a Jupyter Notebook to a Python script.

    Example:
        colabmcp convert notebook.ipynb -o script.py
    """
    print_banner()

    notebook_path = Path(notebook)
    console.print(f"[cyan]📖 Converting: {notebook_path.name}[/cyan]")

    try:
        nb = NotebookParser.parse_file(notebook_path)
    except Exception as e:
        console.print(f"[red]❌ Failed to load notebook: {e}[/red]")
        sys.exit(1)

    # Extract code
    code = NotebookParser.extract_code(nb, skip_markdown=False)

    # Determine output path
    if output:
        output_path = Path(output)
    else:
        output_path = notebook_path.with_suffix('.py')

    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(code)

    console.print(f"[green]✓ Converted to: {output_path}[/green]")


@main.command()
@click.argument('notebook', type=click.Path(exists=True))
def info(notebook):
    """
    Show information about a Jupyter Notebook.

    Example:
        colabmcp info notebook.ipynb
    """
    print_banner()

    notebook_path = Path(notebook)
    console.print(f"[cyan]📖 Analyzing: {notebook_path.name}[/cyan]\n")

    try:
        nb = NotebookParser.parse_file(notebook_path)
    except Exception as e:
        console.print(f"[red]❌ Failed to load notebook: {e}[/red]")
        sys.exit(1)

    # Notebook info table
    table = Table(title="Notebook Information", show_header=False)
    table.add_column("Key", style="cyan")
    table.add_column("Value")

    table.add_row("Path", str(nb.path))
    table.add_row("Format", f"nbformat {nb.nbformat}.{nb.nbformat_minor}")
    table.add_row("Total Cells", str(len(nb.cells)))
    table.add_row("Code Cells", str(len(nb.code_cells)))
    table.add_row("Markdown Cells", str(len(nb.markdown_cells)))

    # Kernel info
    kernel = nb.metadata.get('kernelspec', {})
    if kernel:
        table.add_row("Kernel", kernel.get('display_name', 'Unknown'))
        table.add_row("Language", kernel.get('language', 'Unknown'))

    console.print(table)

    # Cell list
    if nb.cells:
        console.print("\n[bold]Cell Overview:[/bold]\n")

        cell_table = Table(show_header=True, header_style="bold cyan")
        cell_table.add_column("#", justify="right", width=4)
        cell_table.add_column("Type", width=10)
        cell_table.add_column("Lines", justify="right", width=6)
        cell_table.add_column("Preview")

        for cell in nb.cells:
            preview = cell.source[:50].replace('\n', ' ')
            if len(cell.source) > 50:
                preview += "..."

            cell_table.add_row(
                str(cell.index),
                cell.cell_type.value,
                str(len(cell.get_source_lines())),
                preview
            )

        console.print(cell_table)

    # Tags
    tags = set()
    for cell in nb.code_cells:
        cell_tags = cell.metadata.get('tags', [])
        tags.update(cell_tags)

    if tags:
        console.print(f"\n[bold]Tags found:[/bold] {', '.join(sorted(tags))}")


@main.command()
@click.argument('notebook', type=click.Path(exists=True))
@click.option('--start', '-s', default=0, help='Start from cell index')
@click.option('--end', '-e', default=None, type=int, help='End at cell index')
@click.option('--verbose', '-V', is_flag=True, help='Verbose output')
def cells(notebook, start, end, verbose):
    """
    List and preview cells in a notebook.

    Example:
        colabmcp cells notebook.ipynb
        colabmcp cells notebook.ipynb --start 5 --end 10
    """
    print_banner()

    notebook_path = Path(notebook)
    console.print(f"[cyan]📖 Reading: {notebook_path.name}[/cyan]\n")

    try:
        nb = NotebookParser.parse_file(notebook_path)
    except Exception as e:
        console.print(f"[red]❌ Failed to load notebook: {e}[/red]")
        sys.exit(1)

    cells_to_show = nb.cells[start:end]

    for cell in cells_to_show:
        # Header
        cell_type_emoji = "📝" if cell.is_markdown else "🐍"
        console.print(f"\n[bold blue]{'─' * 50}[/bold blue]")
        console.print(f"[bold]{cell_type_emoji} Cell [{cell.index}] - {cell.cell_type.value}[/bold]")

        # Metadata
        if verbose and cell.metadata:
            console.print(f"[dim]Metadata: {cell.metadata}[/dim]")

        # Content
        if cell.is_code:
            syntax = Syntax(cell.source, "python", theme="monokai", line_numbers=True)
            console.print(syntax)
        elif cell.is_markdown:
            md = Markdown(cell.source)
            console.print(md)
        else:
            console.print(cell.source)

    console.print(f"\n[bold]{'─' * 50}[/bold]")
    console.print(f"\n[cyan]Total: {len(cells_to_show)} cells shown[/cyan]")


@main.command()
@click.option('--url', '-u', required=True, help='ColabMCP server URL')
def health(url):
    """
    Check health of a ColabMCP server.

    Example:
        colabmcp health --url https://your-server.modelscope.cn
    """
    print_banner()

    console.print(f"[cyan]🔍 Checking server: {url}[/cyan]\n")

    engine = RemoteExecutionEngine(url)
    result = engine.health_check()

    if "error" in result:
        console.print(f"[red]❌ Connection failed: {result['error']}[/red]")
        sys.exit(1)

    # Display health info
    table = Table(title="Server Health", show_header=False)
    table.add_column("Key", style="cyan")
    table.add_column("Value")

    table.add_row("Status", f"[green]{result.get('status', 'unknown')}[/green]")
    table.add_row("Uptime", f"{result.get('uptime_minutes', 'N/A')} minutes")
    table.add_row("Memory Available", f"{result.get('memory_available_gb', 'N/A')} GB")
    table.add_row("Memory Total", f"{result.get('memory_total_gb', 'N/A')} GB")
    table.add_row("Memory Used", f"{result.get('memory_used_pct', 'N/A')}%")
    table.add_row("GPU Available", "✅ Yes" if result.get('gpu_available') else "❌ No")

    console.print(table)

    # Probe environment
    console.print(f"\n[cyan]🔍 Probing environment...[/cyan]\n")

    probe = engine.probe_environment()
    if "error" not in probe:
        console.print(f"[dim]Python: {probe.get('python_version', 'N/A')[:60]}...[/dim]")
        console.print(f"[dim]Total packages: {probe.get('total_packages', 'N/A')}[/dim]")

        gpu_info = probe.get('gpu_info', '')
        if gpu_info and 'No GPU' not in gpu_info:
            console.print(f"\n[bold]🎮 GPU Info:[/bold]")
            for line in gpu_info.strip().split('\n')[:5]:
                console.print(f"  [dim]{line}[/dim]")


@main.command()
def repl():
    """
    Start an interactive REPL for executing Python code.

    Example:
        colabmcp repl
    """
    print_banner()

    console.print("[bold]Interactive Python REPL[/bold]")
    console.print("[dim]Type 'exit' or press Ctrl+D to exit[/dim]\n")

    engine = LocalExecutionEngine()

    while True:
        try:
            # Read multi-line input
            console.print("[bold cyan]>>>[/bold cyan] ", end='')
            lines = []
            while True:
                try:
                    line = input()
                    if not lines and not line:
                        break
                    lines.append(line)
                    if not line.endswith(':') and (not lines or lines[-1] == ''):
                        break
                    if lines and not line.startswith(' ') and lines[-1] and not lines[-1].endswith(':'):
                        break
                except EOFError:
                    if not lines:
                        raise
                    break

            code = '\n'.join(lines)

            if code.strip().lower() in ('exit', 'quit', 'q'):
                console.print("\n[green]👋 Goodbye![/green]")
                break

            if not code.strip():
                continue

            # Create a fake cell and execute
            from .notebook import NotebookCell
            cell = NotebookCell(
                index=0,
                cell_type=CellType.CODE,
                source=code
            )

            output = engine.execute_cell(cell)

            if output.stdout:
                console.print(output.stdout, end='')
            if output.stderr:
                console.print(f"[yellow]{output.stderr}[/yellow]", end='')
            if output.error:
                console.print(f"[red]{output.error_type}: {output.error}[/red]")

        except KeyboardInterrupt:
            console.print("\n[red]Interrupted[/red]")
            continue
        except EOFError:
            console.print("\n[green]👋 Goodbye![/green]")
            break


if __name__ == '__main__':
    main()
