"""
Crew management for coordinating research and writing tasks.
"""
import sys
from functools import wraps
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from agent_trace.core.trace import start_run
from agent_trace.logging.logger import file_logger
from agent_trace.adapters.crew.tools import patch_crewai_tools

logger = file_logger("CREW_EXAMPLE")
patch_crewai_tools()

# Force flush stdout
sys.stdout.reconfigure(line_buffering=True)  # Python 3.7+

logger.info('='*100)
logger.info("NEW RUN OF CREW EXAMPLE")  # Debug print
logger.info('='*100)

class WebSearchTool(BaseTool):
    name: str = "Web Search Tool"
    description: str = "Search the web using DuckDuckGo."

    def _run(self, query: str) -> str:
        print(f"WebSearchTool._run called with: {query}")  # Debug print
        result = f"Search results for: {query}\n\nMeta has released Llama 4."
        return result

class BlogPostTool(BaseTool):
    name: str = "Blog Post Tool"
    description: str = "Write a blog post based on research."

    def _run(self, research: str) -> str:
        print(f"BlogPostTool._run called with: {research}")  # Debug print
        result = f"Blog post based on: {research}"
        return result

# Create tools and verify their _run methods
search_tool = WebSearchTool()
blog_tool = BlogPostTool()

# Add debug logging to verify tools
logger.debug(f"search_tool is: {search_tool}")
logger.debug(f"blog_tool is: {blog_tool}")

# Define agents using CrewAI's format
researcher = Agent(
    role="AI Technology Researcher",
    goal="Research the latest AI developments",
    backstory="You are an experienced researcher with a keen eye for detail",
    tools=[search_tool],
    verbose=True  # Enable logging for debugging
)

writer = Agent(
    role="Content Creator",
    goal="Create engaging content based on research findings",
    backstory="You are a skilled writer who excels at clear communication",
    tools=[blog_tool],
    verbose=True
)

class ResearchCrew:
    def __init__(self):
        self.agents = {
            "researcher": researcher,
            "writer": writer
        }
        logger.debug(f"Crew initialized with agents: {list(self.agents.keys())}")
    
    def process_request(self, request: str) -> str:
        """Process a research and writing request."""
        try:
            logger.info(f"Processing request: {request}")
            
            # Create tasks
            research_task = Task(
                description="Research the latest developments in AI agents",
                agent=self.agents["researcher"],
                expected_output="A small headline on the latest AI developments"
            )
            
            writing_task = Task(
                description="Write a blog post about AI agents based on the research",
                agent=self.agents["writer"],
                expected_output="A small blog post about AI agents"
            )
            
            # Create crew
            crew = Crew(
                agents=list(self.agents.values()),
                tasks=[research_task, writing_task],
                verbose=True
            )
            
            # Run crew with core tracing
            with start_run("crew_ai_auto_wrap_tools"):
                result = crew.kickoff()
                return result
        
        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return error_msg


if __name__ == "__main__":
    crew = ResearchCrew()
    result = crew.process_request("Research and write about AI agents")
    print("Final Result:", result)