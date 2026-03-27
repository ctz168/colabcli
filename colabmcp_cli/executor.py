#!/usr/bin/env python3
"""
Execution Engine for Jupyter Notebooks

Supports both local and remote execution with streaming output.
"""

import io
import sys
import time
import traceback
import threading
import queue
import json
import re
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Generator, List, Optional, TextIO, Union

from .notebook import Notebook, NotebookCell, CellType


class ExecutionStatus(Enum):
    """Status of cell execution"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"


@dataclass
class CellOutput:
    """Output from a cell execution"""
    cell_index: int
    status: ExecutionStatus
    stdout: str = ""
    stderr: str = ""
    error: Optional[str] = None
    error_type: Optional[str] = None
    traceback: Optional[str] = None
    execution_time: float = 0.0
    outputs: List[Dict[str, Any]] = field(default_factory=list)
    variables: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cell_index": self.cell_index,
            "status": self.status.value,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "error": self.error,
            "error_type": self.error_type,
            "traceback": self.traceback,
            "execution_time": self.execution_time,
            "outputs": self.outputs,
            "variables": self.variables,
        }


@dataclass
class StreamChunk:
    """A chunk of streaming output"""
    cell_index: int
    stream_type: str  # 'stdout', 'stderr', 'status', 'error'
    content: str
    timestamp: float = field(default_factory=time.time)


class StreamingCapture:
    """Capture stdout/stderr and stream chunks"""

    def __init__(self, cell_index: int, output_queue: queue.Queue):
        self.cell_index = cell_index
        self.output_queue = output_queue
        self.buffer = io.StringIO()

    def write(self, text: str) -> int:
        if text:
            self.buffer.write(text)
            # Send streaming chunk
            self.output_queue.put(StreamChunk(
                cell_index=self.cell_index,
                stream_type='stdout',
                content=text
            ))
        return len(text)

    def flush(self):
        pass

    def getvalue(self) -> str:
        return self.buffer.getvalue()


class ExecutionEngine(ABC):
    """Abstract base class for execution engines"""

    def __init__(self):
        self.global_vars: Dict[str, Any] = {}
        self.output_queue: queue.Queue = queue.Queue()
        self.on_cell_start: Optional[Callable[[NotebookCell], None]] = None
        self.on_cell_complete: Optional[Callable[[NotebookCell, CellOutput], None]] = None
        self.on_stream: Optional[Callable[[StreamChunk], None]] = None
        self.stop_on_error: bool = True
        self.timeout: int = 300
        self._stop_requested = False

    @abstractmethod
    def execute_cell(self, cell: NotebookCell) -> CellOutput:
        """Execute a single cell"""
        pass

    def execute_notebook(
        self,
        notebook: Notebook,
        start_cell: int = 0,
        end_cell: Optional[int] = None,
        skip_markdown: bool = True,
        cell_filter: Optional[Callable[[NotebookCell], bool]] = None,
    ) -> Generator[CellOutput, None, None]:
        """
        Execute all cells in a notebook, yielding results as they complete.

        Args:
            notebook: The notebook to execute
            start_cell: Index of first cell to execute
            end_cell: Index of last cell (exclusive)
            skip_markdown: Skip markdown cells
            cell_filter: Optional filter function for cells
        """
        cells = notebook.cells[start_cell:end_cell]

        for cell in cells:
            if self._stop_requested:
                break

            # Skip markdown cells if requested
            if skip_markdown and cell.is_markdown:
                continue

            # Apply custom filter
            if cell_filter and not cell_filter(cell):
                continue

            # Callback for cell start
            if self.on_cell_start:
                self.on_cell_start(cell)

            # Execute cell
            output = self.execute_cell(cell)

            # Callback for cell complete
            if self.on_cell_complete:
                self.on_cell_complete(cell, output)

            yield output

            # Stop on error if configured
            if self.stop_on_error and output.status == ExecutionStatus.ERROR:
                break

    def stop(self):
        """Request execution to stop"""
        self._stop_requested = True

    def get_stream(self) -> Generator[StreamChunk, None, None]:
        """Get streaming output from queue"""
        while True:
            try:
                chunk = self.output_queue.get(timeout=0.1)
                yield chunk
            except queue.Empty:
                continue


class LocalExecutionEngine(ExecutionEngine):
    """
    Execute notebook cells locally with streaming output.

    Supports:
    - IPython magic commands
    - Variable persistence between cells
    - Streaming stdout/stderr
    """

    def __init__(self):
        super().__init__()
        self.global_vars = {'__builtins__': __builtins__}
        self._setup_ipython()

    def _setup_ipython(self):
        """Setup IPython shell for magic commands"""
        try:
            from IPython import get_ipython
            from IPython.core.interactiveshell import InteractiveShell

            # Get or create IPython instance
            self.shell = get_ipython()
            if self.shell is None:
                self.shell = InteractiveShell.instance()

            self.has_ipython = True
        except ImportError:
            self.shell = None
            self.has_ipython = False

    def execute_cell(self, cell: NotebookCell) -> CellOutput:
        """Execute a single cell locally"""
        if not cell.is_code:
            return CellOutput(
                cell_index=cell.index,
                status=ExecutionStatus.SKIPPED
            )

        if self._stop_requested:
            return CellOutput(
                cell_index=cell.index,
                status=ExecutionStatus.SKIPPED
            )

        start_time = time.time()
        stdout_capture = StreamingCapture(cell.index, self.output_queue)
        stderr_capture = StreamingCapture(cell.index, self.output_queue)

        # Redirect stdout/stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = stdout_capture
        sys.stderr = stderr_capture

        try:
            # Send status update
            self.output_queue.put(StreamChunk(
                cell_index=cell.index,
                stream_type='status',
                content='running'
            ))

            code = cell.source

            # Check for magic commands
            if cell.has_magic_commands() and self.has_ipython:
                # Use IPython to run cells with magic
                result = self.shell.run_cell(code)
                if not result.success:
                    raise result.error_in_exec if result.error_in_exec else Exception("Execution failed")
            else:
                # Regular Python execution
                exec_globals = {**self.global_vars}
                exec_locals = {}

                exec(code, exec_globals, exec_locals)

                # Save variables to global scope
                for key, value in exec_locals.items():
                    if not key.startswith('_'):
                        self.global_vars[key] = value

            # Build output
            output = CellOutput(
                cell_index=cell.index,
                status=ExecutionStatus.SUCCESS,
                stdout=stdout_capture.getvalue(),
                stderr=stderr_capture.getvalue(),
                execution_time=time.time() - start_time,
                variables=[k for k in self.global_vars.keys() if not k.startswith('_')]
            )

            self.output_queue.put(StreamChunk(
                cell_index=cell.index,
                stream_type='status',
                content='success'
            ))

            return output

        except Exception as e:
            error_output = CellOutput(
                cell_index=cell.index,
                status=ExecutionStatus.ERROR,
                stdout=stdout_capture.getvalue(),
                stderr=stderr_capture.getvalue(),
                error=str(e),
                error_type=type(e).__name__,
                traceback=traceback.format_exc(),
                execution_time=time.time() - start_time
            )

            self.output_queue.put(StreamChunk(
                cell_index=cell.index,
                stream_type='error',
                content=str(e)
            ))

            return error_output

        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    def get_variable(self, name: str) -> Any:
        """Get a variable from the global scope"""
        return self.global_vars.get(name)

    def set_variable(self, name: str, value: Any):
        """Set a variable in the global scope"""
        self.global_vars[name] = value


class RemoteExecutionEngine(ExecutionEngine):
    """
    Execute notebook cells on a remote ColabMCP server with streaming output.

    Uses Server-Sent Events (SSE) or polling for streaming output.
    """

    def __init__(self, base_url: str, timeout: int = 300):
        super().__init__()
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._setup_session()

    def _setup_session(self):
        """Setup HTTP session"""
        import requests
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'ColabMCP-CLI/1.0'
        })

    def health_check(self) -> Dict[str, Any]:
        """Check server health"""
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "status": "failed"}

    def execute_cell(self, cell: NotebookCell) -> CellOutput:
        """Execute a single cell on remote server"""
        if not cell.is_code:
            return CellOutput(
                cell_index=cell.index,
                status=ExecutionStatus.SKIPPED
            )

        if self._stop_requested:
            return CellOutput(
                cell_index=cell.index,
                status=ExecutionStatus.SKIPPED
            )

        start_time = time.time()

        # Send status update
        self.output_queue.put(StreamChunk(
            cell_index=cell.index,
            stream_type='status',
            content='running'
        ))

        try:
            # Prepare code - handle magic commands
            code = self._prepare_code(cell.source)

            # Execute on remote server
            response = self.session.post(
                f"{self.base_url}/execute",
                json={
                    "code": code,
                    "timeout": self.timeout
                },
                timeout=self.timeout + 30
            )
            response.raise_for_status()
            result = response.json()

            # Stream output in real-time (simulated for non-streaming server)
            if result.get("stdout"):
                self.output_queue.put(StreamChunk(
                    cell_index=cell.index,
                    stream_type='stdout',
                    content=result["stdout"]
                ))

            if result.get("stderr"):
                self.output_queue.put(StreamChunk(
                    cell_index=cell.index,
                    stream_type='stderr',
                    content=result["stderr"]
                ))

            # Build output
            if result.get("success"):
                output = CellOutput(
                    cell_index=cell.index,
                    status=ExecutionStatus.SUCCESS,
                    stdout=result.get("stdout", ""),
                    stderr=result.get("stderr", ""),
                    execution_time=result.get("execution_time_sec", time.time() - start_time),
                    variables=result.get("variables", [])
                )

                self.output_queue.put(StreamChunk(
                    cell_index=cell.index,
                    stream_type='status',
                    content='success'
                ))
            else:
                output = CellOutput(
                    cell_index=cell.index,
                    status=ExecutionStatus.ERROR,
                    stdout=result.get("stdout", ""),
                    stderr=result.get("stderr", ""),
                    error=result.get("error"),
                    error_type=result.get("error_type"),
                    traceback=result.get("traceback"),
                    execution_time=result.get("execution_time_sec", time.time() - start_time)
                )

                self.output_queue.put(StreamChunk(
                    cell_index=cell.index,
                    stream_type='error',
                    content=result.get("error", "Unknown error")
                ))

            return output

        except Exception as e:
            error_output = CellOutput(
                cell_index=cell.index,
                status=ExecutionStatus.ERROR,
                error=str(e),
                error_type=type(e).__name__,
                traceback=traceback.format_exc(),
                execution_time=time.time() - start_time
            )

            self.output_queue.put(StreamChunk(
                cell_index=cell.index,
                stream_type='error',
                content=str(e)
            ))

            return error_output

    def _prepare_code(self, code: str) -> str:
        """
        Prepare code for remote execution.

        Convert magic commands to regular Python where possible.
        """
        lines = code.split('\n')
        prepared_lines = []

        for line in lines:
            stripped = line.strip()

            # Handle pip install
            if stripped.startswith('!pip install') or stripped.startswith('%pip install'):
                # Convert to subprocess
                packages = stripped.replace('!pip install', '').replace('%pip install', '').strip()
                prepared_lines.append(f"import subprocess; subprocess.run(['pip', 'install'] + '{packages}'.split(), check=True)")
            # Handle shell commands
            elif stripped.startswith('!'):
                cmd = stripped[1:].strip()
                prepared_lines.append(f"import subprocess; subprocess.run({repr(cmd)}, shell=True)")
            # Handle line magics - skip for now
            elif stripped.startswith('%'):
                if stripped.startswith('%%'):
                    # Cell magic - keep as comment
                    prepared_lines.append(f"# [Cell magic skipped]: {stripped}")
                else:
                    # Line magic - skip
                    prepared_lines.append(f"# [Magic skipped]: {stripped}")
            else:
                prepared_lines.append(line)

        return '\n'.join(prepared_lines)

    def probe_environment(self) -> Dict[str, Any]:
        """Probe remote environment"""
        try:
            response = self.session.get(
                f"{self.base_url}/probe",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def list_variables(self) -> Dict[str, Any]:
        """List variables on remote server"""
        try:
            response = self.session.get(
                f"{self.base_url}/variables",
                timeout=15
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def cleanup(self) -> Dict[str, Any]:
        """Cleanup remote memory"""
        try:
            response = self.session.post(
                f"{self.base_url}/cleanup",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}


class StreamingExecutor:
    """
    High-level streaming executor that handles output display.

    Combines execution engine with output formatting.
    """

    def __init__(
        self,
        engine: ExecutionEngine,
        show_markdown: bool = False,
        show_timing: bool = True,
        color_output: bool = True
    ):
        self.engine = engine
        self.show_markdown = show_markdown
        self.show_timing = show_timing
        self.color_output = color_output

        # Setup callbacks
        self.engine.on_cell_start = self._on_cell_start
        self.engine.on_cell_complete = self._on_cell_complete
        self.engine.on_stream = self._on_stream

    def _on_cell_start(self, cell: NotebookCell):
        """Handle cell start event"""
        pass  # Will be overridden by CLI

    def _on_cell_complete(self, cell: NotebookCell, output: CellOutput):
        """Handle cell complete event"""
        pass  # Will be overridden by CLI

    def _on_stream(self, chunk: StreamChunk):
        """Handle streaming output"""
        pass  # Will be overridden by CLI

    def run(
        self,
        notebook: Notebook,
        start_cell: int = 0,
        end_cell: Optional[int] = None,
        stop_on_error: bool = True
    ) -> List[CellOutput]:
        """Run notebook and collect all outputs"""
        self.engine.stop_on_error = stop_on_error
        results = []

        for output in self.engine.execute_notebook(
            notebook,
            start_cell=start_cell,
            end_cell=end_cell,
            skip_markdown=not self.show_markdown
        ):
            results.append(output)

        return results
