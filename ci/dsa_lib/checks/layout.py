"""Layout and identity-of-file rules: D1 (files and slugs), D2 (unique slugs), D18 (redirects).

Single purpose: check that files are where and what their names say they are.
"""

from __future__ import annotations

import re
from collections import Counter

from ..model import SLUG_MAX_LENGTH, SLUG_PATTERN, Finding, Repo, error

_DISCUSSION_SLUG = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}-.+")


def _stem_findings(item) -> list[Finding]:
    """D1 findings for one item's filename: slug format, kind pattern, filename = slug field."""
    problems = []
    if not re.fullmatch(SLUG_PATTERN, item.stem) or len(item.stem) > SLUG_MAX_LENGTH:
        problems.append(f"filename '{item.stem}' is not a valid slug (a-z, 0-9, hyphens; max {SLUG_MAX_LENGTH})")
    if item.kind == "discussion" and not _DISCUSSION_SLUG.match(item.stem):
        problems.append("a discussion slug must start with yyyy-mm-dd-")
    declared = item.data.get("slug")
    if declared is not None and declared != item.stem:
        problems.append(f"front matter slug '{declared}' differs from the filename '{item.stem}'")
    return [error("D1", item.path, "slug", message, (item.slug,)) for message in problems]


def check_d01_layout(repo: Repo) -> list[Finding]:
    """D1: only `<slug>.md` files in the content folders; filename equals slug; slug format."""
    findings = [
        error("D1", path, "", "not a plain <slug>.md file: remove it or move it out of the content folder")
        for path in repo.stray_paths
    ]
    for item in repo.items:
        findings.extend(_stem_findings(item))
    return findings


def check_d02_unique_slugs(repo: Repo) -> list[Finding]:
    """D2: slugs are unique across all kinds, and none equals a redirect source."""
    counts = Counter(item.slug for item in repo.items)
    findings = []
    for item in repo.items:
        if counts[item.slug] > 1:
            findings.append(error("D2", item.path, "slug", f"slug '{item.slug}' is used by more than one file", (item.slug,)))
        if item.slug in repo.config.redirects:
            findings.append(error("D2", item.path, "slug", f"slug '{item.slug}' is also a key in config/redirects.json", (item.slug,)))
    return findings


def check_d18_redirects(repo: Repo) -> list[Finding]:
    """D18: redirect sources have no file, targets exist, and there are no chains or loops."""
    findings = []
    for old, new in sorted(repo.config.redirects.items()):
        file = "config/redirects.json"
        if old in repo.by_slug:
            findings.append(error("D18", file, old, f"redirect source '{old}' still has a file"))
        if new not in repo.by_slug:
            findings.append(error("D18", file, old, f"redirect target '{new}' does not exist"))
        if new in repo.config.redirects:
            findings.append(error("D18", file, old, f"'{old}' -> '{new}' is a chain or loop; point '{old}' at the final slug"))
    return findings
