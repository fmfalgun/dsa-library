"""Generator tests: deterministic bytes, correct graph, correct staleness detection.

Single purpose: prove api/v1 is byte-stable and that index.json carries the
links the spec's acceptance list names.
"""

from __future__ import annotations

import json

from conftest import all_findings, make_repo, rule_ids, write_generated
from dsa_lib import emit


def _api_bytes(root) -> dict[str, bytes]:
    """Return every generated file's bytes, keyed by relative path, for byte comparison."""
    files = sorted((root / "api" / "v1").rglob("*.json")) + [root / "README.md"]
    return {path.relative_to(root).as_posix(): path.read_bytes() for path in files}


def _index(root) -> dict:
    """Load the generated index.json."""
    return json.loads((root / "api" / "v1" / "index.json").read_text(encoding="utf-8"))


def test_running_the_generator_twice_changes_nothing(tmp_path):
    """Spec acceptance: a second run produces byte-identical api/v1 and README."""
    root = make_repo(tmp_path)
    write_generated(root)
    first = _api_bytes(root)
    write_generated(root)
    assert _api_bytes(root) == first


def test_check_passes_right_after_generation(tmp_path):
    """After writing, the staleness check (D16) finds nothing."""
    root = make_repo(tmp_path, generate_first=True)
    assert rule_ids(all_findings(root, include_stale=True)) == set()


def test_index_computes_reverse_links(tmp_path):
    """Spec acceptance: used_by on sliding-window and monotonic-deque, discussed_in on greedy."""
    root = make_repo(tmp_path, generate_first=True)
    items = _index(root)["items"]
    problem = "leetcode-0239-sliding-window-maximum"
    assert items["sliding-window"]["links"]["used_by"] == [problem]
    assert items["monotonic-deque"]["links"]["used_by"] == [problem]
    assert items["greedy"]["links"]["discussed_in"] == ["2026-11-17-why-greedy-fails-coin-change"]


def test_symmetric_links_appear_on_both_items(tmp_path):
    """related is stored once (in sliding-window) but published on both concepts."""
    items = _index(make_repo(tmp_path, generate_first=True))["items"]
    assert items["sliding-window"]["links"]["related"] == ["two-pointers"]
    assert items["two-pointers"]["links"]["related"] == ["sliding-window"]


def test_index_lookups_topic_keys_and_aliases(tmp_path):
    """topic_keys, aliases (lowercased) and the problem's judge URL are published."""
    index = _index(make_repo(tmp_path, generate_first=True))
    assert index["topic_keys"] == {"coin-change|dynamic-programming|greedy": ["2026-11-17-why-greedy-fails-coin-change"]}
    assert index["aliases"]["moving window"] == "sliding-window"
    problem = index["items"]["leetcode-0239-sliding-window-maximum"]
    assert problem["problem_url"].startswith("https://leetcode.com/")
    assert problem["url"].endswith("problems/leetcode-0239-sliding-window-maximum.md")


def test_renamed_slug_resolves_in_index_with_a_recorded_warning(tmp_path):
    """Spec acceptance: an old slug resolves to the new one, and the warning is in diagnostics."""
    root = make_repo(tmp_path, "links/d05_redirect")
    write_generated(root)
    index = _index(root)
    assert index["items"]["uses-old-name"]["links"]["prerequisites"] == ["greedy"]
    assert index["redirects"] == {"old-greedy": "greedy"}
    assert [w["rule"] for w in index["diagnostics"]["warnings"]] == ["D5"]


def test_stale_and_unexpected_generated_files_fail_d16(tmp_path):
    """Editing a generated file, or adding a stray one under api/v1, is caught by D16."""
    root = make_repo(tmp_path, generate_first=True)
    (root / "api" / "v1" / "search.json").write_text("[]\n", encoding="utf-8")
    (root / "api" / "v1" / "extra.json").write_text("{}\n", encoding="utf-8")
    messages = [found.file for found in all_findings(root, include_stale=True) if found.rule == "D16"]
    assert "api/v1/search.json" in messages and "api/v1/extra.json" in messages


def test_readme_without_markers_fails_d16(tmp_path):
    """A README lacking the rule markers cannot be regenerated, so D16 reports it."""
    root = make_repo(tmp_path, generate_first=True)
    (root / "README.md").write_text("no markers here\n", encoding="utf-8")
    assert "D16" in rule_ids(all_findings(root, include_stale=True))


def test_x_keys_are_copied_to_extra(tmp_path):
    """An `x_` front-matter key is accepted and published untouched under `extra`."""
    root = make_repo(tmp_path)
    path = root / "concepts" / "arrays.md"
    path.write_text(path.read_text(encoding="utf-8").replace("status: stub\n", "status: stub\nx_note: hello\n", 1), encoding="utf-8")
    write_generated(root)
    assert _index(root)["items"]["arrays"]["extra"] == {"x_note": "hello"}


def test_dumps_is_canonical():
    """dumps sorts keys, indents by 2 spaces, ends with a newline and keeps non-ASCII text."""
    assert emit.dumps({"b": 1, "a": "é"}) == '{\n  "a": "é",\n  "b": 1\n}\n'
