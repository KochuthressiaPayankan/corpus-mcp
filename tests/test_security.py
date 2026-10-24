import os
from pathlib import Path

import pytest

from corpus_mcp.security import SecurityError, safe_resolve


@pytest.fixture
def root(tmp_path: Path) -> Path:
    (tmp_path / "ok.md").write_text("hello")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "nested.txt").write_text("nested")
    (tmp_path / "script.exe").write_text("nope")
    return tmp_path


def test_valid_file(root):
    assert safe_resolve("ok.md", root) == (root / "ok.md").resolve()


def test_nested_file(root):
    assert safe_resolve("sub/nested.txt", root).name == "nested.txt"


def test_empty_path(root):
    with pytest.raises(SecurityError):
        safe_resolve("   ", root)


def test_traversal_blocked(root):
    with pytest.raises(SecurityError):
        safe_resolve("../../etc/passwd", root)


def test_absolute_outside_blocked(root, tmp_path_factory):
    outside = tmp_path_factory.mktemp("outside") / "secret.md"
    outside.write_text("secret")
    with pytest.raises(SecurityError):
        safe_resolve(str(outside), root)


def test_bad_extension(root):
    with pytest.raises(SecurityError):
        safe_resolve("script.exe", root)


def test_missing_file(root):
    with pytest.raises(FileNotFoundError):
        safe_resolve("missing.md", root)


def test_symlink_escape_blocked(root, tmp_path_factory):
    outside = tmp_path_factory.mktemp("outside2") / "secret.md"
    outside.write_text("secret")
    link = root / "link.md"
    try:
        os.symlink(outside, link)
    except (OSError, NotImplementedError):
        pytest.skip("Symlinks not supported here")
    with pytest.raises(SecurityError):
        safe_resolve("link.md", root)
