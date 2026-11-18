"""One failing fixture per rule D1-D20, caught with the right rule ID.

Single purpose: prove each rule fires on its fixture and that the valid
fixture passes clean. D20 has its own tests in test_hygiene.py because its
fixtures (secrets, big files) must be built at run time, never committed.
"""

from __future__ import annotations

import pytest

from conftest import all_findings, make_repo, rule_ids
from dsa_lib.rules import RULES

# (fixture folder, expected rule, expected severity)
CASES = [
    ("structure/d01", "D1", "error"),
    ("structure/d02", "D2", "error"),
    ("structure/d03", "D3", "error"),
    ("structure/d04", "D4", "error"),
    ("links/d05", "D5", "error"),
    ("links/d06", "D6", "error"),
    ("links/d07", "D7", "error"),
    ("structure/d08", "D8", "error"),
    ("structure/d09", "D9", "error"),
    ("links/d10", "D10", "error"),
    ("links/d11", "D11", "error"),
    ("links/d12", "D12", "warning"),
    ("links/d13", "D13", "warning"),
    ("structure/d14", "D14", "error"),
    ("policy/d15", "D15", "error"),
    ("policy/d16", "D16", "error"),
    ("policy/d17", "D17", "error"),
    ("policy/d18", "D18", "error"),
    ("policy/d19", "D19", "error"),
]
RULES_TESTED_ELSEWHERE = {"D20"}


@pytest.mark.parametrize("fixture,rule,severity", CASES, ids=[case[0] for case in CASES])
def test_fixture_triggers_its_rule(tmp_path, fixture, rule, severity):
    """Each fixture, laid over the valid repo, produces its rule at the expected severity."""
    root = make_repo(tmp_path, fixture, generate_first=(rule == "D16"))
    findings = all_findings(root, include_stale=(rule == "D16"))
    assert rule in rule_ids(findings, severity), [found.render() for found in findings]


def test_every_rule_has_a_fixture_or_a_named_test():
    """No rule in the table lacks coverage: fixtures here, or D20 in test_hygiene.py."""
    covered = {case[1] for case in CASES} | RULES_TESTED_ELSEWHERE
    assert covered == {rule.rule_id for rule in RULES}


def test_valid_fixture_has_no_findings(tmp_path):
    """The valid fixture passes every rule with no errors and no warnings."""
    findings = all_findings(make_repo(tmp_path))
    assert findings == [], [found.render() for found in findings]


def test_d05_reports_missing_and_wrong_kind(tmp_path):
    """A missing target and a target of the wrong kind are two separate D5 errors."""
    findings = all_findings(make_repo(tmp_path, "links/d05"))
    messages = " | ".join(found.message for found in findings if found.rule == "D5")
    assert "no-such-concept" in messages and "needs concept" in messages


def test_d06_reports_self_link_and_cycle(tmp_path):
    """The d06 fixture has a self-link and a two-file prerequisites cycle."""
    findings = all_findings(make_repo(tmp_path, "links/d06"))
    messages = " | ".join(found.message for found in findings if found.rule == "D6")
    assert "link to itself" in messages and "cycle:" in messages


def test_d09_reports_wrong_prefix_and_duplicate_id(tmp_path):
    """A slug prefix that disagrees with source_id, and a repeated (source, id) pair, both fail D9."""
    findings = all_findings(make_repo(tmp_path, "structure/d09"))
    messages = " | ".join(found.message for found in findings if found.rule == "D9")
    assert "slug must start with" in messages and "already stored as" in messages


def test_d11_passes_when_distinct_from_has_a_reason(tmp_path):
    """Spec acceptance: the same about-set fails D11, and distinct_from with a reason makes it pass."""
    failing = all_findings(make_repo(tmp_path / "a", "links/d11"))
    passing = all_findings(make_repo(tmp_path / "b", "links/d11_distinct"))
    assert "D11" in rule_ids(failing)
    assert "D11" not in rule_ids(passing) and rule_ids(passing, "error") == set()


def test_d05_redirect_resolves_with_a_warning_only(tmp_path):
    """Spec acceptance: a link to a renamed slug keeps resolving and only warns."""
    findings = all_findings(make_repo(tmp_path, "links/d05_redirect"))
    assert rule_ids(findings, "error") == set()
    assert "D5" in rule_ids(findings, "warning")
