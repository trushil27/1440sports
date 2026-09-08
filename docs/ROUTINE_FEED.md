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

**Corrected 7 Sep 2026.** The first version told the routine to lead with a `<SIGNALS>` JSON
block. That parses beautifully and reads like spam — the operator opened it and saw a wall of
braces. A daily email is read by a person first. This version puts a readable digest at the
top in the desk's own voice and leaves one small machine block at the very bottom, under a
rule, where nobody has to look at it.

Paste this into the Claude app: Routines → *Daily sponsorship prospect research* → edit prompt.

```text
Research and identify B2B sponsorship and activation opportunities for racing teams in F1, Formula E championships, and FE paddock teams.

1. Scan recent news, team announcements, and sponsor landscapes for F1 and Formula E to identify gaps in current sponsorships or upcoming activation windows.
2. Research 5–10 B2B technology and services companies that could add value to racing operations (e.g., data analytics, logistics, AI/automation, connectivity, sustainability tech, Fintech, Energy) and cross-reference them against current team sponsor lists.
3. For each prospect, assess fit: Does their product/service integrate into car performance, championship operations, or team infrastructure? Is there a narrative alignment with the team's brand or goals?
4. Prioritize prospects capable of 3+ year deals with clear activation potential (title rights, technical partnership, paddock presence, or branded integrations).
5. BE EARLY. The prospects that matter most are companies whose Series C, Series D, Series E (or later) round, or spin-out / carve-out, was announced in the last 30 days — new money and a new brand to build at the same moment, before other agencies have called. Look for those first; name the round stage and its date for every prospect.

PRIORITY (MD instruction, Sep 2026): FORMULA E over Formula 1. Weight the search towards Formula E teams and FE-suited categories (energy, electrification, storage, charging, industrial, mobility, sustainability). Only put a prospect on F1 when the FE case would be dishonest.

ONLY include a prospect whose trigger event — a funding round, listing, spin-off, major contract or leadership hire — is dated within the last 90 days. Never invent a figure, a name, a date or a source: if you could not verify something, leave it out and say so.

DELIVERY — every run, this is what makes the work usable. Email Trushil.Jani@1440sports.com with the subject "1440 Routine Signals — <date as D Mon YYYY>". Write the body for a person to read on a phone in thirty seconds, in this shape and nothing else:

1440 ROUTINE SIGNALS — <date>
<One sentence: how many candidates, and the single best one.>

1. <COMPANY> — <FE or F1> — <team>
   Trigger: <the dated event, with its date>
   Why: <one sentence on the fit and the open lane>
   Source: <the primary URL you actually opened>

2. <COMPANY> — …

SCREENED OUT
<Company>: <one line on why — stale, already a partner, too small.>

---
DATA (for the desk, ignore)
<SIGNALS>[{"company": "...", "series": "FE", "team": "...", "trigger": "...", "trigger_date": "YYYY-MM-DD", "source_url": "...", "person": null, "role": null, "score": 0}]</SIGNALS>

Keep the readable part above the rule short: five entries at most, one line each for Trigger, Why and Source. If a run finds nothing that clears the bar, send the email anyway saying what you monitored, with an empty list in the data block.
```

## What happens once it delivers

The desk reads those emails, drops anything it already holds (by normalised company name) and
anything on the blocklist, and leaves the rest for a full case build under `docs/CASE_SPEC.md`.
The routine's score is a hint only — every claim is re-verified before a case is written,
exactly as the n8n rows were.
