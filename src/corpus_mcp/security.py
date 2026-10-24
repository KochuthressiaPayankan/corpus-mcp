from pathlib import Path

from corpus_mcp.config import ALLOWED_EXTENSIONS, DOCS_ROOT, MAX_FILE_BYTES


class SecurityError(ValueError):
    """Raised when a requested path is not allowed."""


def safe_resolve(user_path: str, root: Path = DOCS_ROOT) -> Path:
    """Resolve a user-supplied path and guarantee it stays inside `root`.

    Rejects: empty paths, absolute paths outside root, '..' traversal,
    symlinks that point outside root, disallowed extensions, oversized files.
    """
    if not user_path or not user_path.strip():
        raise SecurityError("Path must not be empty.")

    root = root.resolve()
    candidate = Path(user_path)

    # Relative paths are relative to root; absolute paths are checked as-is
    full = candidate if candidate.is_absolute() else root / candidate
    resolved = full.resolve()  # collapses '..' and follows symlinks

    try:
        resolved.relative_to(root)
    except ValueError:
        raise SecurityError("Access denied: path is outside the documents folder.")

    if resolved.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise SecurityError(
            f"File type '{resolved.suffix}' is not allowed. "
            f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    if not resolved.exists():
        raise FileNotFoundError(
            f"File not found: {user_path}. Use list_documents to see available files."
        )

    if not resolved.is_file():
        raise SecurityError("Path is not a file.")

    if resolved.stat().st_size > MAX_FILE_BYTES:
        raise SecurityError(f"File is too large (limit {MAX_FILE_BYTES} bytes).")

    return resolved
