import time
import datetime
import uuid
from functools import wraps
from agent_trace.core.trace import log_agent_step, update_agent_step
from agent_trace.logging.logger import file_logger

logger = file_logger("LANGGRAPH_NODE_ADAPTER")

def patch_langgraph_node():
    try:
        from langgraph.graph import StateGraph
    except ImportError:
        logger.error("LangGraph not installed. Please install langgraph to use this patch.")
        return

    original_add_node = StateGraph.add_node

    @wraps(original_add_node)
    def wrapped_add_node(self, node_name, node_func):
        logger.debug(f"Wrapping LangGraph node: {node_name}")

        @wraps(node_func)
        def wrapped_node_func(*args, **kwargs):
            trace_id = str(uuid.uuid4())
            started_at = datetime.datetime.now().isoformat()
            
            logger.debug(f"[agent-trace] NODE_START: {node_name} | trace_id={trace_id} | started_at={started_at}")

            # Create the step at the beginning
            step = log_agent_step(
                agent_name=node_name,
                started_at=started_at
            )

            try:
                result = node_func(*args, **kwargs)
                
                # Update the step with the result and duration
                if step:  # step might be None if no active trace
                    update_agent_step(
                        step=step,
                        result=result if result else None,
                        duration_ms=(datetime.datetime.now() - datetime.datetime.fromisoformat(started_at)).total_seconds() * 1000
                    )

                logger.debug(f"[agent-trace] NODE_END: {node_name} | result='{str(result)[:100]}...' | trace_id={trace_id}")
                return result
            except Exception as e:
                # Update the step with the error and duration
                if step:  # step might be None if no active trace
                    update_agent_step(
                        step=step,
                        result=str(e),
                        duration_ms=(datetime.datetime.now() - datetime.datetime.fromisoformat(started_at)).total_seconds() * 1000
                    )
                logger.error(f"[agent-trace] NODE_ERROR: {node_name} | error={str(e)} | trace_id={trace_id}")
                raise

        return original_add_node(self, node_name, wrapped_node_func)

    StateGraph.add_node = wrapped_add_node
    logger.info("LangGraph StateGraph.add_node has been patched for agent tracing.")
