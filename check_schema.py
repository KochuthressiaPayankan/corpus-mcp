import asyncio
import json

from mcp import Client

from corpus_mcp.server import mcp


async def main():
    async with Client(mcp) as client:
        result = await client.list_tools()
        tools = getattr(result, "tools", result)
        for tool in tools:
            schema = getattr(tool, "input_schema", None) or getattr(tool, "inputSchema", None)
            print("TOOL:", tool.name)
            print(json.dumps(schema, indent=2))
            print("-" * 40)


asyncio.run(main())
