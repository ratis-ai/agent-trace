# agent_trace/adapters/crew.py
from crewai import Agent
from agent_trace.logging.logger import file_logger
from agent_trace.adapters.base.agents import AgentTrace

logger = file_logger("CREW_AGENTS_ADAPTER")

class CrewAgentTrace(AgentTrace):
    """Implementation of TraceAgent for CrewAI agents."""
    
    def get_agent_name(self, agent_instance) -> str:
        """Get the name/identifier of the CrewAI agent instance."""
        return agent_instance.role
    
    def get_original_execute_method(self):
        """Get the original execute_task method from CrewAI Agent class."""
        return Agent.execute_task
    
    def set_execute_method(self, new_method):
        """Set the new execute_task method on the CrewAI Agent class."""
        Agent.execute_task = new_method

def patch_crewai_agents():
    """Legacy function for backward compatibility."""
    CrewAgentTrace().trace()