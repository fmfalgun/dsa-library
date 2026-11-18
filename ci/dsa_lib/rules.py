"""The D1-D20 rule table and the runner that applies every check.

Single purpose: be the one list of rules (README text, severities) and the one
place that decides which check functions run, offline and online.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .checks import discussions, fields, hygiene, identity, layout, links, xrefs
from .model import Finding, Repo
from .schema import check_d03_schema


@dataclass(frozen=True)
class Rule:
    """One validation rule as documented in spec section 10."""

    rule_id: str
    severity: str
    text: str


RULES: tuple[Rule, ...] = (
    Rule("D1", "error", "Every content file is `concepts/`, `problems/` or `discussions/` + `<slug>.md`; filename = `slug`; slug matches the format; no other files in those folders"),
    Rule("D2", "error", "Slugs are unique across all kinds; no slug equals a key in `redirects.json`"),
    Rule("D3", "error", "Front matter parses and passes its JSON Schema; `kind` matches the folder; required fields present; unknown keys only with an `x_` prefix"),
    Rule("D4", "error", "Only the seven link fields from section 7 are used, each on its allowed kind"),
    Rule("D5", "error", "Every link target exists, or resolves through a redirect (resolving is a warning); the target is of the right kind for that field"),
    Rule("D6", "error", "No cycles in `prerequisites`, `variant_of` or `follow_up_of`; no self-links in any field"),
    Rule("D7", "error", "A symmetric pair (`related`, `similar`) is not stored in both files"),
    Rule("D8", "error", "No duplicate entries inside a link, tag or alias list"),
    Rule("D9", "error", "Each `(source, source_id)` pair is unique; the slug prefix matches `source`; `url` matches the source's pattern"),
    Rule("D10", "error", "A discussion's `about` has at least 2 distinct items after resolving redirects"),
    Rule("D11", "error", "Topic keys are unique unless one file of the pair names the other in `distinct_from`"),
    Rule("D12", "warning", "One discussion's link set is a strict subset of another's"),
    Rule("D13", "warning", "Link-set Jaccard >= 0.75, or question/title similarity >= 0.85"),
    Rule("D14", "error", "Aliases are unique, lowercase-unique, and never equal to an existing slug or title of another item"),
    Rule("D15", "error", "`show_on` values are in `config/sites.json`; `tags` are in `config/tags.json`"),
    Rule("D16", "error", "`api/v1/` and the README rule list are exactly what the generator produces now (`--check` mode)"),
    Rule("D17", "error offline / warning online", "`xrefs` match `<alias>:<path>` with a registered alias (offline); the target exists (online, CI only)"),
    Rule("D18", "error", "Redirect sources have no file; redirect targets exist; no chains or loops (A->B->C must be written as A->C)"),
    Rule("D19", "error", "`created` <= `updated`; both are valid dates, not in the future; a discussion's slug date equals `created`"),
    Rule("D20", "error", "No secrets in content, config, docs or templates; no file over 1 MB in content folders"),
)

OFFLINE_CHECKS: tuple[Callable[[Repo], list[Finding]], ...] = (
    layout.check_d01_layout,
    layout.check_d02_unique_slugs,
    check_d03_schema,
    links.check_d04_link_fields,
    links.check_d05_link_targets,
    links.check_d06_cycles_and_self_links,
    links.check_d07_symmetric_pairs,
    fields.check_d08_duplicate_entries,
    identity.check_d09_problem_identity,
    discussions.check_d10_about_size,
    discussions.check_d11_same_topic,
    discussions.check_d12_d13_look_alikes,
    identity.check_d14_aliases,
    fields.check_d15_allowed_values,
    xrefs.check_d17_offline,
    layout.check_d18_redirects,
    fields.check_d19_dates,
    hygiene.check_d20_secrets_and_size,
)


def _sorted(findings: list[Finding]) -> list[Finding]:
    """Order findings deterministically so output and the index never depend on check order."""
    return sorted(findings, key=lambda found: (found.file, found.rule, found.field, found.message))


def run_offline_checks(repo: Repo) -> list[Finding]:
    """Run every check that needs no network; return all findings, sorted."""
    findings: list[Finding] = []
    for check in OFFLINE_CHECKS:
        findings.extend(check(repo))
    return _sorted(findings)


def run_online_checks(repo: Repo, fetch: xrefs.Fetcher) -> list[Finding]:
    """Run the network checks (D17 online); every finding is a warning."""
    return _sorted(xrefs.check_d17_online(repo, fetch))


def render_rules_markdown() -> str:
    """Return the README rule list as Markdown, generated from RULES."""
    lines = ["| Rule | Severity | Check |", "| --- | --- | --- |"]
    lines.extend(f"| {rule.rule_id} | {rule.severity} | {rule.text} |" for rule in RULES)
    return "\n".join(lines)
