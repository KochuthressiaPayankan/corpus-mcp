import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Root folder the server is allowed to read. Everything outside is off-limits.
DOCS_ROOT: Path = Path(os.getenv("DOCS_ROOT", "./sample_docs")).resolve()

# Only these file types can be listed/read/indexed
ALLOWED_EXTENSIONS: frozenset[str] = frozenset(
    {".md", ".txt", ".py", ".json", ".csv", ".rst"}
)

MAX_FILE_BYTES: int = 200_000      # refuse to read files bigger than this
MAX_READ_CHARS: int = 20_000       # truncate returned text beyond this
MAX_RESULTS: int = 50              # hard cap on any list/search result
