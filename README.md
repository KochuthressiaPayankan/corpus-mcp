# corpus-mcp

A local [Model Context Protocol](https://modelcontextprotocol.io) server that lets AI apps like Claude Desktop search and read a folder of documents, with a sandbox that keeps them inside that folder.

![demo](docs/demo.gif)

## Tools

| Tool | What it does |
|------|--------------|
| `search_documents` | BM25 keyword search, returns ranked `{path, score, snippet}` |
| `read_document` | Reads one file (truncated at 20,000 characters, flagged if so) |
| `list_documents` | Lists files with size and modified time, optional extension filter |
| `summarize_folder_stats` | File counts by type, total size, most recent files |

It also exposes a `docs://{+path}` resource and a `summarize_document` prompt.

## Setup

```bash
git clone [your repo URL]
cd corpus-mcp
uv sync
uv run pytest
```

Add this to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`), using absolute paths, then fully quit and reopen the app:

```json
{
  "mcpServers": {
    "corpus-mcp": {
      "command": "/absolute/path/to/uv",
      "args": ["--directory", "/absolute/path/to/corpus-mcp", "run", "corpus-mcp"],
      "env": { "DOCS_ROOT": "/absolute/path/to/your/docs" }
    }
  }
}
```

## Security model

The server only reads files, and every path goes through one function, `safe_resolve`:

- The path is resolved to its real location (collapsing `..` and following symlinks) and must sit inside `DOCS_ROOT`
- Only allowed extensions: `.md .txt .py .json .csv .rst`
- Files over 200 KB are refused, and output is truncated
- Result counts are capped at 50

Attempts like `../../etc/passwd`, absolute paths and symlinks pointing outside the folder are rejected, and the tests cover each case.

![traversal blocked](docs/traversal-blocked.png)

## Design decisions

- **Tool logic is plain functions**, and `server.py` only registers them, so everything is testable without a running server.
- **Expected failures raise `ToolError`.** In the v2 SDK any other exception is reduced to a generic message, so the model couldn't tell why a call failed. Now it sees "File not found... use list_documents" and can recover.
- **stdio transport only**, since it's local and needs no auth.
- **BM25 index rebuilds itself** when files change.
- Built on the `mcp` v2 Python SDK (`MCPServer`).

## Roadmap

- Swap BM25 for hybrid search backed by Qdrant
- Streamable HTTP transport with auth, deployed on AWS Lambda
- Write tools, behind explicit confirmation
