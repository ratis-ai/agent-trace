# Agent Trace 🕵️‍♂️

A universal agent trace logger and viewer for LLM agents. Capture every step of your agent's execution with beautiful, readable traces.

## Features

- 🎯 **Zero-config tracing**: Just add `@trace_tool` to your functions
- 📊 **Rich CLI viewer**: See your agent's execution timeline
- 💾 **Local-first storage**: All traces stored as JSON files
- 🔌 **Framework agnostic**: Works with any Python agent framework

## Quick Start

```bash
# Install
pip install agent-trace

# Run the example
python examples/summarize_and_email.py

# View the trace
agent-trace view --latest
```

## Usage

1. Decorate your tool functions:

```python
from agent_trace import trace_tool

@trace_tool
def my_tool(arg1: str) -> str:
    return "result"
```

2. Wrap your agent runs:

```python
from agent_trace import start_run

with start_run("my-agent-run"):
    result = my_tool("input")
```

3. View the traces:

```bash
# View latest trace
agent-trace view --latest

# View all traces
agent-trace view

# View as JSON
agent-trace view --json

# Filter by name
agent-trace view --name "my-agent"
```

## Example Output

```
📋 Run: summarize_pdf_and_email
🕒 2024-04-07T15:42:00

🔧 read_pdf(path='report.pdf') → ✅ 123ms
🔧 summarize_text(text=...) → ✅ 342ms
🔧 send_email(to='user@example.com') → ✅ 78ms

⏱ Total: 0.6s
```

## Configuration

- Set `AGENT_TRACE_DIR` environment variable to change trace storage location
- Default: `./trace_logs`

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT 