"""Cross-repo reference rule D17: xrefs use a registered alias (offline) and exist (online).

Single purpose: validate `<alias>:<path>` references to other repos. Offline
problems are errors; online problems are only warnings, so a change in
another repo never blocks a commit here (spec coupling rule 3).
"""

from __future__ import annotations

import json
import urllib.request
from typing import Callable

from ..model import Finding, Item, Repo, error, warning

# A fetcher takes a URL and returns the parsed JSON, or raises OSError/ValueError.
Fetcher = Callable[[str], object]


def split_xref(reference: str) -> tuple[str, str] | None:
    """Split `<alias>:<path>`; return None when the shape is wrong."""
    alias, separator, path = reference.partition(":")
    return (alias, path) if separator and alias and path else None


def xref_url(repo: Repo, reference: str) -> str | None:
    """Return the published URL of a registered reference, or None when it cannot be resolved."""
    parts = split_xref(reference)
    entry = repo.config.repos.get(parts[0]) if parts else None
    return f"{entry.base_url}data/{parts[1]}.json" if entry and parts else None


def check_d17_offline(repo: Repo) -> list[Finding]:
    """D17 (offline): each xref has the `<alias>:<path>` shape and a registered alias."""
    findings = []
    for item in repo.items:
        for reference in item.values("xrefs"):
            parts = split_xref(reference)
            if parts is None:
                findings.append(error("D17", item.path, "xrefs", f"'{reference}' must look like <alias>:<path>", (item.slug,)))
            elif parts[0] not in repo.config.repos:
                findings.append(error("D17", item.path, "xrefs", f"alias '{parts[0]}' is not in config/repos.json", (item.slug,)))
    return findings


def _manifest_finding(repo: Repo, item: Item, reference: str, fetch: Fetcher) -> Finding | None:
    """Warn when the manifest of the referenced folder cannot be read or lacks the record."""
    parts = split_xref(reference)
    entry = repo.config.repos.get(parts[0]) if parts else None
    if entry is None or entry.exists_check != "manifest" or "/" not in parts[1]:
        return None
    folder, name = parts[1].split("/", 1)
    url = f"{entry.base_url}data/{folder}/manifest.json"
    try:
        manifest = fetch(url)
    except (OSError, ValueError) as problem:
        return warning("D17", item.path, "xrefs", f"could not check '{reference}': {url} unreachable ({problem})", (item.slug,))
    if not isinstance(manifest, list) or f"{name}.json" not in manifest:
        return warning("D17", item.path, "xrefs", f"'{reference}' was not found in {url}", (item.slug,))
    return None


def check_d17_online(repo: Repo, fetch: Fetcher) -> list[Finding]:
    """D17 (online): warn about xrefs whose target is missing or whose repo is unreachable."""
    findings = []
    for item in repo.items:
        for reference in item.values("xrefs"):
            finding = _manifest_finding(repo, item, reference, fetch)
            if finding:
                findings.append(finding)
    return findings


def fetch_json(url: str, timeout_seconds: int = 10) -> object:
    """Fetch a URL and parse it as JSON.

    Used only for `--online`. Raises OSError (network problems, HTTP errors)
    or ValueError (not JSON); callers turn both into warnings.
    """
    with urllib.request.urlopen(url, timeout=timeout_seconds) as response:  # noqa: S310 - fixed https base URLs from config
        return json.loads(response.read().decode("utf-8"))
