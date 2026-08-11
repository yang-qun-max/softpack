"""
MCP Server for softpack — plug directly into Claude Code.

Usage:
    claude mcp add softpack -- uv run softpack mcp
    # or
    pip install softpack[mcp]
    softpack mcp
"""

import json
import sys


def serve():
    """
    Run softpack as an MCP server via stdio.

    Provides a single tool: `softpack_compress`
    Claude Code can call it when context approaches 70%.
    """
    try:
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.types import Tool, TextContent
    except ImportError:
        print(
            "MCP support requires: pip install softpack[mcp]",
            file=sys.stderr,
        )
        sys.exit(1)

    from softpack import compress, METHODS

    server = Server("softpack")

    @server.list_tools()
    async def list_tools():
        return [
            Tool(
                name="softpack_compress",
                description=(
                    "Gently compress conversation context before the LLM compaction "
                    "crushes it. Call this when context is around 70% full. "
                    "Preserves all technical entities (code, numbers, English terms) "
                    "while reducing Chinese prose by ~50%. "
                    "This is a lossy but entity-safe pre-compression — critical "
                    "keywords survive, filler words are dropped."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The context/memory/conversation text to compress.",
                        },
                        "method": {
                            "type": "string",
                            "enum": ["uniform", "hybrid_lock", "p0p1", "edge_preserve"],
                            "description": "Compression method. Default: hybrid_lock.",
                            "default": "hybrid_lock",
                        },
                        "ratio": {
                            "type": "number",
                            "description": "Target keep ratio (0.0 to 1.0). Default: 0.5.",
                            "default": 0.5,
                        },
                    },
                    "required": ["text"],
                },
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        if name != "softpack_compress":
            raise ValueError(f"Unknown tool: {name}")

        text = arguments.get("text", "")
        method = arguments.get("method", "hybrid_lock")
        ratio = arguments.get("ratio", 0.5)

        try:
            result = compress(text, method=method, ratio=ratio)
        except ValueError as e:
            return [TextContent(
                type="text",
                text=json.dumps({"error": str(e)}, ensure_ascii=False)
            )]

        original_chars = len(text)
        compressed_chars = len(result)
        saved = original_chars - compressed_chars
        saved_pct = (saved / original_chars * 100) if original_chars > 0 else 0

        return [TextContent(
            type="text",
            text=json.dumps({
                "compressed": result,
                "stats": {
                    "original_chars": original_chars,
                    "compressed_chars": compressed_chars,
                    "saved_chars": saved,
                    "saved_percent": round(saved_pct, 1),
                    "method": method,
                }
            }, ensure_ascii=False)
        )]

    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream)

    import asyncio
    asyncio.run(main())


if __name__ == "__main__":
    serve()
