---
name: linshare
description: Share documents through LinShare - send files to people by email (inside or outside the organisation), list or revoke what was shared, list and download files received, ask people to send files, and work with team workgroups and workspaces (browse, upload, download, manage members). Use when the user asks to share, send, transfer or receive a file "via LinShare", to check or cancel a LinShare share, or about a LinShare workgroup, workspace or shared space.
---

# LinShare

`linshare` is a command-line tool for a LinShare server (version 6.5 or later).
Use it to share the user's documents safely.

## First, check the setup

Before the first LinShare command of a conversation, run `linshare --json whoami`:

- **command not found** (exit 127): the `linshare` command is not installed. Tell the user,
  in plain words, that this skill needs it and that they can install it themselves with
  `pip install "git+https://github.com/wboudiche/linshare-cli#subdirectory=agent-harness"` (Python 3.10+).
  Don't install it yourself.
- **exit 2** (`"code": "auth"`): not logged in. Ask the user to type, in this chat,
  `! linshare login --server <address of their LinShare>` (ask for the address if you
  don't know it) — they type their password there, never in the conversation.
  With SSO: `! linshare login --token --server <address>`, pasting a token from the web UI.
- **exit 0**: it shows the server and the account; go on with the request.

## Rules — follow them every time

1. **Always pass `--json`** right after `linshare` (`linshare --json shares list`) and read the JSON.
2. **Login is done by the user, never by you.** If a command fails with exit code 2
   (`"code": "auth"`), ask the user to type `! linshare login` themselves
   (`! linshare login --token` if they sign in with SSO and have a token from the web UI).
   Never ask for or type their password.
3. **Get an explicit "yes" before anything leaves the account or is destroyed.**
   This covers `share`, `request-files`, `shares revoke`, `documents delete`, `requests close`,
   and for shared spaces `spaces upload`, `spaces add-member`, `spaces set-role`,
   `spaces remove-member`, `spaces delete-files`, `spaces delete`.
   - For `share` and `request-files`: run the same command with `--dry-run` first,
     then show the user, in plain words:
     the files (name and size), every recipient — marking `"external": true` ones
     as **outside your organisation** — the expiry date, subject, message,
     whether a password-protected link is used, and `downloadAlert` / `copyToMe`
     (what the server will really do: the administrator's settings can override the user's choice;
     say so when `detail` says so).
   - For `revoke`, `delete`, `close`: list first, then show exactly which items will be affected.
   - For `spaces upload` and `spaces add-member`: run with `--dry-run` first. For an upload, show
     the files, the workgroup (and folder) and `visibleTo` — everyone in it will see the files
     (if `visibleTo` is null, say the members could not be listed). For a new member, show the
     person (name and email), the space and the role, in plain words (READER: read only,
     CONTRIBUTOR: can add, WRITER: can add and change, ADMIN: also manages members).
   - `spaces delete` removes the space and all its files **for every member**; `spaces delete-files`
     removes them for everyone too. Say so, naming the space and the items.
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
     (the exact date the user approved), never a relative value like `7d` again;
     same for `--alert-if-not-downloaded` (the dry-run's `alertIfNotDownloaded`).
4. **Check the server, not your memory.** Before telling the user whether something was
   shared, sent, revoked or closed, run the matching list command (`shares list`,
   `requests list`, `documents list`, `spaces files`, `spaces members`). Notes from earlier
   conversations can be out of date.
5. **No confirmation is needed for read-only commands:** `whoami`, `shares list`,
   `received list`, `received download`, `documents list`, `requests list`, `requests download`,
   `spaces list`, `spaces files`, `spaces members`, `spaces download`. Creating an empty
   workgroup or folder (`spaces create`, `spaces mkdir`) needs no confirmation either: nobody
   else sees it until files or members are added.
6. **After sharing**, tell the user which files went to whom and until when.
   **Downloads:** LinShare emails the sender the first time each recipient downloads a share,
   and `shares list` shows a `downloaded` count — use it to answer "has X downloaded it?".
   To be warned when a file is *not* downloaded, use `--alert-if-not-downloaded`
   (a date, a delay like `3d`, or `off`; without it the server's default applies).
7. **Shared spaces.** A *workgroup* holds files a team shares; a *workspace* groups workgroups.
   Commands take ids: run `spaces list` to find the space, `spaces files SPACE [--folder ID]` to
   find a folder or file. Several spaces can have the same name: if the user's words match more
   than one, ask which. Sharing a file *by email* (`share`) and putting it in a workgroup
   (`spaces upload`) are different: ask if unclear.
   On LinShare 7.0 some things fail because of server bugs: `spaces members` cannot list members
   (use the member id printed by `add-member` for `set-role` / `remove-member`), and people cannot
   be added to a *workspace* (only to its workgroups). Relay the message; don't retry in other ways.
8. **On errors** relay `error.message` in plain words. Don't retry a refused share with
   different settings without asking. Exit 1 means the command itself was wrong (fix it,
   don't ask the user to log in). When a share fails the tool removes the uploaded files and
   says so; if `error.code` is `"timeout"` the outcome is unknown — follow the message
   (check `shares list` / `documents list`) before any retry.
9. **Large files** are fine: above 2 MiB the tool sends them in chunks, like the web UI.
   Uploading takes about 15 s per GB on a fast network, much more on a slow one. For a file
   over a few hundred MB, give the `share` command a long timeout (or run it in the
   background) so it is not cut off, and tell the user it may take a while.

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
| `linshare share FILE... --to EMAIL... [--expires 7d\|2w\|1m\|YYYY-MM-DD] [--subject S] [--message M] [--password-link] [--alert-if-not-downloaded WHEN] [--send-me-a-copy] [--dry-run]` | upload and share by email | **yes** |
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
| `linshare spaces list [--in WORKSPACE]` | workgroups and workspaces, with your role | no |
| `linshare spaces create NAME [--workspace] [--in WORKSPACE]` | create a workgroup (or workspace) | no |
| `linshare spaces delete ID...` | delete spaces and all their files, for everyone | **yes** |
| `linshare spaces files SPACE [--folder ID]` | folders and files of a workgroup | no |
| `linshare spaces mkdir SPACE NAME [--folder ID]` | create a folder | no |
| `linshare spaces upload SPACE FILE... [--folder ID] [--dry-run]` | put files in a workgroup (members see them) | **yes** |
| `linshare spaces download SPACE ID [--out DIR]` | save a workgroup file (never overwrites) | no |
| `linshare spaces delete-files SPACE ID...` | delete files or folders, for everyone | **yes** |
| `linshare spaces members SPACE` | members and roles | no |
| `linshare spaces add-member SPACE EMAIL --role R [--dry-run]` | give someone access | **yes** |
| `linshare spaces set-role SPACE MEMBER ROLE` | change a role (MEMBER: email or member id) | **yes** |
| `linshare spaces remove-member SPACE MEMBER` | remove access | **yes** |

`--to` and `--from` are repeated for several people: `--to a@x.org --to b@y.org`.
"External" is a heuristic: a different email domain than the user's.

## Exit codes

0 ok · 1 bad input or wrong command · 2 not logged in / login problem · 3 server refused · 4 server unreachable, failing or too slow (`"code": "timeout"`).
