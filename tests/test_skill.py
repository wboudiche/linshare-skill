"""The skill must only mention commands and options that the installed `linshare` has,
and must keep its safety rules."""

import re
import shutil
import subprocess
from pathlib import Path

import pytest

SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"
TEXT = SKILL.read_text(encoding="utf-8")
LINSHARE = shutil.which("linshare")
needs_cli = pytest.mark.skipif(not LINSHARE, reason="`linshare` is not installed")


def help_text(words: tuple[str, ...]) -> str:
    proc = subprocess.run([LINSHARE, *words, "--help"], capture_output=True, text=True, timeout=30)
    assert proc.returncode == 0, f"`linshare {' '.join(words)}` does not exist:\n{proc.stdout}{proc.stderr}"
    return proc.stdout


def snippets() -> list[str]:
    """Every `linshare ...` the skill writes: inline code spans and lines of code blocks."""
    spans = re.findall(r"`(?:! )?(linshare[^`]*)`", TEXT)
    blocks = "\n".join(re.findall(r"```bash\n(.*?)```", TEXT, re.S))
    lines = [line.split("#")[0].strip() for line in blocks.splitlines()]
    return spans + [line for line in lines if line.startswith("linshare")]


def mentioned_commands() -> dict[tuple[str, ...], set[str]]:
    """Command words → the options used with them anywhere in the skill."""
    found: dict[tuple[str, ...], set[str]] = {}
    for snippet in snippets():
        words = []
        for t in snippet.split()[1:]:
            if t == "--json":
                continue
            if not re.fullmatch(r"[a-z][a-z-]*", t):
                break
            words.append(t)
        if not words:
            continue
        options = {o for o in re.findall(r"--[a-z][a-z-]*", snippet) if o != "--json"}
        found.setdefault(tuple(words), set()).update(options)
    return found


def test_frontmatter():
    assert TEXT.startswith("---\nname: cli-anything-linshare\ndescription: ")


@pytest.mark.parametrize("needle", ["--dry-run", "linshare login", "explicit", "--json", "Never ask for or type their password"])
def test_safety_rules_are_there(needle):
    assert needle in TEXT


def test_reuses_the_dry_run_exact_dates():
    assert "expirationDate" in TEXT and "exact date" in TEXT
    assert "alertIfNotDownloaded" in TEXT


def test_finds_the_commands_it_should():
    cmds = mentioned_commands()
    for words in [("share",), ("shares", "list"), ("shares", "revoke"), ("received", "download"),
                  ("request-files",), ("requests", "close"), ("documents", "delete"), ("login",),
                  ("spaces", "list"), ("spaces", "files"), ("spaces", "upload"), ("spaces", "download"),
                  ("spaces", "add-member"), ("spaces", "remove-member"), ("spaces", "delete")]:
        assert words in cmds, words


@needs_cli
@pytest.mark.parametrize("words", sorted(mentioned_commands()), ids=" ".join)
def test_command_and_options_exist(words):
    text = help_text(words)
    missing = [o for o in sorted(mentioned_commands()[words]) if o not in text]
    assert not missing, f"`linshare {' '.join(words)}` has no {missing}"
