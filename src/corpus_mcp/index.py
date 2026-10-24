import re
from pathlib import Path

from rank_bm25 import BM25Okapi

from corpus_mcp.config import DOCS_ROOT
from corpus_mcp.tools.files import iter_documents

TOKEN_RE = re.compile(r"[a-z0-9_]+")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def make_snippet(text: str, tokens: list[str], width: int = 100) -> str:
    lowered = text.lower()
    positions = [lowered.find(t) for t in tokens if t in lowered]
    if not positions:
        return text[: width * 2].replace("\n", " ").strip()
    pos = min(positions)
    start, end = max(0, pos - width), min(len(text), pos + width)
    snippet = text[start:end].replace("\n", " ").strip()
    return ("..." if start > 0 else "") + snippet + ("..." if end < len(text) else "")


class DocumentIndex:
    """BM25 index over the documents folder. Rebuilds itself when files change."""

    def __init__(self, root: Path = DOCS_ROOT):
        self.root = root.resolve()
        self._signature: tuple | None = None
        self._paths: list[str] = []
        self._texts: list[str] = []
        self._bm25: BM25Okapi | None = None

    def _current_signature(self) -> tuple:
        return tuple(
            (str(p), p.stat().st_mtime_ns, p.stat().st_size)
            for p in iter_documents(self.root)
        )

    def refresh(self) -> None:
        signature = self._current_signature()
        if signature == self._signature:
            return
        paths, texts = [], []
        for path in iter_documents(self.root):
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            paths.append(path.relative_to(self.root).as_posix())
            texts.append(text)
        tokenized = [tokenize(t) for t in texts]
        self._paths, self._texts = paths, texts
        self._bm25 = BM25Okapi(tokenized) if any(tokenized) else None
        self._signature = signature

    def search(self, query: str, limit: int) -> list[dict]:
        self.refresh()
        tokens = tokenize(query)
        if not tokens or self._bm25 is None:
            return []
        scores = self._bm25.get_scores(tokens)
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        results = []
        for i in ranked:
            if scores[i] <= 0 or len(results) >= limit:
                break
            results.append(
                {
                    "path": self._paths[i],
                    "score": round(float(scores[i]), 3),
                    "snippet": make_snippet(self._texts[i], tokens),
                }
            )
        return results
