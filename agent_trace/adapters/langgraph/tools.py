from langgraph.graph import StateGraph
from agent_trace.logging.logger import file_logger
from agent_trace.adapters.base.tools import ToolTrace

logger = file_logger("LANGGRAPH_TOOLS_ADAPTER")

class LangGraphToolTrace(ToolTrace):
    """Implementation of ToolTrace for LangGraph tools."""
    
    def get_tool_name(self, tool) -> str:
        """Get the name/identifier of the LangGraph tool."""
        return getattr(tool, '__name__', tool.__class__.__name__)

    def is_class_based_tool(self, tool) -> bool:
        """Determine if the tool is class-based (has __call__ method) or function-based."""
        return hasattr(tool, '__call__') and not callable(tool)

    def get_original_execute_method(self, tool):
        """Get the original execution method from the tool."""
        if self.is_class_based_tool(tool):
            return tool.__call__
        return tool

    def set_execute_method(self, tool, new_method):
        """Set the new execution method on the tool."""
        if self.is_class_based_tool(tool):
            tool.__call__ = new_method
            return tool
        else:
            # For function-based tools, we return the new method directly
            new_method.__name__ = self.get_tool_name(tool)
            return new_method

def patch_langgraph_tools():
    """Patch LangGraph StateGraph so all tools get traced automatically."""
    logger.info("Patching LangGraph tools")
    original_add_node = StateGraph.add_node
    tool_tracer = LangGraphToolTrace()

    def wrapped_add_node(self, node_name, node_func):
        logger.debug(f"Processing node: {node_name}")
        traced_node = tool_tracer.trace(node_func)
        return original_add_node(self, node_name, traced_node)

    StateGraph.add_node = wrapped_add_node
    logger.info("Successfully patched LangGraph StateGraph.add_node for tool tracing")
