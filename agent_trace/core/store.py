import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv

from .schema import Trace

from agent_trace.logging.logger import file_logger
logger = file_logger("TRACE_STORE")

# Load environment variables from .env file
load_dotenv()

def get_traces_dir() -> Path:
    """Get the directory where traces are stored."""
    # Read from .env, fallback to default if not set
    base_dir = os.getenv(
        "AGENT_TRACE_DIR",
        str(Path.home() / ".agent_trace")
    )
    traces_dir = Path(base_dir) / "traces"
    traces_dir.mkdir(parents=True, exist_ok=True)
    return traces_dir


def save_trace(trace: Trace) -> Path:
    """Save a trace to the local filesystem."""
    traces_dir = get_traces_dir()
    
    # Create filename with timestamp and trace name using local time
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{trace.name}_{trace.trace_id}.json"
    
    filepath = traces_dir / filename
    with open(filepath, "w") as f:
        json.dump(trace.model_dump(), f, default=str, indent=2)
    logger.info("-"*100)
    logger.info(f"Saved trace to {filepath}")
    logger.info("-"*100)
    return filepath


def load_trace(filepath: Path) -> Trace:
    """Load a trace from a file."""
    with open(filepath) as f:
        data = json.load(f)
    return Trace.model_validate(data)


def list_traces(
    limit: Optional[int] = None,
    name_filter: Optional[str] = None
) -> List[Trace]:
    """List traces, optionally filtered and limited."""
    traces_dir = get_traces_dir()
    
    files = sorted(
        traces_dir.glob("*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    traces = []
    for f in files:
        if limit and len(traces) >= limit:
            break
            
        trace = load_trace(f)
        if name_filter and name_filter not in trace.name:
            continue
            
        traces.append(trace)
        
    return traces 