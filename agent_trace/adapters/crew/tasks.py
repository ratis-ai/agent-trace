import uuid
import datetime
from functools import wraps
from crewai import Agent, Task, Crew
from agent_trace.logging.logger import file_logger
from agent_trace.core.trace import log_task_step
from agent_trace.adapters.base.tasks import TaskTrace

logger = file_logger("CREW_TASKS_ADAPTER")

class CrewTaskTrace(TaskTrace):
    """Implementation of TaskTrace for CrewAI tasks."""
    
    def get_agent_name(self, task_instance) -> str:
        """Get the name/identifier of the CrewAI agent executing the task."""
        return task_instance.agent.role
    
    def get_task_name(self, task_instance) -> str:
        """Get the description of the CrewAI task."""
        return task_instance.description

    def get_original_execute_method(self):
        """Get the original execute_sync method from CrewAI Task class."""
        return Task.execute_sync
    
    def set_execute_method(self, new_method):
        """Set the new execute_sync method on the CrewAI Task class."""
        Task.execute_sync = new_method

def patch_crewai_tasks():
    """Legacy function for backward compatibility."""
    CrewTaskTrace().trace()