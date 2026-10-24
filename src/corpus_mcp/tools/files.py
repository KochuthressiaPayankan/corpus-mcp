from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from corpus_mcp.config import (
    ALLOWED_EXTENSIONS,
    DOCS_ROOT,
    MAX_FILE_BYTES,
    MAX_READ_CHARS,
    MAX_RESULTS,
)
from corpus_mcp.security import safe_resolve


def iso(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat(timespec="seconds")


def iter_documents(root: Path = DOCS_ROOT) -> Iterator[Path]:
    """Yield every allowed, reasonably sized file under root (sorted).

    Skips hidden folders, disallowed extensions, oversized files, and
    symlinks that point outside root.
    """
    root = root.resolve()
    for path in sorted(root.rglob("*")):
        rel_parts = path.relative_to(root).parts
        if any(part.startswith(".") for part in rel_parts):
            continue
        if not path.is_file() or path.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue
        try:
            path.resolve().relative_to(root)
        except ValueError:
            continue
        if path.stat().st_size > MAX_FILE_BYTES:
            continue
        yield path


def list_documents(
    extension: str | None = None,
    limit: int = 50,
    root: Path = DOCS_ROOT,
) -> list[dict]:
    if not 1 <= limit <= MAX_RESULTS:
        raise ValueError(f"limit must be between 1 and {MAX_RESULTS}.")

    wanted = None
    if extension:
        wanted = extension.lower()
        if not wanted.startswith("."):
            wanted = "." + wanted
        if wanted not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Extension '{extension}' is not supported. "
                f"Supported: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )

    root = root.resolve()
    results = []
    for path in iter_documents(root):
        if wanted and path.suffix.lower() != wanted:
            continue
        stat = path.stat()
        results.append(
            {
                "path": path.relative_to(root).as_posix(),
                "size_bytes": stat.st_size,
                "modified": iso(stat.st_mtime),
            }
        )
        if len(results) >= limit:
            break
    return results


def read_document(path: str, root: Path = DOCS_ROOT) -> dict:
    resolved = safe_resolve(path, root)
    text = resolved.read_text(encoding="utf-8", errors="replace")
    truncated = len(text) > MAX_READ_CHARS
    return {
        "path": resolved.relative_to(root.resolve()).as_posix(),
        "content": text[:MAX_READ_CHARS],
        "truncated": truncated,
        "total_chars": len(text),
    }
