# Outreach: a sequence per trigger, a weekly cadence, and the numbers

Requested by the operator on 11 Sep 2026: "Outreach sequence per trigger (new CEO / CMO,
ex-sponsor exec moves, funding round) and a weekly cadence with reply and meeting rates
tracked. We also have to spot these for the signals."

## What kind of moment is this? — `intel.triggers`

Every signal row now carries a `trigger_type`, derived deterministically from the trigger
text the ledger verified (and `key_facts.alumni_match`), never guessed by a model:

| type | shown as | opens on |
|---|---|---|
| `exec_move` | Ex-sponsor executive | shared history: the person did a grid deal before |
| `new_cmo` | New CMO / commercial lead | the buyer just arrived; their 90-day plan |
| `new_ceo` | New CEO | first hundred days; strategy, not sport |
| `spin_off` | Spin-off / carve-out | a new name needs a stage; founding partner |
| `listing` | Listing / IPO | public audience, IR calendar |
| `funding_round` | Funding round | new money, new brand budget |
| `expansion` | Expansion | the race in the new market |
| `other` | Other | standard sequence |

Priority when several apply: exec move > new CMO > new CEO > spin-off > listing > round.
The scanner prompt now asks for leadership triggers as first-class signals in the same
window (new CEO / CMO / CCO appointments; senior hires from companies that sponsored a
team, named in `key_facts.alumni_match`), so the desk spots them, not just rounds.

The app shows the type as a chip on every row and as a filter on the signal lists.

## The sequences — `intel.outreach`

One touch a week for four weeks, a LinkedIn connect in the first week, a call in the third;
after the last touch the sequence is parked for 90 days unless a reply came:

| day | step | channel |
|---|---|---|
| 0 | open | email |
| 3 | connect | LinkedIn |
| 7 | follow_up | email |
| 14 | value_add | email |
| 21 | call | phone |
| 28 | close_loop | email |

What each touch *says* differs by trigger (`python -m intel.outreach plan`). The opening
email still comes from `outreach.compose` — verified claims only, the 25-minute ask.

## The log — `data/outreach_log.json` (the outcomes loop)

```bash
python -m intel.outreach start 247                     # open a sequence for a brief
python -m intel.outreach touch 247 open                # a step went out (by N° or sequence id)
python -m intel.outreach touch 247 follow_up --date 2026-09-18
python -m intel.outreach reply 247 --note "asked for the deck"
python -m intel.outreach meeting 247 --date 2026-09-25
python -m intel.outreach outcome 247 won|declined|parked
python -m intel.outreach report [--email]              # the weekly report
```

Rates: `reply_rate = replies / sequences with ≥1 sent touch`, `meeting_rate = meetings /
contacted`, by trigger type and in total, plus the last eight ISO weeks (started, touches,
replies, meetings) and "due this week" (planned touches up to Sunday; overdue flagged).

## The trigger watch and the filings inbox

- `data/trigger_watch.json` is the desk's judged list: named people and events with the
  sponsor link, the ICP call, series fit, team lane, action (`start_sequence`,
  `sponsor_side`, `watch`, `in_pursuit`, `screen_out`) and sources. Filled and re-swept by
  the desk in session; shown first on the Outreach page and in the Monday report.
- `data/trigger_inbox.json` is automatic: `intel.edgar_watch` runs in the daily job and pulls
  from SEC EDGAR full-text search every Form 8-K of the last two days whose Item 5.02 names a
  chief marketing, commercial, revenue or executive officer, plus new S-1 / F-1 / 10-12B
  registration statements. Listed companies only (a private company files nothing; the
  routine, the scanner and the press wires cover those). Each hit waits as "to judge" until
  the desk moves it into the watch or sets `judged: true`. No model, no key, no cost.
- What is *not* automatic, stated plainly: private-company CMO moves and departures
  (Binance, Crypto.com) come from press coverage, the routine's `<SIGNALS>` block and the
  scanner; a paid people-data feed (PitchBook, Crunchbase, ZoomInfo) would add same-day
  capture there and can be wired into the same inbox.

## Where it shows

- **App → Outreach**: rates by trigger, the 8-week series, this week's touches, every
  sequence, and the playbooks. Every signal page shows its sequence with dates (from the
  start date, or "if started today").
- **Monday 07:00 UTC email** to the operator (`.github/workflows/weekly-outreach.yml`):
  the same numbers and the week's touches. No model API key, no database.

Commit the log after logging; the site and the Monday email read the repo.
