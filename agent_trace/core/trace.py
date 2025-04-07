import functools
import time
from contextlib import contextmanager
from typing import Any, Callable, Dict, Optional

from .schema import Trace, ToolStep, ReasoningStep, TaskStep, AgentStep
from .store import save_trace

from agent_trace.logging.logger import file_logger
logger = file_logger("TRACE")

_current_trace: Optional[Trace] = None

def trace(func: Callable, tool_name: Optional[str] = None) -> Callable:
    """Decorator to trace tool execution."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Use provided tool_name if available, otherwise use function name
        actual_name = tool_name or func.__name__
        logger.debug(f"Entering function: {actual_name}")
        
        if _current_trace is None:
            # No active trace, just execute the function
            result = func(*args, **kwargs)
            logger.debug(f"Exiting function: {actual_name}")
            return result

        # Track timing and execute
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            
            # Create tool step after we have the result
            step = ToolStep(
                tool_name=actual_name,
                inputs={
                    **{f"arg_{i}": arg for i, arg in enumerate(args)},
                    **kwargs
                },
                output=result,
                duration_ms=(time.time() - start_time) * 1000
            )
            _current_trace.steps.append(step)
            
            logger.debug(f"Exiting function: {actual_name}")
            return result
        except Exception as e:
            # Create error step
            step = ToolStep(
                tool_name=actual_name,
                inputs={
                    **{f"arg_{i}": arg for i, arg in enumerate(args)},
                    **kwargs
                },
                error=str(e),
                duration_ms=(time.time() - start_time) * 1000
            )
            _current_trace.steps.append(step)
            logger.error(f"Error in function: {actual_name}: {e}")
            raise
    
    # Set the name on the wrapper function
    wrapper.__name__ = tool_name or func.__name__
    return wrapper

def log_tool_step(
    tool_name: str,
    inputs: Dict[str, Any],
    output: Any,
    error: Optional[str] = None,
    duration_ms: float = 0,
    metadata: Optional[Dict[str, Any]] = None
) -> Optional[ToolStep]:
    """Log a tool step to the current trace. Returns the created step for later updates."""
    if _current_trace is None:
        logger.debug(f"No active trace, skipping tool step: {tool_name}")
        return None
    
    step = ToolStep(
        tool_name=tool_name,
        inputs=inputs,
        output=output,
        error=error,
        duration_ms=duration_ms,
        metadata=metadata or {},
    )
    _current_trace.steps.append(step)
    logger.debug(f"Created tool step: {tool_name}")
    return step

def update_tool_step(
    step: ToolStep,
    output: Optional[Any] = None,
    error: Optional[str] = None,
    duration_ms: Optional[float] = None,
) -> None:
    """Update an existing tool step with new values."""
    if duration_ms is not None:
        step.duration_ms = duration_ms
    if output is not None:
        step.output = output
    if error is not None:
        step.error = error
    logger.debug(f"Updated tool step: {step.tool_name}")

def log_react_step(
    agent_name: str,
    thought: str,
    action: Optional[str] = None,
    observation: Optional[str] = None,
    task_name: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """Log a reasoning step to the current trace."""
    if _current_trace is None:
        logger.debug(f"No active trace, skipping reasoning step: {thought}")
        return

    step = ReasoningStep(
        thought=thought,
        action=action,
        observation=observation,
        agent_name=agent_name,
        task_name=task_name,
        metadata=metadata or {}
    )
    _current_trace.steps.append(step)
    logger.debug(f"Added reasoning step: {thought}")

def log_task_step(
    agent_name: str,
    task_name: str,
    started_at: str,
    duration_ms: float = 0,
    result: Optional[Any] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Optional[TaskStep]:
    """Log a task step to the current trace. Returns the created step for later updates."""
    if _current_trace is None:
        logger.debug(f"No active trace, skipping task step: {task_name}")
        return None
    
    step = TaskStep(
        agent_name=agent_name,
        task_name=task_name,
        result=result,
        started_at=started_at,
        duration_ms=duration_ms,
        metadata=metadata or {},
    )
    _current_trace.steps.append(step)
    logger.debug(f"Created task step: {task_name}")
    return step

def update_task_step(
    step: TaskStep,
    result: Optional[Any] = None,
    duration_ms: Optional[float] = None,
) -> None:
    """Update an existing task step with new values."""
    if duration_ms is not None:
        step.duration_ms = duration_ms
    if result is not None:
        step.result = result
    logger.debug(f"Updated task step: {step.task_name}")

def log_agent_step(
    agent_name: str,
    started_at: str,
    duration_ms: float = 0,
    result: Optional[Any] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Optional[AgentStep]:
    """Log an agent step to the current trace. Returns the created step for later updates."""
    if _current_trace is None:
        logger.debug(f"No active trace, skipping agent step: {agent_name}")
        return None

    # Create the step at the beginning
    step = AgentStep(
        agent_name=agent_name,
        started_at=started_at,
        duration_ms=duration_ms,  # Initialize with provided value or 0
        result=result,  # Initialize with provided value or None
        metadata=metadata or {},
    )
    _current_trace.steps.append(step)
    logger.debug(f"Created agent step: {agent_name}")
    return step

def update_agent_step(
    step: AgentStep,
    result: Optional[Any] = None,
    duration_ms: Optional[float] = None,
) -> None:
    """Update an existing agent step with new values."""
    if duration_ms is not None:
        step.duration_ms = duration_ms
    if result is not None:
        step.result = result
    logger.debug(f"Updated agent step: {step.agent_name}")

@contextmanager
def start_run(name: str, metadata: Optional[dict] = None):
    """Context manager to start a new trace."""
    global _current_trace
    logger.info(f"Starting trace run: {name}")
    
    trace = Trace(name=name, metadata=metadata or {})
    previous_trace = _current_trace
    _current_trace = trace
    
    try:
        yield trace
    finally:
        from datetime import datetime
        trace.ended_at = datetime.now()
        _current_trace = previous_trace
        save_trace(trace)
        logger.info(f"Completed trace run: {name}")