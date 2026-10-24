import logging
import sys
from functools import wraps

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from corpus_mcp.security import SecurityError
from corpus_mcp.tools import files, search, stats

# IMPORTANT: log to stderr, never stdout (stdout is the MCP protocol channel)
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger("corpus-mcp")

mcp = MCPServer("corpus-mcp")


def friendly_errors(fn):
    """Turn expected failures into ToolError so the model sees the message.

    Anything else is still treated as a crash (generic message to the model,
    full traceback in the server log).
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except (SecurityError, FileNotFoundError, ValueError) as exc:
            logger.warning("%s rejected: %s", fn.__name__, exc)
            raise ToolError(str(exc)) from exc

    return wrapper


@mcp.tool()
def ping() -> str:
    """Check that the server is running. Returns 'pong'."""
    return "pong"


@mcp.tool()
@friendly_errors
def search_documents(query: str, limit: int = 5) -> list[dict]:
    """Search the document collection by keywords and return the best matches.

    Use this first when you need to find which documents mention a topic.
    Returns a ranked list of {path, score, snippet}. Pass a path to
    read_document to see the full text. Returns an empty list if nothing matches.

    Args:
        query: Keywords to look for, e.g. "lambda cold starts".
        limit: Maximum number of results (1-50, default 5).
    """
    logger.info("search_documents query=%r limit=%d", query, limit)
    return search.search_documents(query, limit)


@mcp.tool()
@friendly_errors
def read_document(path: str) -> dict:
    """Read the full text of one document.

    Use a path exactly as returned by list_documents or search_documents
    (relative to the documents folder, e.g. "subfolder/nested.md").
    Long files are truncated; check the 'truncated' field in the result.

    Args:
        path: Relative path of the document to read.
    """
    logger.info("read_document path=%r", path)
    return files.read_document(path)


@mcp.tool()
@friendly_errors
def list_documents(extension: str | None = None, limit: int = 50) -> list[dict]:
    """List the available documents with size and last-modified time.

    Use this to discover what exists before reading or searching.

    Args:
        extension: Optional file type filter such as "md" or ".txt".
        limit: Maximum number of files to return (1-50, default 50).
    """
    logger.info("list_documents extension=%r limit=%d", extension, limit)
    return files.list_documents(extension, limit)


@mcp.tool()
def summarize_folder_stats() -> dict:
    """Get an overview of the collection: file counts by type, total size,
    and the most recently modified files."""
    logger.info("summarize_folder_stats")
    return stats.folder_stats()


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
