# 6 AM daily delivery — paste-ready setup

This delivers one branded 2-page hero brief (PDF attached) to
**trushil.jani@1440sports.com** every morning at **06:00**.

The container here is ephemeral, so the schedule lives in **Claude Code on the
web** (a fresh container is spun up on the trigger). Two things to set once:
the **secrets** (so it can send email) and the **trigger** (so it runs at 6 AM).

---

## Step 1 — Add secrets (once)

In the Claude Code web environment for `trushil27/1440sports`
→ **Settings → Environment variables / Secrets**, add:

```
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_STARTTLS=1
SMTP_USER=trushil.jani@1440sports.com
SMTP_PASS=<Microsoft 365 app password>
EMAIL_FROM=trushil.jani@1440sports.com
EMAIL_TO=trushil.jani@1440sports.com
```

`EMAIL_TO` is already the default in code, so the only truly required secrets are
`SMTP_HOST/PORT/USER/PASS`. To also copy your MD automatically, set e.g.
`EMAIL_CC=md.name@1440sports.com`.

> **M365 app password:** Microsoft 365 → Security info → Add sign-in method →
> App password. If your tenant disables SMTP AUTH, ask IT to enable
> authenticated SMTP for this mailbox or provide an SMTP relay. (Gmail
> alternative: `smtp.gmail.com` / `587` + a Google App Password.)

---

## Step 2 — Create the 6 AM trigger (once)

In the same environment → **Schedules / Triggers → New scheduled session**:

- **Frequency:** Daily
- **Time:** `06:00` (set your timezone — e.g. Europe/London or America/New_York)
- **Cron equivalent:** `0 6 * * *`
- **Repository / branch:** `trushil27/1440sports` · `claude/confident-cray-Q9sAc`
- **Network policy:** allow **web access + outbound SMTP**
- **Prompt (paste exactly):**

```
Follow the instructions in PROMPT_DAILY.md. Refresh the signal data with live
research, then run `python engine/run_daily.py` to select today's hero, render
the branded 2-page PDF, and email it to trushil.jani@1440sports.com. Commit the
updated data and the new brief to this branch. Reply with the hero, its score,
and the one sharpest reason.
```

That's it. Every day at 06:00 a fresh session runs the research refresh, renders
the hero brief, emails the PDF, and commits the artifacts.

---

## Step 3 (optional) — verify it works now

From a session in this repo, with the secrets set:

```bash
python engine/run_daily.py            # sends today's hero to your email
```

You should receive the email with the 2-page PDF attached within a minute.
Without secrets it dry-runs (writes to `briefs/<date>/`, prints a notice).

---

## What gets delivered

- **Subject:** `1440 Brief NNN — <Company> (<score>/100 <tier>) — <date>`
- **Body:** branded HTML summary (logo, score, headline, lede)
- **Attachments:** the 2-page **PDF** + the HTML

To send your MD the full pack instead of one hero, run
`python engine/run_daily.py --batch` (renders every eligible brief into
`briefs/<date>/`).
