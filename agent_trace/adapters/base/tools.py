import uuid
import datetime
from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Callable, Dict, Optional
from agent_trace.logging.logger import file_logger
from agent_trace.core.trace import log_tool_step, update_tool_step

logger = file_logger("BASE_TOOLS_ADAPTER")

class ToolTrace(ABC):
    """Abstract base class for tracing tool execution."""
    
    @abstractmethod
    def get_tool_name(self, tool) -> str:
        """Get the name/identifier of the tool."""
        pass

    @abstractmethod
    def is_class_based_tool(self, tool) -> bool:
        """Determine if the tool is class-based or function-based."""
        pass

    @abstractmethod
    def get_original_execute_method(self, tool) -> Callable:
        """Get the original execution method to be traced."""
        pass

    @abstractmethod
    def set_execute_method(self, tool, new_method: Callable) -> None:
        """Set the new execution method on the tool."""
        pass

    def create_traced_execute(self, tool, original_execute: Callable) -> Callable:
        """Create a traced version of the execute method."""
        tool_name = self.get_tool_name(tool)

        @wraps(original_execute)
        def traced_execute(*args, **kwargs):
            trace_id = str(uuid.uuid4())
            started_at = datetime.datetime.now().isoformat()
            
            logger.debug(f"[agent-trace] TOOL_START: {tool_name} | trace_id={trace_id} | started_at={started_at}")

            # Create the step at the beginning
            step = log_tool_step(
                tool_name=tool_name,
                inputs={
                    **{f"arg_{i}": arg for i, arg in enumerate(args)},
                    **kwargs
                },
                output=None,  # Will be updated after execution
                duration_ms=0  # Will be updated after execution
            )

            try:
                start_time = datetime.datetime.now()
                result = original_execute(*args, **kwargs)
                duration_ms = (datetime.datetime.now() - start_time).total_seconds() * 1000

                # Update the step with the result and duration
                if step:  # step might be None if no active trace
                    update_tool_step(
                        step=step,
                        output=result,
                        duration_ms=duration_ms
                    )

                logger.debug(f"[agent-trace] TOOL_END: {tool_name} | result='{str(result)[:100]}...' | trace_id={trace_id}")
                return result
            except Exception as e:
                # Update the step with the error and duration
                if step:  # step might be None if no active trace
                    update_tool_step(
                        step=step,
                        error=str(e),
                        duration_ms=(datetime.datetime.now() - start_time).total_seconds() * 1000
                    )
                logger.error(f"[agent-trace] TOOL_ERROR: {tool_name} | error={str(e)} | trace_id={trace_id}")
                raise

        return traced_execute

    def trace(self, tool: Any) -> Any:
        """
        Trace a single tool's execution.
        Returns the tool with its execution method traced.
        """
        original_execute = self.get_original_execute_method(tool)
        traced_execute = self.create_traced_execute(tool, original_execute)
        return self.set_execute_method(tool, traced_execute)