import pytest

from corpus_mcp.config import MAX_READ_CHARS
from corpus_mcp.tools.files import list_documents, read_document
from corpus_mcp.tools.search import search_documents
from corpus_mcp.tools.stats import folder_stats


@pytest.fixture
def root(tmp_path):
    (tmp_path / "lambda.md").write_text("Lambda is serverless compute. Cold starts matter.")
    (tmp_path / "rag.md").write_text("Hybrid search mixes BM25 with vector search for retrieval.")
    (tmp_path / "docker.txt").write_text("Docker builds container images.")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "git.md").write_text("Git rebase rewrites history.")
    return tmp_path


def test_list_all(root):
    assert len(list_documents(root=root)) == 4


def test_list_filter_extension(root):
    assert len(list_documents(extension="md", root=root)) == 3
    assert len(list_documents(extension=".txt", root=root)) == 1


def test_list_bad_limit(root):
    with pytest.raises(ValueError):
        list_documents(limit=0, root=root)


def test_list_bad_extension(root):
    with pytest.raises(ValueError):
        list_documents(extension="exe", root=root)


def test_read_document(root):
    result = read_document("sub/git.md", root)
    assert "rebase" in result["content"]
    assert result["truncated"] is False


def test_read_truncates_long_files(root):
    (root / "long.md").write_text("x" * (MAX_READ_CHARS + 10))
    result = read_document("long.md", root)
    assert result["truncated"] is True
    assert len(result["content"]) == MAX_READ_CHARS


def test_read_blocks_traversal(root):
    with pytest.raises(ValueError):
        read_document("../../etc/passwd", root)


def test_search_finds_best_match(root):
    results = search_documents("serverless", root=root)
    assert results and results[0]["path"] == "lambda.md"


def test_search_no_match(root):
    assert search_documents("zzzzqqqq", root=root) == []


def test_search_empty_query(root):
    with pytest.raises(ValueError):
        search_documents("   ", root=root)


def test_stats(root):
    result = folder_stats(root)
    assert result["total_files"] == 4
    assert result["files_by_extension"][".md"] == 3
