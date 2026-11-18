"""Shared data types and constants for the dsa-library tooling.

Single purpose: define Item, Finding, Repo and the table of link fields, so
every other module speaks the same vocabulary and none imports another's
internals.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from .config import Config

KINDS = ("concept", "problem", "discussion")
KIND_FOLDERS = {"concept": "concepts", "problem": "problems", "discussion": "discussions"}
FOLDER_KINDS = {folder: kind for kind, folder in KIND_FOLDERS.items()}
SLUG_PATTERN = r"^[a-z0-9]+(-[a-z0-9]+)*$"
SLUG_MAX_LENGTH = 80
SCHEMA_VERSION = "1.0.0"
BASE_URL = "https://fmfalgun.github.io/dsa-library/"
SEVERITY_ERROR = "error"
SEVERITY_WARNING = "warning"


@dataclass(frozen=True)
class LinkSpec:
    """One row of the spec's relation table (section 7).

    owner is the only kind allowed to store the field, targets are the kinds
    it may point to, reverse is the computed name on the target side (equal
    to the field name when the link is symmetric).
    """

    owner: str
    targets: tuple[str, ...]
    is_list: bool
    reverse: str
    symmetric: bool = False


LINK_FIELDS: dict[str, LinkSpec] = {
    "uses": LinkSpec("problem", ("concept",), True, "used_by"),
    "similar": LinkSpec("problem", ("problem",), True, "similar", symmetric=True),
    "follow_up_of": LinkSpec("problem", ("problem",), False, "follow_ups"),
    "prerequisites": LinkSpec("concept", ("concept",), True, "required_by"),
    "variant_of": LinkSpec("concept", ("concept",), False, "variants"),
    "related": LinkSpec("concept", ("concept",), True, "related", symmetric=True),
    "about": LinkSpec("discussion", KINDS, True, "discussed_in"),
}


@dataclass(frozen=True)
class Finding:
    """One validation result: which rule, how serious, where, and why.

    slugs lists the items involved (one or two) so the index can attach a
    warning to the items it concerns.
    """

    rule: str
    severity: str
    file: str
    field: str
    message: str
    slugs: tuple[str, ...] = ()

    def render(self) -> str:
        """Return the one-line form printed to the terminal."""
        where = f"{self.file} [{self.field}]" if self.field else self.file
        return f"{self.severity.upper()} {self.rule} {where}: {self.message}"


def error(rule: str, file: str, field_name: str, message: str, slugs: tuple[str, ...] = ()) -> Finding:
    """Build an error Finding; errors block commits and fail CI."""
    return Finding(rule, SEVERITY_ERROR, file, field_name, message, slugs)


def warning(rule: str, file: str, field_name: str, message: str, slugs: tuple[str, ...] = ()) -> Finding:
    """Build a warning Finding; warnings are printed and recorded only."""
    return Finding(rule, SEVERITY_WARNING, file, field_name, message, slugs)


@dataclass
class Item:
    """One content file: its place, its front matter and its body.

    data is empty and error is set when the file could not be parsed; checks
    skip such items because D3 already reports them.
    """

    folder_kind: str
    stem: str
    path: str
    data: dict
    body: str
    error: str | None = None

    @property
    def slug(self) -> str:
        """The item's ID: its filename without the extension."""
        return self.stem

    @property
    def kind(self) -> str:
        """The kind implied by the folder the file sits in."""
        return self.folder_kind

    def values(self, field_name: str) -> list[str]:
        """Return the string entries of a field, whether it holds a list or one string.

        A missing field gives an empty list; non-string entries are ignored
        because the schema check (D3) reports them.
        """
        raw = self.data.get(field_name)
        entries = raw if isinstance(raw, list) else [raw]
        return [entry for entry in entries if isinstance(entry, str)]


@dataclass
class Repo:
    """Everything the checks need: root, config, items, stray paths and 'today'."""

    root: Path
    config: Config
    items: list[Item]
    stray_paths: list[str]
    today: date
    by_slug: dict[str, Item] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Index items by slug; the first file wins so D2 can report the rest."""
        for item in self.items:
            self.by_slug.setdefault(item.slug, item)

    def resolve(self, slug: str) -> str:
        """Follow a redirect once; redirect chains are forbidden (D18)."""
        return self.config.redirects.get(slug, slug)

    def items_of(self, kind: str) -> list[Item]:
        """Return the parsed items of one kind, in path order."""
        return [item for item in self.items if item.kind == kind and not item.error]


def owned_links(item: Item) -> list[tuple[str, LinkSpec, str]]:
    """List every (field, spec, target) link the item stores on a field it may own."""
    found = []
    for name, spec in LINK_FIELDS.items():
        if spec.owner != item.kind:
            continue
        found.extend((name, spec, target) for target in item.values(name))
    return found


def misplaced_link_fields(item: Item) -> list[str]:
    """Return link fields present on an item of a kind that may not own them (D4)."""
    return [
        name for name, spec in LINK_FIELDS.items()
        if spec.owner != item.kind and name in item.data
    ]


def distinct_from_slugs(item: Item) -> list[str]:
    """Return the slugs a discussion declares itself distinct from."""
    raw = item.data.get("distinct_from")
    entries = raw if isinstance(raw, list) else []
    return [entry["slug"] for entry in entries if isinstance(entry, dict) and isinstance(entry.get("slug"), str)]
