"""Validates each item's front matter against its JSON Schema (rule D3).

Single purpose: load schema/*.schema.json and turn schema violations and
parse failures into D3 findings.
"""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from .model import KINDS, Finding, Item, Repo, error, misplaced_link_fields


def load_validators(root: Path) -> dict[str, Draft202012Validator]:
    """Load one validator per kind from <root>/schema.

    Raises OSError or json.JSONDecodeError when a schema file is missing or
    broken: that is a repo defect, not a content error, so it stops the run.
    """
    validators = {}
    for kind in KINDS:
        document = json.loads((root / "schema" / f"{kind}.schema.json").read_text(encoding="utf-8"))
        validators[kind] = Draft202012Validator(document)
    return validators


def _field_label(violation) -> str:
    """Name the offending field: its dotted path, or '(front matter)' at the top level."""
    return ".".join(str(part) for part in violation.absolute_path) or "(front matter)"


def _validate_item(item: Item, validator: Draft202012Validator) -> list[Finding]:
    """Return D3 findings for one parsed item.

    Link fields on the wrong kind are removed first: D4 reports those, and
    reporting them here too would give one mistake two rule IDs.
    """
    data = {key: value for key, value in item.data.items() if key not in misplaced_link_fields(item)}
    violations = sorted(validator.iter_errors(data), key=lambda found: list(map(str, found.absolute_path)))
    return [error("D3", item.path, _field_label(found), found.message, (item.slug,)) for found in violations]


def check_d03_schema(repo: Repo) -> list[Finding]:
    """D3: front matter parses and passes the schema for the folder's kind."""
    validators = load_validators(repo.root)
    findings: list[Finding] = []
    for item in repo.items:
        if item.error:
            findings.append(error("D3", item.path, "", item.error, (item.slug,)))
        else:
            findings.extend(_validate_item(item, validators[item.kind]))
    return findings
