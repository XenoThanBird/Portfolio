"""
MCP Server Template
--------------------
A clean Model Context Protocol server scaffold with tool registration,
structured responses, and async handlers.

This template demonstrates the MCP server pattern. Replace the example
tool with your own domain-specific tools.

Usage:
    python -m mcp_server.server

Register in Claude Desktop via claude_desktop_config.json.
"""

import asyncio
import logging
from typing import Any, Sequence

from mcp.server import Server
from mcp.types import TextContent, Tool

from .config import settings
from .client import make_request

logger = logging.getLogger(__name__)

app = Server(settings.server_name)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """Register available MCP tools."""
    return [
        Tool(
            name="example_lookup",
            description=(
                "Example tool that fetches data from a public API. "
                "Replace this with your own domain-specific tool. "
                "Idempotent read-only operation."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query or lookup key",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results to return",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 20,
                    },
                    "dry_run": {
                        "type": "boolean",
                        "description": "Preview the request without executing",
                        "default": False,
                    },
                },
                "required": ["query"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Route tool invocations to handlers."""
    try:
        if name == "example_lookup":
            return await handle_example_lookup(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        logger.error("Tool %s failed: %s", name, e, exc_info=True)
        return [
            TextContent(
                type="text",
                text=f"Error executing {name}: {str(e)}",
            )
        ]


async def handle_example_lookup(args: dict[str, Any]) -> Sequence[TextContent]:
    """
    Example tool handler. Replace with your own logic.

    This example queries the JSONPlaceholder API as a demonstration.
    """
    query = args.get("query", "")
    limit = args.get("limit", 5)
    dry_run = args.get("dry_run", False)

    url = "https://jsonplaceholder.typicode.com/posts"
    params = {"_limit": limit}

    if dry_run:
        return [
            TextContent(
                type="text",
                text=f"DRY RUN: Would fetch from {url} with params {params}\nQuery: {query}",
            )
        ]

    data = await make_request(url, params=params)

    if not data:
        return [
            TextContent(type="text", text="No data returned from API.")
        ]

    # Filter results by query (simple substring match for demo)
    filtered = [
        item for item in data
        if query.lower() in item.get("title", "").lower()
        or query.lower() in item.get("body", "").lower()
    ]

    if not filtered:
        filtered = data[:limit]

    lines = [f"--- Results for '{query}' ({len(filtered)} items) ---\n"]
    for item in filtered:
        lines.append(f"Title: {item.get('title', 'N/A')}")
        lines.append(f"Body: {item.get('body', 'N/A')[:200]}")
        lines.append("")

    return [
        TextContent(type="text", text="\n".join(lines))
    ]


async def run_server():
    """Start the MCP server with stdio transport."""
    from mcp.server.stdio import stdio_server

    logger.info("Starting MCP server: %s", settings.server_name)
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def main():
    logging.basicConfig(level=getattr(logging, settings.log_level))
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
