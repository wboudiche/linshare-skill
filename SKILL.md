---
name: cli-anything-linshare
description: Share documents through LinShare - send files to people by email (inside or outside the organisation), list or revoke what was shared, list and download files received, and ask people to send files. Use when the user asks to share, send, transfer or receive a file "via LinShare", or to check or cancel a LinShare share.
---

# cli-anything-linshare

`linshare` is a command-line tool for a LinShare server (version 6.5 or later).
Use it to share the user's documents safely.

## Installation

```bash
pip install "git+<linshare-cli repository URL>#subdirectory=agent-harness"   # or: pip install -e agent-harness
```

Requires Python 3.10+ and a LinShare account on a 6.5+ server.

## Rules — follow them every time

1. **Always pass `--json`** right after `linshare` (`linshare --json shares list`) and read the JSON.
2. **Login is done by the user, never by you.** If a command fails with exit code 2
   (`"code": "auth"`), ask the user to type `! linshare login` themselves
   (`! linshare login --token` if they sign in with SSO and have a token from the web UI).
   Never ask for or type their password.
3. **Get an explicit "yes" before anything leaves the account or is destroyed.**
   This covers `share`, `request-files`, `shares revoke`, `documents delete`, `requests close`.
   - For `share` and `request-files`: run the same command with `--dry-run` first,
     then show the user, in plain words:
     the files (name and size), every recipient — marking `"external": true` ones
     as **outside your organisation** — the expiry date, subject, message,
     and whether a password-protected link is used.
   - For `revoke`, `delete`, `close`: list first, then show exactly which items will be affected.
   - Use only the words the user gave for `--subject` and `--message`. Don't write one
     yourself; leave them out, or suggest one and add it only if the user says so.
     A `--label` for `request-files` may be a short name taken from the user's own words
     ("October invoice"); without one the tool picks "Files for <your email>".
   - `request-files` needs a `--message` (LinShare refuses a request without one). If the
     user gave none, ask them for the text before the dry run; you may propose a wording,
     but use it only once they accept it.
   - No expiry given (`"expirationDate": null`) means the server's default expiry, not "never".
   - Wait for an explicit yes. If the user changes anything (a recipient, the expiry, a file),
     run a new `--dry-run` and ask again. Never reuse an earlier yes.
   - In the real run, pass the dry-run's `expirationDate` as `--expires YYYY-MM-DD`
     (the exact date the user approved), never a relative value like `7d` again.
4. **Check the server, not your memory.** Before telling the user whether something was
   shared, sent, revoked or closed, run the matching list command (`shares list`,
   `requests list`, `documents list`). Notes from earlier conversations can be out of date.
5. **No confirmation is needed for read-only commands:** `whoami`, `shares list`,
   `received list`, `received download`, `documents list`, `requests list`, `requests download`.
6. **After sharing**, tell the user which files went to whom and until when.
7. **On errors** relay `error.message` in plain words. Don't retry a refused share with
   different settings without asking. Exit 1 means the command itself was wrong (fix it,
   don't ask the user to log in). When a share fails the tool removes the uploaded files and
   says so; if `error.code` is `"timeout"` the outcome is unknown — follow the message
   (check `shares list` / `documents list`) before any retry.

## Typical flow

```bash
linshare --json share ./contract.pdf --to marc@acme.com --expires 7d --message "Please sign" --dry-run
# → show the summary to the user, wait for "yes"
# dry-run said "expirationDate": "2026-11-13"
linshare --json share ./contract.pdf --to marc@acme.com --expires 2026-11-13 --message "Please sign"
```

## Commands

| Command | What it does | Confirm first? |
|---|---|---|
| `linshare login [--server URL] [--email E]` | user logs in once (password, 2FA code if needed) | user runs it |
| `linshare login --token [--server URL]` | user pastes a token made in the LinShare web UI | user runs it |
| `linshare logout` | forgets (and revokes) the token | no |
| `linshare whoami` | server and account in use | no |
| `linshare share FILE... --to EMAIL... [--expires 7d\|2w\|1m\|YYYY-MM-DD] [--subject S] [--message M] [--password-link] [--dry-run]` | upload and share by email | **yes** |
| `linshare shares list` | what the user shared | no |
| `linshare shares revoke ID...` | cancel shares | **yes** |
| `linshare received list` | what others shared with the user | no |
| `linshare received download ID [--out DIR]` | save a received file (never overwrites) | no |
| `linshare documents list` | the user's documents | no |
| `linshare documents delete ID...` | delete documents | **yes** |
| `linshare request-files --from EMAIL... --message M [--label L] [--expires ...] [--dry-run]` | ask people to send files (one private request each) | **yes** |
| `linshare requests list` | upload requests and files received | no |
| `linshare requests download ID [--out DIR]` | download received files as a zip | no |
| `linshare requests close ID...` | close requests | **yes** |

`--to` and `--from` are repeated for several people: `--to a@x.org --to b@y.org`.
"External" is a heuristic: a different email domain than the user's.

## Exit codes

0 ok · 1 bad input or wrong command · 2 not logged in / login problem · 3 server refused · 4 server unreachable, failing or too slow (`"code": "timeout"`).
