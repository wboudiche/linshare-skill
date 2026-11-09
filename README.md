# linshare-skill

An agent skill that lets an AI assistant (Claude Code and other tools that read
`SKILL.md` skills) share documents through LinShare: send files by email, list or
revoke shares, download received files, and ask people to send files. The assistant
shows a dry-run summary and waits for an explicit "yes" before anything is sent,
revoked, deleted or closed.

The skill drives the `linshare` command from the **linshare-cli** repository, which
must be installed first (Python 3.10+, LinShare 6.5 or later).

## Install

**1. The skill, in Claude Code** — type in Claude:

```
/plugin install linshare --marketplace wboudiche/linshare-skill
```

(older Claude Code: `/plugin marketplace add wboudiche/linshare-skill`, then `/plugin install linshare@linshare-skill`)

**2. The `linshare` command** (Python 3.10+):

```bash
pip install "git+<linshare-cli repository URL>#subdirectory=agent-harness"
```

**3. Log in once**, by typing in Claude (your password goes to your terminal, never to the chat):

```
! linshare login --server https://linshare.example.com
```

You don't need to remember steps 2 and 3: on the first request, the assistant checks
and tells you what is missing.

Other agents that read `SKILL.md` skills: copy `skills/linshare/` into their skills folder.

## What you can ask

Ask in plain words, in any language. ✋ marks the actions the assistant always
confirms with you first.

### Send files

| You say | What happens |
|---|---|
| "Share contract.pdf with marc@acme.com via LinShare" | ✋ uploads the file and shares it by email; the server's default expiry applies |
| "Send report.pdf and annex.xlsx to marc@acme.com and julie@acme.com, for 2 weeks" | ✋ several files, several recipients, expiry in 14 days |
| "Share the contract with Marc until December 15, subject *Contract*, message *Please sign before Friday*" | ✋ exact expiry date, your subject and message (it never writes one for you) |
| "Share budget.xlsx with partner@other.org with a password-protected link" | ✋ recipients outside your organisation are flagged; they get a password-protected link |
| "Share it with Marc and warn me if he hasn't downloaded it by Friday" | ✋ LinShare emails you on that day if the share is still not downloaded |
| "Share it with Marc, no reminder" | ✋ turns that alert off (if your administrator allows it) |
| "Share it with Marc and send me a copy of the email" | ✋ you also receive the share notification |
| "Share this 3 GB video with the team" | ✋ large files are fine: they are uploaded in chunks; the assistant warns you it takes a while |

### Follow up

| You say | What happens |
|---|---|
| "What have I shared on LinShare?" | lists your shares: file, recipient, expiry, number of downloads |
| "Has Marc downloaded the contract?" | reads the download count on the server (LinShare also emails you at the first download) |
| "Cancel what I shared with Marc" | ✋ lists the matching shares, then revokes them |
| "Delete the old version of the report from LinShare" | ✋ lists your documents, then deletes the ones you confirm |

### Receive files

| You say | What happens |
|---|---|
| "What did people send me on LinShare?" | lists the files shared with you |
| "Download the file Julie sent me into ~/Downloads" | saves it (never overwrites an existing file) |
| "Ask ann@acme.com to send me the scans, message *Please upload the signed scans*" | ✋ creates a private upload request; LinShare emails Ann a link |
| "Ask Ann and Bob for their invoices before the end of the month" | ✋ one private request per person, with that deadline; it asks you for the message if you gave none |
| "Did Ann send the scans?" | lists your requests and how many files came in |
| "Download what Ann sent" | saves the received files as a zip |
| "Close the request to Ann" | ✋ closes it; nobody can upload any more |

### Team workgroups and workspaces

| You say | What happens |
|---|---|
| "Which LinShare workgroups am I in?" | lists your workgroups and workspaces, with your role in each |
| "What's in the Marketing workgroup?" / "…in its Contracts folder?" | lists folders and files (who changed them last, when) |
| "Put these slides in the Marketing workgroup, in Contracts" | ✋ shows the files, the folder and everyone who will see them, then uploads (any size) |
| "Get the latest budget from the Finance workgroup" | downloads it (never overwrites an existing file) |
| "Create a workgroup *Project Atlas* with a folder *Specs*" | creates them; you are the only member until you add people |
| "Add julie@acme.com to Project Atlas as a reader" | ✋ shows who, where and what the role allows, then adds her |
| "Let Julie edit files in Project Atlas" | ✋ changes her role to writer |
| "Who has access to Project Atlas?" | lists the members and their roles |
| "Remove Paul from Project Atlas" | ✋ removes his access |
| "Delete the old drafts from Project Atlas" | ✋ lists them, says they disappear for every member, then deletes |
| "Delete the Project Atlas workgroup" | ✋ warns that all its files go, for everyone, then deletes |

Roles: *reader* (read only), *contributor* (can add files), *writer* (can add and
change), *admin* (also manages members). Workspaces group several workgroups; they
have reader, writer and admin roles.

On LinShare 7.0, a few of these fail because of server bugs (listing members,
adding someone to a workspace); the assistant tells you when that happens.

### Account

| You say | What happens |
|---|---|
| "Connect me to LinShare" | tells you to type `! linshare login` yourself: you enter your password (and 2FA code) in your terminal, never in the chat |
| "Which LinShare account am I using?" | shows the server, its version and your email |

### What a confirmation looks like

```
You:    Share contract.pdf with marc@acme.com and paul@partner.org for a week,
        message "Please sign".
Agent:  Here is what will be sent:
        - contract.pdf (240 KB)
        - to marc@acme.com, and paul@partner.org — outside your organisation
        - expires on 2026-11-16
        - message: "Please sign"; no password-protected link
        - download alert: on 2026-11-11 (server default: after 3 working days)
        Shall I send it?
You:    yes
Agent:  Shared contract.pdf with marc@acme.com and paul@partner.org until 2026-11-16.
```

The assistant checks the dry run against the server first, so the summary shows
what will really happen, including settings your administrator imposes. If you
change anything (a recipient, the date, a file), it shows a new summary and asks
again. Before telling you whether something was shared, revoked or closed, it
checks the server rather than its memory.

## Test

`tests/test_skill.py` checks that every command and option the skill mentions exists
in the installed `linshare` (so the skill and the command don't drift apart), and that
the safety rules are still there:

```bash
pip install pytest
pytest -q tests
```

The checks against the command are skipped if `linshare` is not installed.

## Compatibility

Written for linshare-cli as of 2026-11-09 (`spaces` commands, `share --alert-if-not-downloaded`,
`--send-me-a-copy`, `request-files --message`). Run the tests after updating either side.
