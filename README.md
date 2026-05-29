# 1440 Sports — Sponsorship Signals Engine

An automated daily intelligence engine that finds B2B companies eligible for a
**multi-year (min. 3-year) motorsport sponsorship** in **Formula 1 / Formula E /
FE paddock teams**, scores each opportunity on the 1440 scorecard, and emails the
single highest-conviction **"hero brief"** every morning — rendered in the exact
**1440 brand format** of the Ramp Intelligence Brief (N° 025).

> **Branding is locked to the Ramp standard:** navy `#191a48` + gold `#d1ae7a`,
> serif body, 1440 Sports logo masthead, **strictly 2 pages** (the generator
> *errors* if a brief overflows to 3). Logos live in `brand/assets/`.

---

## What it does each day

1. **Scores** every prospect on **5 pillars × /20** → Opportunity /100:
   Timing, Capacity, Brand Fit, Urgency, **Ops Fit**. (Matches the Ramp scorecard.)
2. **Gates out** the ineligible: wrong series, sub-3-year, **already present on a
   grid** (directly or via a parent/subsidiary), or **oversaturated** (>100
   agencies already pitching — the "don't be the 100th in the inbox" rule).
3. **Selects one hero** (with a 5-day cooldown so it rotates) and renders the
   branded 2-page brief as **PDF + HTML + Markdown**.
4. **Emails it** to you (Outlook/M365 via SMTP).

Each prospect is tagged **MODE A** (tech belongs in the car/championship) or
**MODE B** (tech serves the team's back-office), and **`discovery: seeded|self`**
so you can see which leads the engine found independently.

Full model: [`engine/methodology.md`](engine/methodology.md).

---

## Today's leaderboard (2026-05-29)

| # | Score | Tier | Series | Prospect | Discovery |
|---|------|------|--------|----------|-----------|
| 1 | 87 | HOT · TOP TIER | F1 | Ramp | seeded |
| 2 | 86 | HOT · TOP TIER | F1 | JFrog | seeded |
| 3 | 83 | HOT | F1 | **Cohesity** | **self** |
| 4 | 78 | HOT | F1 | SnapLogic | seeded |
| 5 | 76 | HOT | F1 | **Snyk** | **self** |
| 6 | 76 | HOT | F1 | **Quantinuum** | **self** |
| 7 | 72 | WARM | F1 | **Abnormal Security** | **self** |
| 8 | 72 | WARM | FE | **1Password** | **self** |
| 9 | 72 | WARM | FE | **Mistral AI** | **self** |
| 10 | 69 | WARM | F1 | **Sonatype** | **self** |
| 11 | 61 | DEVELOPING | FE | **Isomorphic Labs** | **self** |
| — gated | 77 | — | — | Databricks | >100 pitches |
| — excluded | — | — | — | Schneider Electric (owns AVEVA → Porsche FE) | already present |
| — watch | — | — | — | Vertesia ("Versigent") | not yet $1B |

Team-side opening tracked: **Alpine/BWT title deal expiring end-2026** (Gucci
linked); **DS Penske exiting FE** (do not target until resolved).

---

## Quick start

```bash
pip install -r requirements.txt           # jinja2 + weasyprint (PDF)

python engine/run_daily.py --list         # ranked leaderboard
python engine/run_daily.py                 # pick hero, render brief, email it
python engine/run_daily.py --no-email      # render to disk only (dry-run)
python engine/run_daily.py --batch         # render ALL eligible briefs (for the MD)
python engine/run_daily.py --force jfrog   # force a specific prospect
```

Output: `briefs/<date>/<prospect>.{pdf,html,md}`; the pick is logged to
`briefs/history.json` so the next day rotates.

---

## How you receive the PDF in email — step by step

Delivery is via **SMTP**, configured only through environment variables (no
secrets in the repo). The daily run emails an HTML summary **with the 2-page PDF
attached**.

### Option A — automated daily email (recommended): Claude Code on the web

1. Go to <https://claude.com/code> → open this repo's environment.
2. **Settings → Secrets/Environment variables**, add (for Microsoft 365 / Outlook):
   ```
   SMTP_HOST=smtp.office365.com
   SMTP_PORT=587
   SMTP_STARTTLS=1
   SMTP_USER=you@yourdomain.com
   SMTP_PASS=<M365 app password>      # see note below
   EMAIL_FROM=you@yourdomain.com
   EMAIL_TO=you@1440sports.com,md@1440sports.com   # comma-separated
   ```
   > **M365 app password:** if your tenant blocks basic SMTP auth, create an
   > *app password* (Security info → Add sign-in method → App password), or ask
   > IT to enable an authenticated SMTP relay / SMTP AUTH for the mailbox. For
   > Gmail, use `smtp.gmail.com:587` + a Google App Password.
3. **Set a scheduled trigger** (daily, e.g. 07:00 your time) with the prompt:
   *"Follow the instructions in `PROMPT_DAILY.md`."*
4. Pick a **network policy** that allows web research **and** outbound SMTP.

Each morning a fresh container runs the research refresh, renders the hero brief,
and emails it to `EMAIL_TO` with the PDF attached. Details:
[`scheduling/claude-web-trigger.md`](scheduling/claude-web-trigger.md).

### Option B — run it yourself, on demand

```bash
export SMTP_HOST=smtp.office365.com SMTP_PORT=587 SMTP_STARTTLS=1
export SMTP_USER=you@yourdomain.com SMTP_PASS=...
export EMAIL_FROM=you@yourdomain.com EMAIL_TO=you@1440sports.com
python engine/run_daily.py
```

### Option C — GitHub Actions cron (engine-only, no live research)

Move [`scheduling/daily-brief.yml`](scheduling/daily-brief.yml) to
`.github/workflows/`, add the same `SMTP_*`/`EMAIL_*` values as repo secrets, and
it emails the hero on a daily cron.

**Until SMTP is set, the run dry-runs**: it writes the brief to `briefs/<date>/`
and prints a notice, so nothing breaks.

> The connected M365 MCP tools in this workspace are read/search only (no
> `Mail.Send` scope), which is why delivery uses SMTP. If you grant a Graph
> `Mail.Send` scope later, swap `send_email.send()` for a Graph call — the rest
> of the pipeline is unchanged.

---

## "Where is the engine deployed?"

The engine is **code in this repo** — there is no separate server to host. It is
designed to run as a **scheduled Claude Code web session** (Option A): the
"deployment" is the daily trigger + the environment secrets + the network policy.
That is the durable model, because the execution container is ephemeral (it is
reclaimed after inactivity, so an in-container `cron` would not survive). For a
fully self-hosted alternative, the GitHub Actions cron (Option C) runs the engine
on GitHub's infrastructure with no machine of your own.

See <https://code.claude.com/docs/en/claude-code-on-the-web> for triggers,
environments, secrets, and network policies.

---

## For submitting to your MD

- **One polished hero brief/day**: `python engine/run_daily.py` → emailed PDF.
- **A full pack of every live opportunity**: `python engine/run_daily.py --batch`
  → all eligible 2-page briefs in `briefs/<date>/`, each on-brand and 2 pages.
- **The leaderboard at a glance**: `python engine/run_daily.py --list`.

---

## Repo layout

```
engine/
  methodology.md        # the scoring + selection model (read first)
  scoring.py            # 5 pillars, tiers, gates (incl. already-present), ranking, cooldown
  generate_brief.py     # branded HTML + Markdown + PDF; ENFORCES 2-page limit
  send_email.py         # SMTP delivery (Outlook/M365), dry-run safe
  run_daily.py          # daily entrypoint (--list / --batch / --force / --no-email)
  templates/brief.html.j2   # the 1440-branded 2-page layout
brand/
  assets/               # 1440 logos (navy/gold + white), used in the masthead
  logos_src/            # original CMYK logo pack (PNG/SVG/EPS)
data/
  prospects.json        # the scored prospect database (the engine's memory)
  teams.json            # live F1 + FE sponsor inventory / open categories
  sources.md            # citations behind the current data
briefs/<date>/...       # generated briefs + history.json
scheduling/             # Claude web trigger + GitHub Actions
PROMPT_DAILY.md         # the daily research-refresh instruction
.claude/settings.json   # SessionStart hook: installs deps in each web session
```
