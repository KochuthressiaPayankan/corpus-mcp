from collections import Counter
from pathlib import Path

from corpus_mcp.config import DOCS_ROOT
from corpus_mcp.tools.files import iso, iter_documents


def folder_stats(root: Path = DOCS_ROOT) -> dict:
    root = root.resolve()
    files = list(iter_documents(root))
    by_extension = Counter(p.suffix.lower() for p in files)
    recent = sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[:5]
    return {
        "total_files": len(files),
        "total_size_bytes": sum(p.stat().st_size for p in files),
        "files_by_extension": dict(by_extension),
        "most_recent": [
            {"path": p.relative_to(root).as_posix(), "modified": iso(p.stat().st_mtime)}
            for p in recent
        ],
    }
