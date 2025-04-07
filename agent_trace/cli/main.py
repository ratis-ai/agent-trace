import json
from typing import Optional
from datetime import datetime

import click
from rich.console import Console
from rich.table import Table

from agent_trace.core.store import list_traces, load_trace

console = Console()


def format_duration(ms: Optional[float]) -> str:
    """Format duration in milliseconds to a human readable string."""
    if ms is None:
        return "..."
    if ms < 1000:
        return f"{ms:.0f}ms"
    return f"{ms/1000:.1f}s"


def parse_datetime(ctx, param, value):
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        raise click.BadParameter("Date must be in ISO format (e.g. 2025-04-07T00:00)")


def filter_traces_by_tool(traces, tool_name: Optional[str]) -> list:
    if not tool_name:
        return traces
    return [
        trace for trace in traces
        if any(step.tool_name == tool_name for step in trace.steps)
    ]


def format_step(step) -> tuple:
    """Format a step for display in the table."""
    if step.step_type == "tool":
        status = "❌" if step.error else "✅"
        duration = format_duration(step.duration_ms)
        
        inputs_str = ", ".join(
            f"{k}={repr(v)}" for k, v in step.inputs.items()
        )
        
        return (
            f"🔧 {step.tool_name}({inputs_str})",
            "→",
            f"{status} {duration}"
        )
    elif step.step_type == "reasoning":
        duration = format_duration(step.duration_ms)
        thought_line = f"💭 {step.thought}"
        
        if step.action:
            thought_line += f"\n   ⚡ Action: {step.action}"
        if step.observation:
            thought_line += f"\n   👁 Observed: {step.observation}"
            
        return (
            thought_line,
            "",
            f"🤔 {duration}"
        )


@click.group()
def cli():
    """Agent Trace CLI - View and analyze agent execution traces."""
    pass


@cli.command()
@click.option("--latest", is_flag=True, help="Show only the latest trace")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
@click.option("--name", help="Filter traces by name")
@click.option("--since", callback=parse_datetime, help="Show traces after this date (ISO format)")
@click.option("--until", callback=parse_datetime, help="Show traces before this date (ISO format)")
@click.option("--tool", help="Filter traces that used this tool")
@click.option("--limit", type=int, default=10, help="Maximum number of traces to show")
@click.argument("index", type=int, required=False)
def view(
    latest: bool,
    json_output: bool,
    name: Optional[str],
    since: Optional[datetime],
    until: Optional[datetime],
    tool: Optional[str],
    limit: int,
    index: Optional[int]
):
    """View agent traces. Optionally provide an index number to view a specific trace."""
    traces = list_traces(
        limit=1 if latest else limit,
        name_filter=name,
        since=since,
        until=until
    )
    
    if not traces:
        console.print("[yellow]No traces found[/yellow]")
        return

    # Apply tool filter if specified
    traces = filter_traces_by_tool(traces, tool)
    if not traces:
        console.print("[yellow]No traces found with the specified tool[/yellow]")
        return

    if index is not None:
        if index < 1 or index > len(traces):
            console.print(f"[red]Error: Index {index} is out of range. Available range: 1-{len(traces)}[/red]")
            return
        traces = [traces[index - 1]]
        
    if json_output:
        for trace in traces:
            click.echo(json.dumps(trace.model_dump(), indent=2, default=str))
        return
        
    for trace in traces:
        console.print(f"\n📋 [bold blue]Run:[/bold blue] {trace.name}")
        console.print(f"🕒 {trace.started_at.isoformat()}")
        console.print()
        
        table = Table(show_header=False)
        for step in trace.steps:
            left, middle, right = format_step(step)
            table.add_row(left, middle, right)
            
            if hasattr(step, 'error') and step.error:
                table.add_row("", "", f"[red]{step.error}[/red]")
                
        console.print(table)
        console.print()
        console.print(
            f"⏱ Total: {format_duration(trace.duration_ms)}"
        )


@cli.command()
@click.argument("trace_id")
def replay(trace_id: str):
    """Replay a specific trace (not implemented in MVP)."""
    console.print(
        "[yellow]Trace replay not implemented in MVP[/yellow]"
    )


@cli.command()
@click.option("--limit", type=int, default=10, help="Maximum number of traces to show")
@click.option("--name", help="Filter traces by name")
def list(limit: int, name: Optional[str]):
    """List available traces in a concise format."""
    traces = list_traces(limit=limit, name_filter=name)
    
    if not traces:
        console.print("[yellow]No traces found[/yellow]")
        return
        
    for i, trace in enumerate(traces, 1):
        status = "❌" if any(step.error for step in trace.steps) else "✅"
        date_str = trace.started_at.strftime("%Y-%m-%d %H:%M")
        duration = format_duration(trace.duration_ms)
        console.print(
            f"📋 {i}. {trace.name:<25} {date_str}   {status} {duration}"
        )


if __name__ == "__main__":
    cli() 