# linshare-skill

An agent skill that lets an AI assistant (Claude Code and other tools that read
`SKILL.md` skills) share documents through LinShare: send files by email, list or
revoke shares, download received files, and ask people to send files. The assistant
shows a dry-run summary and waits for an explicit "yes" before anything is sent,
revoked, deleted or closed.

The skill drives the `linshare` command from the **linshare-cli** repository, which
must be installed first (Python 3.10+, LinShare 6.5 or later).

## Install

```bash
# 1. the command
pip install "git+<linshare-cli repository URL>#subdirectory=agent-harness"

# 2. the skill, for Claude Code
git clone <linshare-skill repository URL> ~/linshare-skill
ln -s ~/linshare-skill ~/.claude/skills/cli-anything-linshare
```

Then the user logs in once, themselves: `linshare login --server https://linshare.example.com`.
The assistant never asks for or types the password.

## Use

Ask in plain words, for example:

- "Share contract.pdf with marc@acme.com via LinShare for a week"
- "Has Marc downloaded it?"
- "Ask ann@acme.com to send me the scans via LinShare"
- "Cancel what I shared with Marc"

Before sharing, asking for files, revoking, deleting or closing, the assistant
shows what will happen (files, recipients — flagging those outside your
organisation — expiry, message, download alert) and waits for your "yes".
It only uses a subject or message you gave it.

## Test

`tests/test_skill.py` checks that every command and option the skill mentions exists
in the installed `linshare` (so the skill and the command don't drift apart), and that
the safety rules are still there:

```bash
pip install pytest
pytest -q tests
```

The tests are skipped if `linshare` is not installed.

## Compatibility

Written for linshare-cli as of 2026-11-08 (`share --alert-if-not-downloaded`,
`--send-me-a-copy`, `request-files --message`). Run the tests after updating either side.
