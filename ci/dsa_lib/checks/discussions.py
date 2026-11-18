"""Discussion rules: D10 (two or more items), D11 (same topic), D12/D13 (look-alikes).

Single purpose: stop the same topic being stored as two discussions
(spec section 8) by comparing every pair of discussions.
"""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations

from .. import dedupe
from ..model import Finding, Item, Repo, distinct_from_slugs, error, warning


def _about(repo: Repo, item: Item) -> frozenset[str]:
    """The discussion's `about` set, redirects followed and duplicates removed."""
    return dedupe.link_set(item.values("about"), repo.resolve)


def _declared_distinct(repo: Repo, first: Item, second: Item) -> bool:
    """True when either discussion names the other in distinct_from."""
    names_second = second.slug in {repo.resolve(s) for s in distinct_from_slugs(first)}
    names_first = first.slug in {repo.resolve(s) for s in distinct_from_slugs(second)}
    return names_second or names_first


def check_d10_about_size(repo: Repo) -> list[Finding]:
    """D10: a discussion is about at least 2 distinct items."""
    return [
        error("D10", item.path, "about", "a discussion about one item belongs in that item's own file", (item.slug,))
        for item in repo.items_of("discussion") if len(_about(repo, item)) < 2
    ]


def check_d11_same_topic(repo: Repo) -> list[Finding]:
    """D11: two discussions with the same topic key, unless one declares distinct_from."""
    groups: dict[str, list[Item]] = defaultdict(list)
    for item in repo.items_of("discussion"):
        if len(_about(repo, item)) >= 2:
            groups[dedupe.topic_key(item.values("about"), repo.resolve)].append(item)
    findings = []
    for key, members in sorted(groups.items()):
        for first, second in combinations(members, 2):
            if not _declared_distinct(repo, first, second):
                findings.append(error("D11", second.path, "about", f"same topic as '{first.slug}' ({key}); merge them or add distinct_from with a reason", (first.slug, second.slug)))
    return findings


def _text_reasons(first: Item, second: Item) -> list[str]:
    """Describe which of question/title are at or above the text similarity threshold."""
    reasons = []
    for name in ("question", "title"):
        ratio = dedupe.text_similarity(str(first.data.get(name, "")), str(second.data.get(name, "")))
        if ratio >= dedupe.TEXT_THRESHOLD:
            reasons.append(f"{name} similarity {ratio:.2f}")
    return reasons


def _pair_findings(repo: Repo, first: Item, second: Item) -> list[Finding]:
    """D12/D13 warnings for one pair of discussions with different topic keys."""
    one, two = _about(repo, first), _about(repo, second)
    slugs, file = (first.slug, second.slug), second.path
    found = []
    if dedupe.is_strict_subset(one, two) or dedupe.is_strict_subset(two, one):
        found.append(warning("D12", file, "about", f"'{first.slug}' and '{second.slug}': one link set contains the other; consider one file with sections", slugs))
    reasons = _text_reasons(first, second)
    overlap = dedupe.jaccard(one, two)
    if overlap >= dedupe.JACCARD_THRESHOLD:
        reasons.append(f"link overlap {overlap:.2f}")
    if reasons:
        found.append(warning("D13", file, "about", f"'{first.slug}' and '{second.slug}' look alike ({', '.join(reasons)}); review by hand", slugs))
    return found


def check_d12_d13_look_alikes(repo: Repo) -> list[Finding]:
    """D12 and D13: warn about discussions whose links or wording overlap heavily.

    Pairs with the same topic key (D11) and pairs declared distinct are skipped.
    """
    usable = [item for item in repo.items_of("discussion") if len(_about(repo, item)) >= 2]
    findings: list[Finding] = []
    for first, second in combinations(sorted(usable, key=lambda item: item.slug), 2):
        same_topic = _about(repo, first) == _about(repo, second)
        if not same_topic and not _declared_distinct(repo, first, second):
            findings.extend(_pair_findings(repo, first, second))
    return findings
