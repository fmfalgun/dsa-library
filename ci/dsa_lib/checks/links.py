"""Link rules: D4 (link fields), D5 (targets), D6 (cycles, self-links), D7 (symmetric pairs).

Single purpose: check that every stored link is allowed, points at something
real of the right kind, and is stored exactly once.
"""

from __future__ import annotations

from ..graph import find_cycle, stored_targets
from ..model import (
    LINK_FIELDS, Finding, Item, Repo, distinct_from_slugs, error, misplaced_link_fields, owned_links, warning,
)

_DIRECTED_FIELDS = ("prerequisites", "variant_of", "follow_up_of")
_SYMMETRIC_FIELDS = tuple(name for name, spec in LINK_FIELDS.items() if spec.symmetric)


def check_d04_link_fields(repo: Repo) -> list[Finding]:
    """D4: every link field sits on the kind that owns it."""
    return [
        error("D4", item.path, name, f"'{name}' is only allowed on {LINK_FIELDS[name].owner} files", (item.slug,))
        for item in repo.items if not item.error
        for name in misplaced_link_fields(item)
    ]


def _target_finding(repo: Repo, item: Item, field_name: str, target: str, allowed: tuple[str, ...]) -> Finding | None:
    """Return the D5 finding for one link target, or None when the link is fine.

    A target reached through a redirect is a warning (update the link); a
    missing target or one of the wrong kind is an error.
    """
    destination = repo.by_slug.get(repo.resolve(target))
    slugs = (item.slug,)
    if destination is None:
        return error("D5", item.path, field_name, f"'{target}' does not exist", slugs)
    if destination.kind not in allowed:
        return error("D5", item.path, field_name, f"'{target}' is a {destination.kind}; {field_name} needs {' or '.join(allowed)}", slugs)
    if target != destination.slug:
        return warning("D5", item.path, field_name, f"'{target}' was renamed to '{destination.slug}'; update the link", slugs)
    return None


def check_d05_link_targets(repo: Repo) -> list[Finding]:
    """D5: every link target exists (or resolves through a redirect) and is the right kind."""
    findings = []
    for item in repo.items:
        checks = [(name, spec.targets, target) for name, spec, target in owned_links(item)]
        if item.kind == "discussion":
            checks += [("distinct_from", tuple(LINK_FIELDS["about"].targets), s) for s in distinct_from_slugs(item)]
        for name, allowed, target in checks:
            finding = _target_finding(repo, item, name, target, allowed)
            if finding:
                findings.append(finding)
    return findings


def _cycle_finding(repo: Repo, field_name: str) -> Finding | None:
    """Return a D6 finding when one directed field has a cycle across the repo."""
    edges = {item.slug: stored_targets(repo, item, field_name) for item in repo.items if not item.error}
    cycle = find_cycle(edges)
    if not cycle:
        return None
    start = repo.by_slug[cycle[0]]
    return error("D6", start.path, field_name, "cycle: " + " -> ".join(cycle), tuple(sorted(set(cycle))))


def check_d06_cycles_and_self_links(repo: Repo) -> list[Finding]:
    """D6: no self-links in any field; no cycles in prerequisites, variant_of or follow_up_of."""
    findings = [
        error("D6", item.path, name, "an item cannot link to itself", (item.slug,))
        for item in repo.items
        for name, _spec, target in owned_links(item)
        if repo.resolve(target) == item.slug
    ]
    cycles = (_cycle_finding(repo, name) for name in _DIRECTED_FIELDS)
    return findings + [finding for finding in cycles if finding]


def _mutual_pairs(repo: Repo, name: str) -> list[tuple[str, str]]:
    """Return (a, b) with a < b where each item lists the other in the symmetric field `name`."""
    stored = {item.slug: set(stored_targets(repo, item, name)) for item in repo.items if not item.error}
    return [
        (slug, other)
        for slug, targets in sorted(stored.items())
        for other in sorted(targets)
        if slug < other and slug in stored.get(other, set())
    ]


def check_d07_symmetric_pairs(repo: Repo) -> list[Finding]:
    """D7: a related/similar pair is stored in one file only, never both."""
    return [
        error("D7", repo.by_slug[slug].path, name,
              f"'{slug}' and '{other}' list each other; keep the link in the newer file only", (slug, other))
        for name in _SYMMETRIC_FIELDS
        for slug, other in _mutual_pairs(repo, name)
    ]
