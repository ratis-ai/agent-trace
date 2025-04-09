from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

class BaseStep(BaseModel):
    """Base class for all step types."""
    started_at: datetime = Field(default_factory=lambda: datetime.now())
    duration_ms: Optional[float] = None
    agent_name: Optional[str] = None
    task_name: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ToolStep(BaseStep):
    """A single tool execution within a trace."""
    step_type: str = "tool"
    tool_name: str
    inputs: Dict[str, Any]
    output: Optional[Any] = None
    error: Optional[str] = None

class ReasoningStep(BaseStep):
    """A reasoning/thought step from the agent."""
    step_type: str = "reasoning"
    thought: str
    action: Optional[str] = None
    observation: Optional[str] = None

class TaskStep(BaseStep):
    """A task step from the agent."""
    step_type: str = "task"
    result: Optional[Any] = None

class AgentStep(BaseStep):
    """An agent step from the agent."""
    step_type: str = "agent"
    result: Optional[Any] = None

class Trace(BaseModel):
    """A complete trace of an agent run."""
    trace_id: UUID = Field(default_factory=uuid4)
    name: str
    started_at: datetime = Field(default_factory=lambda: datetime.now())
    steps: List[Union[ToolStep, ReasoningStep, AgentStep, TaskStep]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    ended_at: Optional[datetime] = None
    
    @property
    def duration_ms(self) -> Optional[float]:
        """Calculate total duration of the trace if ended."""
        if not self.ended_at:
            return None
        return (self.ended_at - self.started_at).total_seconds() * 1000 