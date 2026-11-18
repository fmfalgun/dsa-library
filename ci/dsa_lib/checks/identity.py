"""Identity rules: D9 (problem sources and IDs) and D14 (concept aliases).

Single purpose: keep every problem and every alias pointing at exactly one
thing, so the same problem or name cannot be stored twice.
"""

from __future__ import annotations

import re
from collections import defaultdict

from ..config import Source
from ..model import Finding, Item, Repo, error


def format_source_id(source: Source, raw_id: str) -> str:
    """Return the form of a judge's ID that appears in slugs.

    zero-pad-4 pads digit-only IDs (LeetCode 239 -> 0239); slugify lowercases
    and turns other characters into hyphens (Codeforces 4A -> 4a); none gives
    an empty string.
    """
    if source.slug_id_format == "none":
        return ""
    if source.slug_id_format == "zero-pad-4" and raw_id.isdigit():
        return raw_id.zfill(4)
    return re.sub(r"[^a-z0-9]+", "-", raw_id.lower()).strip("-")


def _required_prefix(source: Source, source_id: str | None) -> str:
    """Return the prefix the problem's slug must start with."""
    formatted = format_source_id(source, source_id) if source_id else ""
    return f"{source.key}-{formatted}-" if formatted else f"{source.key}-"


def _source_problems(item: Item, repo: Repo) -> list[str]:
    """List every D9 problem with one problem item's source, ID, slug prefix and URL."""
    source = repo.config.sources.get(item.data.get("source"))
    if source is None:
        return [f"source '{item.data.get('source')}' is not in config/sources.json"]
    source_id, url = item.data.get("source_id"), item.data.get("url")
    problems = []
    if source.id_required and not (source_id and url):
        problems.append(f"{source.name} problems need both source_id and url")
    prefix = _required_prefix(source, source_id)
    if not item.slug.startswith(prefix) or item.slug == prefix.rstrip("-"):
        problems.append(f"slug must start with '{prefix}' followed by a title")
    if url and source.url_pattern and not re.match(source.url_pattern, url):
        problems.append(f"url does not match the {source.name} pattern")
    return problems


def _duplicate_id_findings(problems: list[Item]) -> list[Finding]:
    """D9 findings for problems that share the same (source, source_id) pair."""
    owners: dict[tuple[str, str], list[Item]] = defaultdict(list)
    for item in problems:
        if item.data.get("source_id") and item.data.get("source"):
            owners[(item.data["source"], str(item.data["source_id"]).lower())].append(item)
    return [
        error("D9", item.path, "source_id", f"{source} {source_id} is already stored as '{items[0].slug}'", (item.slug,))
        for (source, source_id), items in sorted(owners.items())
        for item in items[1:]
    ]


def check_d09_problem_identity(repo: Repo) -> list[Finding]:
    """D9: known source, matching slug prefix and URL pattern, unique (source, source_id)."""
    problems = repo.items_of("problem")
    findings = [
        error("D9", item.path, "source", message, (item.slug,))
        for item in problems for message in _source_problems(item, repo)
    ]
    return findings + _duplicate_id_findings(problems)


def _alias_owners(repo: Repo) -> dict[str, list[Item]]:
    """Map each lowercased, trimmed alias to the concepts that declare it."""
    owners: dict[str, list[Item]] = defaultdict(list)
    for item in repo.items_of("concept"):
        for alias in item.values("aliases"):
            owners[alias.strip().lower()].append(item)
    return owners


def _foreign_names(repo: Repo, owner: Item) -> set[str]:
    """Slugs and lowercased titles of every item except `owner`: names an alias must not take."""
    names = set()
    for other in repo.items:
        if other is not owner:
            names.add(other.slug)
            names.add(str(other.data.get("title", "")).strip().lower())
    return names


def check_d14_aliases(repo: Repo) -> list[Finding]:
    """D14: aliases are unique (case-insensitive) and never another item's slug or title."""
    findings = []
    for alias, owners in sorted(_alias_owners(repo).items()):
        if len(owners) > 1:
            names = ", ".join(sorted(owner.slug for owner in owners))
            findings.append(error("D14", owners[1].path, "aliases", f"alias '{alias}' is declared more than once ({names})", (owners[0].slug,)))
        elif alias in _foreign_names(repo, owners[0]):
            findings.append(error("D14", owners[0].path, "aliases", f"alias '{alias}' equals another item's slug or title", (owners[0].slug,)))
    return findings
