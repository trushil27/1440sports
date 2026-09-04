# Active Deal Blocklist — Gate 5

Companies currently in 1440Sports' active pursuit pipeline. Signals matching these companies are auto-suppressed at Gate 5 — logged but not surfaced in the daily Top 3.

**This file must be maintained by the user.** Update whenever 1440 opens or closes a pursuit.

## How to Use

When scoring any company:
1. After Gates 0-4 pass, check this file before applying scores
2. If the company is listed → log the signal but suppress from digest
3. If the user explicitly asks for validation framing on a blocklisted signal → present with "we already spotted this" framing rather than as fresh news

## Format

```
| Company | Status | Date Added | Notes |
|---------|--------|------------|-------|
| Example | Active | 2026-04-30 | Stage: initial conversation. Owner: MD |
```

## Active Pursuits — As of 30 April 2026

| Company | Status | Date Added | Notes |
|---------|--------|------------|-------|
| Factory AI | Conversation in progress | 2026-04-30 | MD has spoken with them; Series C $1.5B, London office Q2 2026 |

## Closed / Lost (Historical — Do Not Re-Surface for 12 Months)

| Company | Outcome | Date Closed | Re-evaluate After |
|---------|---------|-------------|-------------------|
| *(empty)* | | | |

## Cooling-Off (Do Not Re-Surface for 6 Months)

Signals where outreach happened but didn't progress. Cool off before re-surfacing.

| Company | Last Outreach | Re-evaluate After |
|---------|---------------|-------------------|
| *(empty)* | | |

## Maintenance Notes

When updating:
1. Append new pursuits, do not delete (history matters for the Closed/Lost section)
2. Move from Active to Closed/Lost when the deal concludes one way or the other
3. The Cooling-Off section prevents the engine from re-surfacing recently-pitched companies and looking like it has no memory
