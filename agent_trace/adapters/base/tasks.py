# agent_trace/adapters/base/tasks.py
import uuid
import datetime
from abc import ABC, abstractmethod
from functools import wraps
from agent_trace.logging.logger import file_logger
from agent_trace.core.trace import log_task_step, update_task_step

logger = file_logger("BASE_TASKS_ADAPTER")

class TaskTrace(ABC):
    """Abstract base class for tracing task execution."""
    
    @abstractmethod
    def get_agent_name(self, task_instance) -> str:
        """Get the name/identifier of the agent executing the task."""
        pass

    @abstractmethod
    def get_task_name(self, task_instance) -> str:
        """Get the name/description of the task."""
        pass

    @abstractmethod
    def get_original_execute_method(self):
        """Get the original execution method to be traced."""
        pass

    @abstractmethod
    def set_execute_method(self, new_method):
        """Set the new execution method on the task class."""
        pass

    def create_traced_execute(self, original_execute):
        """Create a traced version of the execute method."""
        @wraps(original_execute)
        def traced_execute(task_instance, *args, **kwargs):
            trace_id = str(uuid.uuid4())
            started_at = datetime.datetime.now().isoformat()
            agent_name = self.get_agent_name(task_instance)
            task_name = self.get_task_name(task_instance)
            
            logger.debug(f"[agent-trace] TASK_START: {agent_name} | task='{task_name}' | trace_id={trace_id} | started_at={started_at}")

            # Create the step at the beginning
            step = log_task_step(
                agent_name=agent_name,
                task_name=task_name,
                started_at=started_at
            )

            try:
                result = original_execute(task_instance, *args, **kwargs)
                logger.info(f"Logging task step with agent_name: {agent_name} and task_name: {task_name}")

                # Update the step with the result and duration
                if step:  # step might be None if no active trace
                    update_task_step(
                        step=step,
                        result=result if result else None,
                        duration_ms=(datetime.datetime.now() - datetime.datetime.fromisoformat(started_at)).total_seconds() * 1000
                    )

                logger.debug(f"[agent-trace] TASK_END: {agent_name} | result='{str(result)[:100]}...' | trace_id={trace_id}")
                return result
            except Exception as e:
                # Update the step with the error and duration
                if step:  # step might be None if no active trace
                    update_task_step(
                        step=step,
                        result=str(e),
                        duration_ms=(datetime.datetime.now() - datetime.datetime.fromisoformat(started_at)).total_seconds() * 1000
                    )
                logger.error(f"[agent-trace] TASK_ERROR: {agent_name} | error={str(e)} | trace_id={trace_id}")
                raise

        return traced_execute

    def trace(self):
        """
        This method orchestrates the tracing process using the abstract methods.
        """
        logger.info("Tracing Task execution")
        original_execute = self.get_original_execute_method()
        traced_execute = self.create_traced_execute(original_execute)
        self.set_execute_method(traced_execute) 