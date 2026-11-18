"""D20 (secrets, file size) and the pre-commit hook's secret blocking.

Single purpose: prove secrets and oversized files are refused. Fake secrets
are assembled at run time so no secret-looking text is ever committed.
"""

from __future__ import annotations

import os
import shutil
import subprocess

from conftest import REPO_ROOT, all_findings, make_repo, rule_ids

FAKE_KEY_LINE = "api_key = " + '"' + "abcd1234" * 3 + '"\n'


def test_d20_flags_a_secret_in_content(tmp_path):
    """A secret-looking assignment inside a content file is a D20 error."""
    root = make_repo(tmp_path)
    (root / "concepts" / "arrays.md").write_text(
        (root / "concepts" / "arrays.md").read_text(encoding="utf-8") + "\n" + FAKE_KEY_LINE, encoding="utf-8")
    assert "D20" in rule_ids(all_findings(root), "error")


def test_d20_flags_a_private_key_header_in_docs(tmp_path):
    """A PEM private-key header in docs/ is a D20 error."""
    root = make_repo(tmp_path)
    (root / "docs").mkdir()
    (root / "docs" / "leak.md").write_text("-----BEGIN " + "RSA PRIVATE KEY-----\n", encoding="utf-8")
    assert "D20" in rule_ids(all_findings(root), "error")


def test_d20_flags_a_file_over_one_megabyte(tmp_path):
    """A content-folder file larger than 1 MB is a D20 error."""
    root = make_repo(tmp_path)
    (root / "solutions" / "big").mkdir(parents=True)
    (root / "solutions" / "big" / "data.txt").write_bytes(b"x" * 1_000_001)
    assert "D20" in rule_ids(all_findings(root), "error")


def _git(repo, *args: str) -> subprocess.CompletedProcess:
    """Run git in `repo` with a throwaway identity and no signing; capture output."""
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid"}
    return subprocess.run(["git", "-c", "commit.gpgsign=false", *args], cwd=repo, env=env,
                          capture_output=True, text=True, check=False)


def _hooked_repo(tmp_path, with_gitignore: bool = True):
    """Create a git repo holding the real hook and tooling plus the valid fixture, hook installed.

    with_gitignore=False omits .gitignore so a key-named file can be staged
    without a forbidden add flag; the hook's name check is what is under test.
    """
    root = make_repo(tmp_path)
    shutil.copytree(REPO_ROOT / "ci", root / "ci", ignore=shutil.ignore_patterns("__pycache__"))
    if with_gitignore:
        shutil.copy(REPO_ROOT / ".gitignore", root / ".gitignore")
    (root / ".venv").symlink_to(REPO_ROOT / ".venv")
    _git(root, "init", "-b", "main")
    _git(root, "config", "core.hooksPath", "ci/hooks")
    return root


def test_hook_accepts_clean_content_and_blocks_a_leaked_key(tmp_path):
    """Spec acceptance: the hook lets a clean commit through and blocks a file with a fake key."""
    root = _hooked_repo(tmp_path)
    _git(root, "add", "-A")
    assert _git(root, "commit", "-m", "clean").returncode == 0
    (root / "docs").mkdir()
    (root / "docs" / "leak.md").write_text(FAKE_KEY_LINE, encoding="utf-8")
    _git(root, "add", "-A")
    blocked = _git(root, "commit", "-m", "leak")
    assert blocked.returncode != 0 and "blocked" in blocked.stderr


def test_hook_refuses_a_key_file_by_name(tmp_path):
    """The hook refuses a staged file named like a private key, whatever it contains."""
    root = _hooked_repo(tmp_path, with_gitignore=False)
    (root / "deploy.pem").write_text("not really a key\n", encoding="utf-8")
    _git(root, "add", "-A", "--", "deploy.pem")
    refused = _git(root, "commit", "-m", "key")
    assert refused.returncode != 0 and "key or env file name" in refused.stderr
