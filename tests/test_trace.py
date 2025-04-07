"""Tests for the core tracing functionality."""
import time
from pathlib import Path

import pytest

from agent_trace import start_run, trace_tool
from agent_trace.store import get_traces_dir, list_traces


@trace_tool
def dummy_tool(arg: str) -> str:
    """A dummy tool for testing."""
    time.sleep(0.1)  # Add some duration
    return f"processed {arg}"


def test_trace_tool():
    """Test that the trace_tool decorator works."""
    result = dummy_tool("test")
    assert result == "processed test"


def test_start_run():
    """Test that start_run creates a trace with steps."""
    with start_run("test-run") as trace:
        dummy_tool("first")
        dummy_tool("second")
        
        assert len(trace.steps) == 2
        assert trace.steps[0].tool_name == "dummy_tool"
        assert trace.steps[0].inputs == {"arg": "first"}
        assert trace.steps[0].output == "processed first"
        assert trace.steps[0].duration_ms is not None


def test_trace_storage(tmp_path: Path, monkeypatch):
    """Test that traces are properly stored."""
    # Use a temporary directory for traces
    monkeypatch.setenv("AGENT_TRACE_DIR", str(tmp_path))
    
    with start_run("storage-test"):
        dummy_tool("test")
    
    traces = list_traces()
    assert len(traces) == 1
    assert traces[0].name == "storage-test"
    assert len(traces[0].steps) == 1 