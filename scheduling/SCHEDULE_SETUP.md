# 6 AM daily delivery — paste-ready setup

This delivers one branded 2-page hero brief (PDF attached) to
**trushil.jani@1440sports.com** every morning at **06:00**.

The container here is ephemeral, so the schedule lives in **Claude Code on the
web** (a fresh container is spun up on the trigger). Two things to set once:
the **secrets** (so it can send email) and the **trigger** (so it runs at 6 AM).

---

> ⚠️ **Never paste a real password/secret into this file or any file in the
> repo.** Secrets go ONLY in the environment's **Settings → Secrets** store.
> Anything committed to git is exposed and must be rotated.

## Why Microsoft Graph, not SMTP

We tested SMTP from this environment: **port 587 is blocked** (and M365 often
disables SMTP AUTH tenant-wide), so SMTP is unreliable here. **Microsoft Graph
sends email over HTTPS (port 443), which is open** — and it sends as your real
mailbox via OAuth, with no SMTP dependency. Graph is the recommended path. SMTP
remains a built-in fallback if your runner allows it.

## Step 1 — One-time Azure app registration (admin)

Ask whoever administers your Microsoft 365 / Azure tenant to:

1. **Azure Portal → App registrations → New registration** (name e.g.
   "1440 Daily Brief Mailer").
2. **API permissions → Add → Microsoft Graph → Application permissions →
   `Mail.Send`**, then **Grant admin consent**.
3. **Certificates & secrets → New client secret** → copy the secret **value**.
4. Note the **Directory (tenant) ID** and **Application (client) ID**.

> Tip: to restrict the app to only send from your mailbox (not the whole
> tenant), apply an Exchange **Application Access Policy** scoped to
> trushil.jani@1440sports.com.

## Step 2 — Add secrets (once) in Settings → Secrets

In the Claude Code web environment for `trushil27/1440sports`
→ **Settings → Environment variables / Secrets**, add:

```
GRAPH_TENANT_ID=<Directory (tenant) ID>
GRAPH_CLIENT_ID=<Application (client) ID>
GRAPH_CLIENT_SECRET=<client secret value>
GRAPH_SENDER=trushil.jani@1440sports.com
EMAIL_TO=trushil.jani@1440sports.com
```

`EMAIL_TO` already defaults to your address in code. To copy your MD
automatically, also add `EMAIL_CC=md.name@1440sports.com`.

(SMTP fallback, only if your environment permits port 587:
`SMTP_HOST/PORT/STARTTLS/USER/PASS` + `EMAIL_FROM`.)

---

## Step 3 — Create the 6 AM trigger (once)

In the same environment → **Schedules / Triggers → New scheduled session**:

- **Frequency:** Daily
- **Time:** `06:00` (set your timezone — e.g. Europe/London or America/New_York)
- **Cron equivalent:** `0 6 * * *`
- **Repository / branch:** `trushil27/1440sports` · `claude/confident-cray-Q9sAc`
- **Network policy:** allow **web access (HTTPS/443)** — Graph needs only 443,
  which is open by default; no special SMTP port required
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

## Step 4 (optional) — verify it works now

From a **fresh** session in this repo (so it picks up the new secrets), with the
Graph secrets set:

```bash
python engine/run_daily.py            # sends today's hero to your email
```

The run prints `Delivery channel: graph` on success. You should receive the
email with the 2-page PDF attached within a minute. Without secrets it dry-runs
(writes to `briefs/<date>/`, prints `Delivery channel: dry-run`).

---

## Weekly rota

The single daily trigger is series-aware (see `engine/cadence.py`): **Mon–Wed =
Formula E**, **Thu–Sat = Formula 1**, **Sun = Decision day** (the one GO pick
across both series). No separate triggers needed — `run_daily.py` reads the date.

## What gets delivered

- **Subject:** `1440 Brief NNN — <Company> (<score>/100 <tier>) — <date>`
- **Body:** branded HTML summary (logo, score, headline, lede)
- **Attachments:** the 2-page **PDF** + the HTML

To send your MD the full pack instead of one hero, run
`python engine/run_daily.py --batch` (renders every eligible brief into
`briefs/<date>/`).
