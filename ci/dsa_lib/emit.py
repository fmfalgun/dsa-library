"""Builds the generated outputs (api/v1/*, README rule list) deterministically.

Single purpose: turn a validated Repo into the exact text of every generated
file, compare it with what is on disk (rule D16), and write it. Output is
byte-stable: sorted keys, 2-space indent, trailing newline, no timestamps.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from . import dedupe, graph
from .checks.xrefs import split_xref, xref_url
from .model import BASE_URL, KIND_FOLDERS, SCHEMA_VERSION, Finding, Item, Repo, error
from .rules import render_rules_markdown

API_DIR = "api/v1"
README_START = "<!-- rules:start -->"
README_END = "<!-- rules:end -->"

_COMMON_FIELDS = ("title", "summary", "status", "tags", "show_on", "refs", "created", "updated")
_KIND_FIELDS = {
    "concept": ("type", "aliases", "complexity"),
    "problem": ("source", "source_id", "difficulty", "found_via", "languages"),
    "discussion": ("question", "sources"),
}
_SORTED_LISTS = frozenset({"tags", "show_on", "aliases", "found_via", "languages"})
_DEFAULTS = {
    "tags": [], "show_on": [], "refs": [], "aliases": [], "found_via": [], "languages": [],
    "sources": [], "complexity": {}, "difficulty": None, "source_id": None,
}


def dumps(value: object) -> str:
    """Serialize to the repo's canonical JSON text (sorted keys, 2 spaces, final newline)."""
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def content_hash(root: Path) -> str:
    """SHA-256 over every content file and config file: path and bytes, in path order."""
    paths = sorted(
        path for folder, pattern in [(f, "*.md") for f in KIND_FOLDERS.values()] + [("config", "*.json")]
        for path in (root / folder).glob(pattern) if path.is_file()
    )
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.relative_to(root).as_posix().encode("utf-8") + b"\0" + path.read_bytes() + b"\0")
    return digest.hexdigest()


def _field_value(item: Item, name: str) -> object:
    """Return a field for the index: its value, or the documented default; scalar lists sorted."""
    value = item.data.get(name, copy.deepcopy(_DEFAULTS.get(name)))
    return sorted(value) if name in _SORTED_LISTS else value


def _item_entry(repo: Repo, item: Item, links: dict) -> dict:
    """Build one item's index entry (metadata, links, xrefs, extension keys)."""
    entry = {name: _field_value(item, name) for name in _COMMON_FIELDS + _KIND_FIELDS[item.kind]}
    entry.update(
        kind=item.kind, path=item.path, url=BASE_URL + item.path, links=links,
        extra={key: value for key, value in item.data.items() if key.startswith("x_")},
        xrefs=sorted(
            ({"ref": ref, "url": xref_url(repo, ref)} for ref in item.values("xrefs") if split_xref(ref)),
            key=lambda found: found["ref"],
        ),
    )
    if item.kind == "problem":
        entry["problem_url"] = item.data.get("url")
    if item.kind == "discussion":
        entry["topic_key"] = dedupe.topic_key(item.values("about"), repo.resolve)
    return entry


def _warning_records(findings: list[Finding]) -> list[dict]:
    """Turn offline warnings into the index's `diagnostics.warnings` records, sorted."""
    records = [
        {"rule": found.rule, "slugs": sorted(found.slugs), "message": found.message}
        for found in findings if found.severity == "warning"
    ]
    return sorted(records, key=lambda record: (record["rule"], record["slugs"], record["message"]))


def _lookups(repo: Repo) -> dict[str, dict]:
    """Build the index's aliases, topic_keys and tags lookup tables."""
    aliases: dict[str, str] = {}
    topics: dict[str, list[str]] = {}
    tags: dict[str, list[str]] = {}
    for item in repo.items_of("concept"):
        aliases.update({alias.strip().lower(): item.slug for alias in item.values("aliases")})
    for item in repo.items_of("discussion"):
        topics.setdefault(dedupe.topic_key(item.values("about"), repo.resolve), []).append(item.slug)
    for item in repo.items:
        for tag in item.values("tags"):
            tags.setdefault(tag, []).append(item.slug)
    return {
        "aliases": aliases,
        "topic_keys": {key: sorted(slugs) for key, slugs in topics.items()},
        "tags": {key: sorted(slugs) for key, slugs in tags.items()},
    }


def build_index(repo: Repo, findings: list[Finding]) -> dict:
    """Build the full index.json object from a validated Repo and its offline findings."""
    links = graph.compute_links(repo)
    items = {item.slug: _item_entry(repo, item, links[item.slug]) for item in repo.items if not item.error}
    counts = {f"{kind}s": len(repo.items_of(kind)) for kind in KIND_FOLDERS}
    return {
        "schema_version": SCHEMA_VERSION,
        "content_hash": content_hash(repo.root),
        "counts": counts,
        "items": items,
        "redirects": dict(repo.config.redirects),
        "diagnostics": {"warnings": _warning_records(findings)},
        **_lookups(repo),
    }


def build_search(repo: Repo) -> list[dict]:
    """Build search.json: one slim record per item, sorted by slug."""
    keys = ("title", "summary", "aliases", "tags", "status", "show_on")
    slim = []
    for item in sorted(repo.items, key=lambda found: found.slug):
        record = {"slug": item.slug, "kind": item.kind, "path": item.path}
        record.update({key: _field_value(item, key) for key in keys})
        slim.append(record)
    return slim


def readme_with_rules(readme_text: str) -> str | None:
    """Return the README with its rule list regenerated, or None when the markers are missing."""
    start, end = readme_text.find(README_START), readme_text.find(README_END)
    if start == -1 or end == -1 or end < start:
        return None
    head = readme_text[:start + len(README_START)]
    return f"{head}\n{render_rules_markdown()}\n{readme_text[end:]}"


def build_outputs(repo: Repo, findings: list[Finding]) -> dict[str, str]:
    """Return {relative path: exact text} for every generated file.

    The README is included only when it exists and has the rule markers;
    stale_findings reports a README without them.
    """
    outputs = {
        f"{API_DIR}/index.json": dumps(build_index(repo, findings)),
        f"{API_DIR}/search.json": dumps(build_search(repo)),
    }
    for schema_file in sorted((repo.root / "schema").glob("*.schema.json")):
        outputs[f"{API_DIR}/schema/{schema_file.name}"] = schema_file.read_text(encoding="utf-8")
    readme = repo.root / "README.md"
    updated = readme_with_rules(readme.read_text(encoding="utf-8")) if readme.is_file() else None
    if updated is not None:
        outputs["README.md"] = updated
    return outputs


def _on_disk(root: Path, relative: str) -> str | None:
    """Read a generated file's current text, or None when it does not exist."""
    path = root / relative
    return path.read_text(encoding="utf-8") if path.is_file() else None


def stale_findings(repo: Repo, outputs: dict[str, str]) -> list[Finding]:
    """D16: report every generated file that is missing, different, or not expected."""
    findings = [
        error("D16", relative, "", "generated file is missing or out of date; run python ci/sync_index.py")
        for relative, text in sorted(outputs.items()) if _on_disk(repo.root, relative) != text
    ]
    if "README.md" not in outputs:
        findings.append(error("D16", "README.md", "", f"README.md must exist and contain {README_START} and {README_END}"))
    api_root = repo.root / API_DIR
    for path in sorted(api_root.rglob("*")) if api_root.is_dir() else []:
        relative = path.relative_to(repo.root).as_posix()
        if path.is_file() and relative not in outputs:
            findings.append(error("D16", relative, "", "unexpected file in api/v1 (generated folder)"))
    return findings


def write_outputs(root: Path, outputs: dict[str, str]) -> None:
    """Write every output and delete unexpected files in api/v1.

    Side effects: creates folders, rewrites files, unlinks leftovers in the
    generated folder only. Raises OSError on I/O failure.
    """
    for relative, text in outputs.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    api_root = root / API_DIR
    for path in sorted(api_root.rglob("*")) if api_root.is_dir() else []:
        if path.is_file() and path.relative_to(root).as_posix() not in outputs:
            path.unlink()
