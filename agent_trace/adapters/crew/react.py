import re
import json
from openai import OpenAI
import dotenv
import os
from crewai import Crew
import io
import contextlib
from agent_trace.core.trace import log_react_step
from agent_trace.adapters.crew.capture import get_stdout_for_crew

from agent_trace.logging.logger import file_logger, console_logger
logger = file_logger("REACT_PARSER")
# console_logger = console_logger("REACT_PARSER_OUT")

dotenv.load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_thought_action_blocks_llm(output: str):
    logger.info(f"Parsing agent names from agent logs: {len(output.split('\n'))} lines")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system", 
                "content": '''
                You are a helpful assistant that parses agent names and thoughts from agent logs. The agent logs are formatted as follows: # Agent: [agent name]\n## Thought: [thought]. Text might be wrapped in ANSI escape codes, so you need to strip them. 
                
                Extract the output as a JSON: 
                {
                    "matches": [
                        {{
                            "agent": string, 
                            "thought": string
                        }},
                        {{
                            "agent": string, 
                            "thought": string
                        }},
                        ...
                    ]
                }
                - In all cases, the output should have an array inside the "matches" key.
                - Even if there is only one match, put it inside the array. 
                - If there are no matches, return an empty array. 
                - If there is a match only for agent and not for thought, mark the thought as an empty string.
                '''
            },
            {"role": "user", "content": output}
        ],
        response_format={"type": "json_object"}
    )
    matches = json.loads(response.choices[0].message.content)["matches"]

    logger.info(f"Found {len(matches)} matches:")
    logger.info(matches)

    results = []
    for match in matches:
        results.append({
            "agent": match["agent"],
            "thought": match["thought"]
        })
    return results

def parse_thought_action_blocks_regex(output: str):
    logger.info(f"Parsing agent names from agent logs: {len(output.split('\n'))} lines")
    # logger.info("Agent logs:")
    # logger.info(output)
    
    # Pattern to match "# Agent:" with potential ANSI codes, followed by the name
    pattern = re.compile(r"\[.*?m# Agent:\[.*?m\s*(.*?)(?=\n|$)", re.DOTALL)
    matches = pattern.findall(output)

    logger.info(f"Found {len(matches)} matches")

    results = []
    for agent in matches:
        # Strip any remaining ANSI codes from the agent name
        clean_agent = re.sub(r'\x1b\[.*?m', '', agent.strip())
        results.append({
            "agent": clean_agent
        })
    return results

def patch_crewai_react():
    logger.info("Parsing captured ReAct logs for crew...")
    
    # We're iterating over every crew_id seen so far
    for crew_id in list(getattr(get_stdout_for_crew, '__globals__', {}).get('_stdout_buffer', {})):
        output = get_stdout_for_crew(crew_id)
        logger.info(f"Received output for crew_id: {crew_id} with {len(output.split('\n'))} lines")
        if not output:
            logger.warning(f"No output found for crew_id: {crew_id}")
            continue

        parsed = parse_thought_action_blocks_llm(output)
        logger.info(f"[{crew_id}] Found {len(parsed)} ReAct steps")

        for step in parsed:
            logger.info(f"Logging step: {step}")
            log_react_step(
                thought=step.get("thought", ""),
                action=step.get("tool", ""),
                observation=step.get("output", ""),
                agent_name=step.get("agent", ""),
                task_name=step.get("task", ""),
                metadata={"raw_input": step.get("input", "")}
            )