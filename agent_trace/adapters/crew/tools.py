from crewai import Agent
from agent_trace.logging.logger import file_logger
from agent_trace.adapters.base.tools import ToolTrace

logger = file_logger("CREW_TOOLS_ADAPTER")

class CrewToolTrace(ToolTrace):
    """Implementation of ToolTrace for CrewAI tools."""
    
    def get_tool_name(self, tool) -> str:
        """Get the name/identifier of the CrewAI tool."""
        if self.is_class_based_tool(tool):
            return getattr(tool, 'name', tool.__class__.__name__)
        return getattr(tool, 'name', tool.__name__)

    def is_class_based_tool(self, tool) -> bool:
        """Determine if the tool is class-based (has _run method) or function-based."""
        return hasattr(tool, '_run')

    def get_original_execute_method(self, tool):
        """Get the original execution method from the tool."""
        if self.is_class_based_tool(tool):
            return tool._run
        return tool

    def set_execute_method(self, tool, new_method):
        """Set the new execution method on the tool."""
        if self.is_class_based_tool(tool):
            tool._run = new_method
            return tool
        else:
            # For function-based tools, we return the new method directly
            new_method.__name__ = self.get_tool_name(tool)
            return new_method

def patch_crewai_tools():
    """Patch CrewAI Agent so all tools get traced automatically."""
    logger.info("Patching CrewAI tools")
    original_init = Agent.__init__
    tool_tracer = CrewToolTrace()

    def wrapped_init(self, *args, tools=None, **kwargs):
        if tools:
            traced_tools = []
            for tool in tools:
                logger.debug(f"Processing tool: {tool}")
                traced_tool = tool_tracer.trace(tool)
                traced_tools.append(traced_tool)
            tools = traced_tools
            logger.debug(f"Final traced tools: {tools}")
        original_init(self, *args, tools=tools, **kwargs)

    Agent.__init__ = wrapped_init
    logger.info("Successfully patched CrewAI Agent initialization")