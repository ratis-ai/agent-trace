from typing import TypedDict
from agent_trace.core.trace import start_run
from langgraph.graph import StateGraph
from agent_trace.adapters.langgraph.agents import patch_langgraph_node
from agent_trace.adapters.langgraph.tools import patch_langgraph_tools
from agent_trace.logging.logger import file_logger

logger = file_logger("LANGGRAPH_NODE_EXAMPLE")
# Patch LangGraph to trace nodes
patch_langgraph_node()
patch_langgraph_tools()
# Define the shared state schema
class AppState(TypedDict):
    topic: str
    research: str
    summary: str

# Define tools
def search_tool(input_text):
    return f"Search results for '{input_text}'"

def summarize_tool(input_text):
    return f"Summary of: {input_text}"

# Define agent nodes
def researcher(state: AppState) -> AppState:
    query = state.get("topic", "AI")
    results = search_tool(query)
    return {"research": results}

def writer(state: AppState) -> AppState:
    text_to_summarize = state.get("research", "")
    summary = summarize_tool(text_to_summarize)
    return {"summary": summary}

def run_graph():
# Create and configure LangGraph
    try: 
        with start_run("langgraph_node"):
            graph = StateGraph(AppState)

            graph.add_node("researcher", researcher)
            graph.add_node("writer", writer)

            graph.set_entry_point("researcher")
            graph.add_edge("researcher", "writer")

            # Compile and run the graph
            compiled = graph.compile()
            result = compiled.invoke({"topic": "LangGraph adapters"})

            print("Final result:", result)
    except Exception as e:
        logger.error(f"Error running graph: {e}")
        raise e

    finally:
        logger.info("Graph run complete")

if __name__ == "__main__":
    run_graph()