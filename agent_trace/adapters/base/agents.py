# agent_trace/adapters/base/agents.py
import uuid
import datetime
from abc import ABC, abstractmethod
from functools import wraps
from agent_trace.logging.logger import file_logger
from agent_trace.core.trace import log_agent_step, update_agent_step

logger = file_logger("BASE_AGENTS_ADAPTER")

class AgentTrace(ABC):
    """Abstract base class for patching agent execution with tracing capabilities."""
    
    @abstractmethod
    def get_agent_name(self, agent_instance) -> str:
        """Get the name/identifier of the agent instance."""
        pass

    @abstractmethod
    def get_original_execute_method(self):
        """Get the original execution method to be patched."""
        pass

    @abstractmethod
    def set_execute_method(self, new_method):
        """Set the new execution method on the agent class."""
        pass

    def create_traced_execute(self, original_execute):
        """Create a traced version of the execute method."""
        @wraps(original_execute)
        def traced_execute(agent_instance, *args, **kwargs):
            trace_id = str(uuid.uuid4())
            started_at = datetime.datetime.now().isoformat()
            agent_name = self.get_agent_name(agent_instance)
            
            logger.debug(f"[agent-trace] AGENT_START: {agent_name} | trace_id={trace_id} | started_at={started_at}")

            # Create the step at the beginning
            step = log_agent_step(
                agent_name=agent_name,
                started_at=started_at
            )

            try:
                result = original_execute(agent_instance, *args, **kwargs)
                logger.info(f"Logging agent step with agent_name: {agent_name}")

                # Update the step with the result and duration
                if step:  # step might be None if no active trace
                    update_agent_step(
                        step=step,
                        result=result if result else None,
                        duration_ms=(datetime.datetime.now() - datetime.datetime.fromisoformat(started_at)).total_seconds() * 1000
                    )

                logger.debug(f"[agent-trace] AGENT_END: {agent_name} | result='{str(result)[:100]}...' | trace_id={trace_id}")
                return result
            except Exception as e:
                # Update the step with the error and duration
                if step:  # step might be None if no active trace
                    update_agent_step(
                        step=step,
                        result=str(e),
                        duration_ms=(datetime.datetime.now() - datetime.datetime.fromisoformat(started_at)).total_seconds() * 1000
                    )
                logger.error(f"[agent-trace] AGENT_ERROR: {agent_name} | error={str(e)} | trace_id={trace_id}")
                raise

        return traced_execute

    def trace(self):
        """
        This method orchestrates the tracing process using the abstract methods.
        """
        logger.info("Tracing Agent execution")
        original_execute = self.get_original_execute_method()
        traced_execute = self.create_traced_execute(original_execute)
        self.set_execute_method(traced_execute)
        