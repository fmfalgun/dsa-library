"""Reads content files (Markdown + YAML front matter) into a Repo.

Single purpose: turn the three content folders into Item objects, recording
anything that is not a clean `<slug>.md` as a stray path instead of guessing.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import yaml

from .config import load_config
from .model import FOLDER_KINDS, Item, Repo

_FENCE = "---"


class _TextDatesLoader(yaml.SafeLoader):
    """A YAML loader that keeps `2026-11-18` as text instead of a date object.

    The schema and the date rule (D19) both want strings, so the implicit
    timestamp resolver is removed from this loader only.
    """


_TextDatesLoader.yaml_implicit_resolvers = {
    first_char: [(tag, regex) for tag, regex in resolvers if tag != "tag:yaml.org,2002:timestamp"]
    for first_char, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


class FrontMatterError(ValueError):
    """Raised when a file has no usable front matter block."""


def split_front_matter(text: str) -> tuple[str, str]:
    """Split a document into (front-matter YAML text, Markdown body).

    The block must start on the first line with `---` and end at the next
    line that is exactly `---`. Raises FrontMatterError otherwise.
    """
    lines = text.lstrip("﻿").splitlines(keepends=True)
    if not lines or lines[0].strip() != _FENCE:
        raise FrontMatterError("file must start with a '---' front matter line")
    for index in range(1, len(lines)):
        if lines[index].strip() == _FENCE:
            return "".join(lines[1:index]), "".join(lines[index + 1:])
    raise FrontMatterError("front matter is not closed by a second '---' line")


def _load_yaml_mapping(yaml_text: str) -> dict:
    """Parse YAML text that must be a mapping; raises FrontMatterError otherwise."""
    try:
        data = yaml.load(yaml_text, Loader=_TextDatesLoader)  # noqa: S506 - SafeLoader subclass
    except yaml.YAMLError as problem:
        raise FrontMatterError(f"front matter is not valid YAML ({problem})") from problem
    if not isinstance(data, dict):
        raise FrontMatterError("front matter must be a key: value mapping")
    return data


def parse_item(root: Path, path: Path, kind: str) -> Item:
    """Read one content file into an Item.

    Never raises for bad content: the problem is stored in Item.error so the
    checker can report it as D3 and carry on with the other files.
    """
    relative = path.relative_to(root).as_posix()
    try:
        text = path.read_text(encoding="utf-8")
        yaml_text, body = split_front_matter(text)
        return Item(kind, path.stem, relative, _load_yaml_mapping(yaml_text), body)
    except (OSError, UnicodeDecodeError, FrontMatterError) as problem:
        return Item(kind, path.stem, relative, {}, "", error=str(problem))


def discover(root: Path) -> tuple[list[Item], list[str]]:
    """Find every content item; return (items, stray paths).

    A stray path is anything in a content folder that is not a plain
    `<name>.md` file (a subfolder, another extension): D1 reports them.
    """
    items: list[Item] = []
    strays: list[str] = []
    for folder, kind in FOLDER_KINDS.items():
        directory = root / folder
        if not directory.is_dir():
            continue
        for path in sorted(directory.iterdir()):
            if path.is_file() and path.suffix == ".md":
                items.append(parse_item(root, path, kind))
            else:
                strays.append(path.relative_to(root).as_posix())
    return items, strays


def load_repo(root: Path, today=None) -> Repo:
    """Load config and content from `root` into a Repo.

    `today` defaults to the current UTC date; tests pass a fixed date.
    Raises ConfigError when config/ is broken.
    """
    items, strays = discover(root)
    current_day = today or datetime.now(timezone.utc).date()
    return Repo(root, load_config(root), items, strays, current_day)
