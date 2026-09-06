# Feeding the 10 a.m. Claude routine into the desk

The account runs a Claude Routine, **"Daily sponsorship prospect research"**, at `0 9 * * *`
(10:00 London in summer). It has been firing daily since 29 May 2026 and it looks for F1 and
Formula E prospects — a second daily source alongside the n8n engine.

## Why none of its history reached the app

Checked on 6 Sep 2026, every route:

| Route | Result |
|---|---|
| `list_sessions` | Trigger-fired sessions are excluded from the listing, so the ~100 past runs cannot be enumerated. |
| `get_session` on a run | Returns metadata only (status, cost, timings). No transcript, so no company names. |
| SharePoint / OneDrive | The routine's step 7 makes a branded PDF, but nothing matching is stored — the file is written inside the run's own container and lost when it ends. |
| Outlook | The routine sends no mail. Its notification channels (push, email) are both off. The 241 `1440 Intelligence Brief — …` emails in the mailbox are the **n8n** engine, not this routine. |

So the routine has been doing real work every morning for three months and throwing all of it
away. Nothing can recover the past runs; the fix is to make future runs deliver.

**The routine cannot be edited by an agent** — it was created through the HTTP API, and an
agent may only update routines it created itself. Trushil has to paste the prompt below into
the routine in the Claude app (Routines → Daily sponsorship prospect research → edit prompt).

## The replacement prompt

Everything the routine already did is kept word for word. Two things are added: the MD's
Formula E priority, and a delivery step that emails a machine-readable block the desk can
ingest exactly the way it ingests the n8n log.

```text
Research and identify B2B sponsorship and activation opportunities for racing teams in F1, Formula E championships, and FE paddock teams.

1. Scan recent news, team announcements, and sponsor landscapes for F1 and Formula E to identify gaps in current sponsorships or upcoming activation windows.
2. Research 5–10 B2B technology and services companies that could add value to racing operations (e.g., data analytics, logistics, AI/automation, connectivity, sustainability tech, Fintech, Energy) and cross-reference them against current team sponsor lists.
3. For each prospect, assess fit: Does their product/service integrate into car performance, championship operations, or team infrastructure? Is there a narrative alignment with the team's brand or goals?
4. Prioritize prospects capable of 3+ year deals with clear activation potential (title rights, technical partnership, paddock presence, or branded integrations).
5. Compile a daily summary with prospect name, relevant racing team(s), category, rationale, and suggested activation angle.
6. Make sure we are 50th agency to outreach the prospect and not more than that.
7. Make that a pdf after every run based on the website and 1440 sports branding with logo.

PRIORITY (MD instruction, Sep 2026): FORMULA E over Formula 1. Weight the search towards Formula E teams and FE-suited categories (energy, electrification, storage, charging, industrial, mobility, sustainability). Only put a prospect on F1 when the FE case would be dishonest.

DELIVERY — do this at the end of EVERY run, it is what makes the work usable:
Email the summary to Trushil.Jani@1440sports.com using the Microsoft 365 connector. Subject exactly: "1440 Routine Signals — <today's date as D Mon YYYY>". The body must start with a machine-readable block so the desk app can ingest it automatically, then your normal prose below it. The block:

<SIGNALS>
[{"company": "...", "series": "FE" or "F1", "team": "...", "category": "...", "trigger": "the specific dated event — a funding round, listing, spin-off, contract or leadership move — with its date", "trigger_date": "YYYY-MM-DD", "source_url": "the primary source you actually opened", "person": "the real decision-maker from the company's own leadership page, or null", "role": "...", "score": 0-100, "rationale": "one sentence", "activation_angle": "one sentence"}]
</SIGNALS>

Rules for that block: valid JSON, one object per prospect. Never invent a figure, a name, a date or a source — if you could not verify something, use null and say so in the prose. Only include a prospect whose trigger event is dated within the last 90 days. If a run finds nothing that clears the bar, send the email anyway with an empty list and explain in the prose what you monitored.

If no new high-confidence prospects emerge, note what you monitored and confirm briefly.
```

## What happens once it delivers

`intel.routine_inbox` reads those emails, turns each `<SIGNALS>` entry into a candidate row,
drops anything already in the desk (by normalised company name) and anything on the
blocklist, and leaves the rest for a full case build under `docs/CASE_SPEC.md`. The routine's
score is a hint only — every claim is re-verified before a case is written, exactly as the
n8n rows were.
