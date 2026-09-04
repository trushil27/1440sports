# Production n8n workflow vs the Python pipeline — reconciliation

Source of truth for "production": `spec/n8n_workflow_production_2026-09-04.json` — the live
export of workflow `1440 Daily Intelligence Brief` (id `SLyZcgWP5vl6kEas`, 18 nodes, `active:
true`). Node code was pulled from `parameters.jsCode` / `parameters.jsonBody`. "Brief" below is
`1440_CLAUDE_CODE_BUILD_BRIEF.md`. This document records, behaviour by behaviour, what production
does, what `pipeline/intel/` does, and whether the brief decides the difference.

Legend for the **Brief decides?** column: **YES §x** = the brief mandates the Python behaviour;
**NO** = the Python is silently different and nobody has ruled on it — needs a human decision.

## 0. Production wiring (as exported)

```
6am Weekdays Trigger  (cron "0 47 21 * * 1-7" — see §3.11)
  → Anthropic — Run Signals (claude-sonnet-4-6, max_tokens 12000, web_search_20250305 ×10)
  → Parse Signal Data (v2.1.9b: parser, HARD_BLOCK, 30-day cooling list, FE rotation, revisit
                       fallback, brief number)
  → Anthropic - Write Brief (claude-sonnet-4-6, max_tokens 16000)   ←── Retry Prep ──┐
  → Parse Claude Response (BRIEF_DATA mandatory, SIGNAL_DATA reconstructed if missing) │
  → Audit Brief (v2.1.8d, 13 rules) ──→ Format Audit Log Rows → Google Sheets — Audit Log
  → Audit Route: pass ─→ Google Sheets — Read Daily Signals → Duplicate Guard (v2.1.10e)
                 retry ─→ Retry Prep ──────────────────────────────────────────────────┘
                 manual_review ─→ Outlook — Operator Manual Review Alert
  → Guard Route: send ─→ 1440 Builder — Render PDF (Railway) → Outlook — Send Brief
                                                             → Google Sheets — Log Signal
                 block ─→ Format Audit Log Rows (guard rows) + Outlook — Guard Block Alert
```

Note the ordering: the brief is **written and audited before** the 30-day duplicate guard runs, so
a duplicate consumes a writer call, a retry and a brief number before it is blocked. The Python
pipeline dedups at triage, before anything is written (brief §6.3).

## 1. Audit Brief (v2.1.8d) → `intel/audit.py`

Ported rule for rule; the module docstring lists the four deliberate deviations (rule 4 uses
`run_date` instead of `new Date()` UTC; rule 6 escapes the team label; rule 11 counts all three
parts of a June-format risk; no `operational_fit_*` fallbacks). Per-rule differences against the
*previous* Python port (which was built from the roadmap's rule list, not the code):

| Rule | JS code(s) / severity | Previous port → now |
|---|---|---|
| 1 | `min_3_year_deal`, `missing_duration_marker` — critical | changed: was any duration ≥ 3 years in words/digits/months; now (a) `\bTWO\s+YEARS?\b` in plain text fails and (b) a literal `<font …>THREE\|FOUR\|FIVE YEARS</font>` marker is required (so "3-year", "36 months", "SIX YEARS" all fail) |
| 2 | `opening_quote_ending`, `opening_quote_metaphor` — critical | changed: ending = `?` followed by `&rdquo;`, `"`, `“`, `”` or end (curly-quote alternatives are the v2.1.8d addition; `’`, `'` and `</font>` after the `?` fail); new metaphor check on the text before the closing ask |
| 3 | `opening_intro_question` — critical | changed: only a *trailing* `?` fails (was any `?`) |
| 4 | `footer_date_mismatch` — **medium** | changed: severity high → medium; comparison is upper/trim of the raw field |
| 5 | `industry_meta_date_suffix` — **medium** | changed: severity high → medium; only `[·\-\s]\s*YYYY-MM-DD$` (prose dates like "· 14 Jun 2026" are no longer caught) |
| 6 | p2: `why_team_claim_in_case_p2_{a,b,c}`, `team_has_no_in_case_p2` critical, `count_claim_in_case_p2` medium; deck: `team_vacancy_in_deck_{a,e,b,c}` critical, `count_claim_in_deck` medium | changed: was one code, generic vacancy words, team aliases (first/last word); now the exact five JS patterns, the v2.1.8d vacancy list, min start-index distance across all mentions (Pattern B), full-label-only team match, C/D applied to the deck too. "the slot is open at [Team]" (original Ramp headline) is deliberately NOT caught |
| 7 | `wc_<field>` — **medium** | changed: severity high → medium; +5 words grace; `value_content` ceiling 70 → 75; `operational_fit_content` added; risks and score-cell notes are NOT counted; `why_now_callout` counted with its "WHY NOW" prefix; JS `wc` (tags only) instead of `strip_markup` |
| 8 | `low_confidence` — critical | identical |
| 9 | `bad_track_label` — **medium** | changed: severity high → medium |
| 10 | `risk_count` — critical when value_section true, medium when false | changed: was always high |
| 11 | `page2_overflow_risk` — critical | changed: budgets 2500/2300 → **2300/2100**; score-cell notes no longer counted; `value_content` counted even when the section is off; JS `plainText` (entities removed) |
| 12 | `value_section_missing`, `value_content_empty` — critical | changed: `value_section_label` no longer checked; empty `value_content` now fails at *any* score when the section is on |
| 13 | `p2_why_team_phrase_overlap` — medium | changed: exact 5-grams (not maximal runs), ≥ 3 content tokens (was 2) with the JS stopword list, phrases with ≥ 2 team-label words skipped, ONE violation naming the first phrase "(+N more)" |
| route | `pass` / `retry` (retry_count < 1) / `manual_review` | changed: `manual_review` added, driven by `retry_count`; `previous_violations` is pass-through only |
| log | `_audit_log_rows`: summary row (`audit_passed` / `audit_failed_retrying` / `audit_failed_manual_review`) + one `violation` row each | new: `AuditResult.log_rows()`; `AuditResult.as_json()` = JS `_audit` |
| feedback | Retry Prep: `- [SEVERITY] code: detail` lines inside the RETRY MODE block | changed: was a numbered "Rule N (code, severity)" list under an "AUDIT FEEDBACK" header |

Severity vocabulary is now the JS's (`critical` / `medium`). `run_daily.produce_brief` still
appends a synthetic `{"rule": 11, "code": "page_overflow", "severity": "high"}` entry on a render
overflow — harmless, but that string should become `critical` when run_daily is next touched.

**Orchestrator mapping (run_daily not edited):** `pass` → render/send path; `retry` → feed
`violations_feedback()` back once; `manual_review` → `AuditStatus.failed` + operator alert, never
MD-eligible. `produce_brief` reaches the same outcome by attempt count; passing
`retry_count=attempt - 1` to `audit_brief` would make the second result read `manual_review`
directly and let `log_rows()` label it `audit_failed_manual_review`.

## 2. Prompts → `intel/prompts/*_v218_*.txt`

Extracted verbatim (see `prompts/README.md`). Findings that need a decision:

| # | Production | Python | Brief decides? |
|---|---|---|---|
| 2.1 | **Scanner scoring text regressed.** The v2.1.8 system prompt opens "Six gates first, then four dimensions 0-25 each … TIMING, CAPACITY, BRAND FIT, URGENCY" and its example `score_breakdown` is `{timing 23, capacity 22, brand_fit 20, urgency_or_alumni 17}` — the pre-Phase-2.1 scale. The 2.1.3 text had five /20 dimensions incl. OPS FIT and the OF gate. Yet the production **writer** user prompt reads `score_breakdown.ops_fit`, `key_facts.taxonomy_category`, `key_facts.ops_fit_note` and `confidence_level` — none of which the production scanner is asked to emit (they render as empty in n8n). | `ScoreBreakdown` enforces five /20 dims (`urgency` required); `urgency_or_alumni` accepted as an optional extra. Output in the 4×25 shape (`timing: 23`, no `urgency`) **fails parse** → scan retry → `ScanFailed`. | Brief §1 says "V2.1 six gates, five dimensions /20" and §0.5 forbids changing the scale without the MD → Python keeps /20. **Decision needed:** either restore the 2.1.3 scoring block in the scanner prompt (recommended) or accept the 4×25 shape. |
| 2.2 | Scanner returns exactly TEN signals. | `scan_candidates_max = 12`, at least 1. | YES §6.1 (8–12). |
| 2.3 | Scanner has no "ANTI-HALLUCINATION RULES" block (moved to the writer). | verbatim v218. | — (test assertion updated). |
| 2.4 | Models `claude-sonnet-4-6`; scanner `max_tokens` 12000; `web_search_20250305`. | `claude-sonnet-5` / `claude-opus-5` (verify), 16000, `web_search_20260209`. | YES §4. |
| 2.5 | Writer user prompt: no `OF gate passed` line; retry block token. | same (v218); retry block substituted. | — |
| 2.6 | Retry Prep includes the **PREVIOUS DRAFT (BRIEF_DATA fields)** JSON in the retry message. | `brief.retry_block()` supports it but `run_daily` passes only the violation lines, so the writer regenerates from the signal + violations. | **NO** — §6.8 says only "one retry with violations fed back". Small `run_daily` change if wanted. |
| 2.7 | Writer picks the VALUE mode itself. | Code decides (`render.value_mode_for`) and tells the writer; `value_mode` emitted. | Not in the brief; the roadmap's mode thresholds are applied in code — keep. |

`WRITER_ADDENDUM` after review — **removed** (covered verbatim by v218): three-year minimum,
VALUE TO [TEAM] section + modes, deck rule, "AUDIT FEEDBACK" retry instruction, "this addendum
wins" preamble. **Kept** (June-format fields the production prompt does not emit): (1) use the
code-decided mode and emit `value_mode`; (2) three-element risk arrays; (3) `bottom_line`;
(4) `hq` / `ticker` / `signals`; (5) proof points / GRID FIT / SOURCES / VERIFIED are computed by
the pipeline, no off-calendar races.

## 3. Selection & dedup — Parse Signal Data (v2.1.9b), Duplicate Guard (v2.1.10e), Read Daily Signals, Retry Prep

| # | Behaviour | Production | Python | Brief decides? |
|---|---|---|---|---|
| 3.1 | **FE rotation days** | `FE_FORCE_DAYS = [2, 5, 6]` on `getUTCDay()` → **Tue, Fri and Sat** force the first eligible FE candidate. (The roadmap's "pending weekend decision" was resolved in code as Sat = FE.) | `score.fe_rotation_day`: Tue/Fri only, on the London run date. Sat/Sun pick by score. | Brief §6.4 says "FE rotation rule (Tue/Fri)". **NO for Saturday** — the brief predates the Sat change; confirm whether Saturday FE-forcing is intended. |
| 3.2 | **Tie-breaks / ordering** | Candidates kept in **scanner order** (model-ranked, best first). `anyWinner` = first eligible; `feWinner` = first eligible FE. No re-sorting by score. | `rank_eligible` sorts by the **recomputed** ranking score (sum of /20 dims, minus ops_fit when brand_fit < 12, plus alumni boost from the `alumni` table, capped at 70 when a sponsor-identity hit exists); FE first on rotation days; ties keep scanner order. | §6.4 "Record all six gate results and the five /20 dimensions + alumni boost … Select the top eligible candidate" implies recomputation but does not say "re-rank". **NO** — silently different when the model's own ranking disagrees with the arithmetic. |
| 3.3 | **Score threshold** | Parse Signal Data has **no floor**. The Duplicate Guard blocks `score < 70` — *after* writing and auditing — using `brief.score` from the writer's BRIEF_DATA (model-authored, may differ from the scanner score). No fallback to the next candidate. | `below_threshold` at triage on the recomputed ranking score (`md_threshold = 70`); next candidate is tried. | YES §6.4 (threshold 70 as config) and §6.5 (next candidate). |
| 3.4 | **Hard-block list** | `HARD_BLOCK` array of 12 names in code: Factory AI, JFrog, Mistral AI, Luminary Cloud, Netomi, Shield AI, Wayve, Lattice, Omni Analytics, Legora, Cerebras Systems, Sierra. Match = equality **or substring either way** on the (older) normaliser (`inc\|ltd\|llc\|corp\|technologies\|technology\|ai\|the` stripped, no parenthetical strip). So "Sierra" blocks "Sierra Space", "Lattice" blocks "Lattice Semiconductor". | `blocklist` table (seeded from `spec/blocklist.md` + the same 12 names, `seeds/blocklist.json`), **exact** `company_norm` match, with status/cooling dates. | YES §6.3 ("Reject if `company_norm` is in `blocklist`"). Note the substring semantics are lost — "Sierra Space" would pass in Python. Not in the brief → flag. |
| 3.5 | **30-day guard keying** | Two layers, both **company-only**: (a) `staticData.surfaced` cooling list in Parse Signal Data (name = old normaliser, `trigger` stored but never compared, 30 days from `ts`); (b) Duplicate Guard vs the *Daily Signals* sheet (name = v2.1.10e normaliser: parenthetical stripped first, then `inc\|ltd\|llc\|corp\|corporation\|technologies\|technology\|ai\|labs\|lab\|holdings\|holding\|group\|company\|co\|the`), rows with `cutoff ≤ date < today`. | `surfaced_log` keyed on `(company_norm, trigger_reason_norm)`; same company + same trigger class within `dedup_window_days` (30) → `dedup_suppressed`; different class → passes, tagged RESURFACED. | YES §3.2 / §6.3 / §9.4 — company-only is the bug the brief calls out. |
| 3.6 | **Normaliser** | Two different normalisers (3.4 vs 3.5b). Guard strips `ai`, `labs`, `lab`, `group`, `co`, `company`, `holding` — so "Exa" ≡ "Exa Labs", "Factory AI" ≡ "Factory". | Brief §5 list: parens → `inc, ltd, llc, plc, corp, holdings, technologies, technology, the` → non-alnum. "Exa Labs" ≠ "Exa"; "Factory AI" keeps "ai". | YES §5 (explicit list). Flag: the production guard's extra suffixes (`labs`, `ai`, `group`, `co`…) were added from real dedup misses; the brief's list does not include them. |
| 3.7 | **What is logged as "surfaced"** | The winner is pushed to the cooling list **at selection**, before writing/audit/guard — a candidate that then fails audit or the guard still cools for 30 days. The Sheets log (guard source) is appended only after a **send**. | `record_surfaced` runs for the **issued** brief only (verified or needs_review, audit pass **or failed**); verification-blocked candidates are not recorded. | **NO** — the brief does not say whether an audit-failed / operator-only brief should count as surfaced. |
| 3.8 | **Same-day re-run** | Guard ignores rows dated today (`rowMs >= todayMs → false`); only the in-memory cooling list prevents a same-day repeat. | Idempotent per date (`_existing_outcome`). | YES §4 / §9.8. |
| 3.9 | **`execution_mode`** | `$execution.mode !== 'production'` (manual editor runs) **and** "trigger node did not fire" both block the send; the block is logged and alerted. The check is per-execution provenance. | `Settings.execution_mode` ∈ production / shadow / dry_run is a **deployment** setting read by `send.distribute` (MD only in production). A manual `--force` run of a production deployment would send to the MD. | Brief §7 + runbook describe shadow mode; nothing covers "manual run in production". **NO** — decide whether a manual run should ever reach the MD. |
| 3.10 | **Revisit fallback tiers** | If no eligible candidate: tier 1 = first candidate that is not hard-blocked (i.e. a cooling one), tier 2 = `candidates[0]` **even if hard-blocked**; flagged `_revisit = true`, which nothing downstream reads. The guard does not re-check HARD_BLOCK, so a tier-2 fallback that is not in the Sheets log within 30 days is **sent to the MD**. Tier-1 cooling candidates that were selected-but-never-sent are also not in the sheet and pass. | No fallback: all suppressed → `no_signal`, operator gets the no-signal note, MD nothing. | YES §7 / §9.9. (Production bug, not a design choice.) |
| 3.11 | **Schedule** | Node named "6am Weekdays Trigger" but the exported cron is `0 47 21 * * 1-7` = **21:47 every day** (n8n six-field cron, instance timezone). | 05:30 Europe/London daily via `intel.schedule`; send 06:00. | YES §4. Flag the export's cron as either a test edit or the real current time. |
| 3.12 | **Brief-number seeding** | `staticData.lastBriefNumber` seeded to **9** (first brief 010), incremented on every selection (numbers are consumed by blocked / manual-review / revisit runs too). | Postgres sequence `brief_number_seq` starting at **1**, allocated when the `Brief` row is created (also consumed by blocked ones). `python -m intel.backfill --restart-sequence N` sets the continuation. | YES §5 (auto-increment, never reused). Operator must restart the sequence past the last production N° at cut-over — the export does not carry the current counter (it lives in n8n static data). |
| 3.13 | **Retry budget** | `retryCount < 1` → one retry, then `manual_review` (operator alert, **no PDF**). Retry message = violation lines + the failed draft JSON. | One retry; second failure → `AuditStatus.failed`, brief **rendered** for the operator, never MD-eligible. Violations only (see 2.6). | YES §6.8. Rendering the failed brief is an addition (operator convenience). |
| 3.14 | **Guard block alert** | To `trushil.jani@1440sports.com`; subject `1440 Intelligence — Brief BLOCKED — {company} — {d MMM yyyy}`; body: company, brief number, score, execution mode, signals rows read, `JSON` of `_guard.blocks` (rule + detail per block: `blocked_non_production_execution`, `blocked_trigger_not_fired`, `blocked_signals_log_unreachable`, `blocked_duplicate_30d`, `blocked_score_below_threshold`, `blocked_audit_not_passed`), and "re-run from 1440 Builder — Render PDF to force a send". Guard rows also go to the Audit Log sheet. | No equivalent event: dedup / threshold happen at triage and appear in the run summary and `/ops`; the operator email covers verification-blocked, needs-review, run failure and no-signal. | §7 lists the operator notices; a "dedup-blocked" notice is not among them. **NO** (minor) — decide whether a suppressed-duplicate should raise an operator email. |
| 3.15 | **Manual-review alert** | Subject `⚠️ 1440 Brief NEEDS MANUAL REVIEW — {company} ({brief_number})`; body: company, number, team, score, violations JSON, "re-run from Render PDF if you choose to send". | Operator email with audit status, attempts and the violation list; PDF attached. | YES §7. |
| 3.16 | **Send Brief** | Recipients `trushil.jani@1440sports.com, trushiljani27@gmail.com` — **the MD is not on the export's distribution**. Subject `1440 Intelligence Brief — {company} — {d MMM yyyy}`; plain-text body with score/tier, person (role), horizon. PDF from the Railway builder. | §7 subject `… N° {n} — {Company} — {score}/100`, three-line take + app link, MD only in production mode. | YES §7. |
| 3.17 | **Log Signal / Read Daily Signals** | `Date` = `signal_date` from the writer's SIGNAL_DATA (model-authored; may be the article date). If SIGNAL_DATA is missing, Parse Claude Response substitutes `footer_date` ("14 JUN 2026"), which the guard's `parseDateMs` cannot parse → row ignored → that company's duplicates pass the guard. | DB rows with real timestamps. | YES §5 / §3.5. (Production latent bug.) |
| 3.18 | **Freshness** | None in code (prompt asks for "past 7-14 days"; gate 2 says 12 months). | Date arithmetic: 14 days Track 1, 90 days alumni, before scoring. | YES §3.3 / §6.2. |
| 3.19 | **Gate 5 saturation cap / alumni boost** | Prompt-only (scanner applies both itself; alumni list of 5 names hard-coded in the prompt). | `preflight` sponsor-identity check caps at 70; alumni boost recomputed from the `alumni` table **on top of** the scanner's dimensions. If the scanner already folded the boost into its dims (the v218 `urgency_or_alumni` field suggests it does), Python double-counts. | §6.4 says record the boost; whether the scanner's own boost is stripped first is not stated. **NO** — tied to 2.1. |
| 3.20 | **Parser** | Bracket-depth balanced, not string-aware; largest region first; prefers a first element with `company`; falls back to any object array; strips code fences on failure. | String-aware depth scan; first parseable array in document order. | YES §6.1 / §9.6. |
| 3.21 | **Audit before/after dedup** | Audit (and retry) run before the guard. | Dedup at triage, before writing. | YES §6.3 (structural dedup). |
| 3.22 | **Audit log persistence** | Every audit and guard row appended to the "Audit Log" sheet. | Violations stored on `briefs.audit_violations`; `AuditResult.log_rows()` reproduces the sheet rows but nothing persists them. | §5 has no audit-log table; `/ops` reads `audit_violations`. — |

## 4. Silent differences needing a human decision (summary)

1. **Scanner scoring scale (2.1 / 3.19):** the production scanner prompt says 4 × 0-25 with
   `urgency_or_alumni`; the writer and the Python contract are 5 × 0-20 with `ops_fit`. Restore the
   2.1.3 scoring block in the scanner prompt, or change the contract (MD approval, §0.5).
2. **Saturday FE-forcing (3.1):** production forces FE on Tue/Fri/**Sat**; the brief and Python say Tue/Fri.
3. **Re-ranking by recomputed score (3.2):** production trusts the scanner's order; Python re-sorts.
4. **What counts as "surfaced" (3.7):** production cools any *selected* candidate; Python only an *issued* brief (incl. audit-failed).
5. **Manual runs in production mode (3.9):** production never lets a non-cron execution reach the MD; Python's mode is a deployment flag.
6. **Blocklist matching (3.4 / 3.6):** production's substring match and wider suffix list (`ai`, `labs`, `group`, `co`…) vs the brief's exact list — "Sierra Space", "Exa Labs" behave differently.
7. **Retry message content (2.6):** production feeds the failed draft back with the violations; Python feeds violations only.
8. **Dedup-blocked operator notice (3.14):** production emails a guard-block alert; Python logs it to the run summary only.
9. **Export housekeeping (3.11 / 3.16 / 3.12):** the exported cron is 21:47 daily and the MD is not on the send list — confirm whether the export reflects the intended live state; and the brief-number counter must be carried over by hand at cut-over.
