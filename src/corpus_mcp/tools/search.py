from pathlib import Path

from corpus_mcp.config import DOCS_ROOT, MAX_RESULTS
from corpus_mcp.index import DocumentIndex

_indexes: dict[Path, DocumentIndex] = {}


def search_documents(query: str, limit: int = 5, root: Path = DOCS_ROOT) -> list[dict]:
    if not query or not query.strip():
        raise ValueError("query must not be empty.")
    if not 1 <= limit <= MAX_RESULTS:
        raise ValueError(f"limit must be between 1 and {MAX_RESULTS}.")

    key = root.resolve()
    if key not in _indexes:
        _indexes[key] = DocumentIndex(key)
    return _indexes[key].search(query, limit)
