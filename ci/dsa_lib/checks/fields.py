"""Field-value rules: D8 (no duplicates in lists), D15 (allowed values), D19 (dates).

Single purpose: check the values of fields that do not involve other items.
"""

from __future__ import annotations

from collections import Counter
from datetime import date

from ..model import LINK_FIELDS, Finding, Repo, error

_LIST_FIELDS = ("tags", "aliases", *LINK_FIELDS)


def check_d08_duplicate_entries(repo: Repo) -> list[Finding]:
    """D8: no list of links, tags or aliases repeats an entry."""
    findings = []
    for item in repo.items:
        for name in _LIST_FIELDS:
            repeated = [value for value, count in Counter(item.values(name)).items() if count > 1]
            findings.extend(
                error("D8", item.path, name, f"'{value}' appears more than once", (item.slug,))
                for value in sorted(repeated)
            )
    return findings


def check_d15_allowed_values(repo: Repo) -> list[Finding]:
    """D15: show_on values are registered sites and tags are in config/tags.json."""
    findings = []
    for item in repo.items:
        for site in item.values("show_on"):
            if site not in repo.config.sites:
                findings.append(error("D15", item.path, "show_on", f"'{site}' is not in config/sites.json", (item.slug,)))
        for tag in item.values("tags"):
            if tag not in repo.config.tags:
                findings.append(error("D15", item.path, "tags", f"'{tag}' is not in config/tags.json", (item.slug,)))
    return findings


def _parse_date(text: object) -> date | None:
    """Return the date for a `YYYY-MM-DD` string, or None when it is not a real date."""
    try:
        return date.fromisoformat(text) if isinstance(text, str) else None
    except ValueError:
        return None


def _date_problems(item, today: date) -> list[str]:
    """List what is wrong with an item's created/updated dates."""
    problems = []
    parsed = {name: _parse_date(item.data.get(name)) for name in ("created", "updated")}
    for name, value in parsed.items():
        if name in item.data and value is None:
            problems.append(f"{name} is not a valid YYYY-MM-DD date")
        elif value is not None and value > today:
            problems.append(f"{name} {value} is in the future")
    created, updated = parsed["created"], parsed["updated"]
    if created and updated and created > updated:
        problems.append("created is after updated")
    if item.kind == "discussion" and created and not item.stem.startswith(created.isoformat()):
        problems.append("the slug's date prefix must equal created")
    return problems


def check_d19_dates(repo: Repo) -> list[Finding]:
    """D19: valid dates, created <= updated, neither in the future, discussion slug date = created."""
    return [
        error("D19", item.path, "created/updated", problem, (item.slug,))
        for item in repo.items if not item.error
        for problem in _date_problems(item, repo.today)
    ]
