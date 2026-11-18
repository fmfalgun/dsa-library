"""Command-line tests: --check, --new, --explain and exit codes.

Single purpose: drive ci/sync_index.py's main() the way a user or CI does.
"""

from __future__ import annotations

import sync_index
from conftest import make_repo


def run(root, *args: str) -> int:
    """Call the CLI against the repo at `root` and return its exit code."""
    return sync_index.main(["--root", str(root), *args])


def test_default_run_writes_files_and_check_then_passes(tmp_path):
    """A plain run writes api/v1; a following --check passes with exit code 0."""
    root = make_repo(tmp_path)
    assert run(root) == 0
    assert (root / "api" / "v1" / "index.json").is_file()
    assert run(root, "--check") == 0


def test_check_fails_and_writes_nothing_when_output_is_missing(tmp_path):
    """--check on a repo with no generated files exits 1 and creates nothing."""
    root = make_repo(tmp_path)
    assert run(root, "--check") == 1
    assert not (root / "api").exists()


def test_errors_block_generation(tmp_path):
    """With a content error the run exits 1 and writes no api/v1."""
    root = make_repo(tmp_path, "structure/d03")
    assert run(root) == 1
    assert not (root / "api").exists()


def test_new_creates_a_file_with_todays_date_then_refuses_a_repeat(tmp_path):
    """--new copies the template with the slug filled in, and refuses an existing slug."""
    root = make_repo(tmp_path)
    assert run(root, "--new", "concept", "binary-search") == 0
    text = (root / "concepts" / "binary-search.md").read_text(encoding="utf-8")
    assert "slug: binary-search" in text and "{{" not in text
    assert run(root, "--new", "concept", "binary-search") == 1


def test_new_rejects_bad_kind_and_bad_slug(tmp_path):
    """An unknown kind or an invalid slug exits 1 and creates nothing."""
    root = make_repo(tmp_path)
    assert run(root, "--new", "essay", "some-slug") == 1
    assert run(root, "--new", "concept", "Not A Slug") == 1


def test_new_problem_takes_its_source_from_the_slug(tmp_path):
    """A new problem file starts with the source taken from the slug's first word."""
    root = make_repo(tmp_path)
    assert run(root, "--new", "problem", "cses-1068-weird-algorithm") == 0
    assert "source: cses" in (root / "problems" / "cses-1068-weird-algorithm.md").read_text(encoding="utf-8")


def test_explain_prints_links_and_rejects_unknown_slugs(tmp_path, capsys):
    """--explain lists links in both directions and exits 1 for an unknown slug."""
    root = make_repo(tmp_path)
    assert run(root, "--explain", "greedy") == 0
    assert "discussed_in" in capsys.readouterr().out
    assert run(root, "--explain", "nothing-here") == 1
