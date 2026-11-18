"""Duplicate-detection helpers for discussions (spec section 8).

Single purpose: pure functions that compute topic keys and the similarity
measures behind rules D11, D12 and D13. No I/O, no Repo access.
"""

from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Callable, Iterable

JACCARD_THRESHOLD = 0.75
TEXT_THRESHOLD = 0.85


def link_set(about: Iterable[str], resolve: Callable[[str], str]) -> frozenset[str]:
    """Return the distinct `about` slugs after following redirects."""
    return frozenset(resolve(slug) for slug in about)


def topic_key(about: Iterable[str], resolve: Callable[[str], str]) -> str:
    """Return the order-independent topic key: resolved, de-duplicated, sorted, joined with '|'."""
    return "|".join(sorted(link_set(about, resolve)))


def is_strict_subset(first: frozenset[str], second: frozenset[str]) -> bool:
    """True when every link of `first` is in `second` and `second` has more."""
    return first < second


def jaccard(first: frozenset[str], second: frozenset[str]) -> float:
    """Shared links divided by all links; 0.0 when both sets are empty."""
    union = first | second
    return len(first & second) / len(union) if union else 0.0


def normalize_text(text: str) -> str:
    """Lowercase, drop punctuation and collapse whitespace, as section 8 prescribes."""
    without_punctuation = re.sub(r"[^\w\s]", "", text.lower())
    return " ".join(without_punctuation.split())


def text_similarity(first: str, second: str) -> float:
    """difflib similarity ratio (0..1) of two normalized strings."""
    return SequenceMatcher(None, normalize_text(first), normalize_text(second)).ratio()
