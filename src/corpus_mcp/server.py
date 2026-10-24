import logging
import sys

from mcp.server.mcpserver import MCPServer

# IMPORTANT: log to stderr, never stdout (stdout is the MCP protocol channel)
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger("corpus-mcp")

mcp = MCPServer("corpus-mcp")


@mcp.tool()
def ping() -> str:
    """Check that the server is running. Returns 'pong'."""
    return "pong"


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
