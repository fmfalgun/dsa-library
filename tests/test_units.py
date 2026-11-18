"""Unit tests for pure helpers: cycle detection, topic keys, similarity, slug IDs, xrefs.

Single purpose: pin the behaviour of the small functions the rules build on.
"""

from __future__ import annotations

import json
from pathlib import Path

from conftest import REPO_ROOT, all_findings, make_repo, load
from dsa_lib import dedupe, graph
from dsa_lib.checks import xrefs
from dsa_lib.checks.identity import format_source_id
from dsa_lib.config import load_config


def test_find_cycle_returns_the_loop_or_none():
    """An acyclic graph gives None; a loop gives the path that closes on its start."""
    assert graph.find_cycle({"a": ["b"], "b": ["c"], "c": []}) is None
    assert graph.find_cycle({"a": ["b"], "b": ["c"], "c": ["a"]}) == ["a", "b", "c", "a"]


def test_topic_key_ignores_order_and_repeats():
    """The spec's example: both orderings give coin-change|dynamic-programming|greedy."""
    same = lambda slug: slug  # noqa: E731 - no redirects in this test
    first = dedupe.topic_key(["greedy", "coin-change", "dynamic-programming"], same)
    second = dedupe.topic_key(["dynamic-programming", "greedy", "coin-change", "greedy"], same)
    assert first == second == "coin-change|dynamic-programming|greedy"


def test_topic_key_follows_redirects():
    """A redirected slug counts as its target when building the key."""
    redirects = {"old": "a"}
    assert dedupe.topic_key(["old", "b"], lambda slug: redirects.get(slug, slug)) == "a|b"


def test_subset_and_jaccard():
    """Strict subset excludes equality; Jaccard is shared over all."""
    small, big = frozenset({"a", "b"}), frozenset({"a", "b", "c"})
    assert dedupe.is_strict_subset(small, big) and not dedupe.is_strict_subset(big, big)
    assert dedupe.jaccard(small, big) == 2 / 3 and dedupe.jaccard(frozenset(), frozenset()) == 0.0


def test_text_similarity_ignores_case_and_punctuation():
    """Questions differing only in case and punctuation are identical after normalizing."""
    assert dedupe.text_similarity("Why does greedy fail?", "why does GREEDY fail") == 1.0
    assert dedupe.text_similarity("binary search", "dijkstra shortest paths") < dedupe.TEXT_THRESHOLD


def test_format_source_id_per_source():
    """LeetCode IDs zero-pad to four digits; Codeforces IDs lowercase; interview has none."""
    sources = load_config(REPO_ROOT).sources
    assert format_source_id(sources["leetcode"], "239") == "0239"
    assert format_source_id(sources["codeforces"], "4A") == "4a"
    assert format_source_id(sources["interview"], "whatever") == ""


def test_offline_xref_with_known_alias_passes(tmp_path):
    """library-data:people/... is registered, so D17 (offline) accepts it."""
    root = make_repo(tmp_path)
    path = root / "concepts" / "arrays.md"
    path.write_text(path.read_text(encoding="utf-8").replace("status: stub\n", "status: stub\nxrefs: [library-data:people/ken-thompson]\n", 1), encoding="utf-8")
    assert all_findings(root) == []


def _repo_with_xref(tmp_path: Path):
    """Build a repo whose `arrays` concept carries one library-data xref; return the loaded Repo."""
    root = make_repo(tmp_path)
    path = root / "concepts" / "arrays.md"
    path.write_text(path.read_text(encoding="utf-8").replace("status: stub\n", "status: stub\nxrefs: [library-data:people/ken-thompson]\n", 1), encoding="utf-8")
    return load(root)


def test_online_xref_found_missing_and_unreachable(tmp_path):
    """Spec acceptance: a missing or unreachable target only warns; a listed one is silent."""
    repo = _repo_with_xref(tmp_path)

    def listed(_url):
        """Stub fetcher: the manifest lists the record."""
        return ["ken-thompson.json"]

    def missing(_url):
        """Stub fetcher: the manifest does not list the record."""
        return ["someone-else.json"]

    def unreachable(_url):
        """Stub fetcher: the network is down."""
        raise OSError("offline")

    assert xrefs.check_d17_online(repo, listed) == []
    assert [f.severity for f in xrefs.check_d17_online(repo, missing)] == ["warning"]
    assert [f.severity for f in xrefs.check_d17_online(repo, unreachable)] == ["warning"]


def test_xref_url_points_at_the_record_file(tmp_path):
    """library-data:people/x resolves to <base>data/people/x.json."""
    repo = _repo_with_xref(tmp_path)
    assert xrefs.xref_url(repo, "library-data:people/ken-thompson") == "https://fmfalgun.github.io/library-data/data/people/ken-thompson.json"
    assert xrefs.xref_url(repo, "nope:people/x") is None
