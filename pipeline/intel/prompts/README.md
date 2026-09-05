# prompts/ — verbatim prompt texts

Extracted programmatically: the n8n HTTP-Request node's `jsonBody` is an `={...}` expression;
strip the leading `=`, `json.loads` the rest, and write `system` and `messages[0].content` out
unchanged. The n8n template expressions (`{{ $today... }}`, `{{ $json.x }}`,
`{{ JSON.stringify($json._retry_block || '').slice(1, -1) }}`) are left in place and substituted
by `intel/scan.py` / `intel/brief.py` at run time. Do not hand-edit these files: change the
source export, re-extract.

| File | Source | Version | Used by |
|---|---|---|---|
| `scanner_v218_system.txt` / `scanner_v218_user.txt` | `spec/n8n_workflow_production_2026-09-04.json`, node `Anthropic — Run Signals` (`system` / user `content`) | **Production, live export 4 Sep 2026** (workflow `SLyZcgWP5vl6kEas`, versionId `23454442-…`); node calls `claude-sonnet-4-6`, `max_tokens` 12000, `web_search_20250305` ×10 | `intel/scan.py` |
| `writer_v218_system.txt` / `writer_v218_user.txt` | same export, node `Anthropic - Write Brief` | **Production, live export 4 Sep 2026**; `claude-sonnet-4-6`, `max_tokens` 16000, no tools | `intel/brief.py` (+ `WRITER_ADDENDUM`) |
| `scanner_v213_system.txt` / `scanner_v213_user.txt` | `spec/n8n_v21_prompts.md` NODE 1 | Phase 2.1.3 (21 May 2026) — superseded, kept for diffing | — |
| `writer_v213_system.txt` / `writer_v213_user.txt` | `spec/n8n_v21_prompts.md` NODE 2 | Phase 2.1.3 (21 May 2026) — superseded, kept for diffing | — |

## What changed 2.1.3 → production (2.1.8)

Scanner: adds the "TEAM MATCHING — FULL GRID EXPLORATION" block (eleven named F1 teams, forbidden
default-reasoning patterns, teams with the most open categories, six-step matching protocol) and
trims the FE-quota text. It also **drops** the Phase 2.1 scoring block: the production system prompt
opens with the pre-2.1 "four dimensions 0-25 each" text, its example `score_breakdown` is
`{timing, capacity, brand_fit, urgency_or_alumni}` (no `ops_fit`), and `key_facts` no longer lists
`taxonomy_category` / `ops_fit_note` — yet the production *writer* user prompt reads all five /20
dimensions plus those two key facts. The "ANTI-HALLUCINATION RULES" block of 2.1.3 is gone from the
scanner (it survives in the writer). See `docs/N8N_RECONCILIATION.md` §2.

**Run-time splice (since the first live run, 5 Sep 2026):** the model followed the regressed text
and returned `timing: 23 … urgency_or_alumni` for all ten candidates, which the /20 contract
rejects. `intel/scan.py::scanner_system_prompt()` therefore replaces, at run time, the three
regressed scoring lines and the example's `key_facts`/`score_breakdown` tail with the 2.1.3
SCORING block (gates, anti-hallucination, five /20 dimensions, OF gate, tiers) and example —
i.e. the scoring the build brief specifies (§1, §6.4). The file on disk stays verbatim; the
splice asserts its anchors so a re-extracted export that changes them fails loudly. As a safety
net `parse.ScoreBreakdown` still accepts the 4×25 shape (rescaled ×0.8, `legacy_scale=true`).

Writer: adds the DECK RULE with the Armada N°014 / Datadog N°011 calibration decks, RETRY HANDLING
(`=== RETRY MODE - CORRECTING PREVIOUS DRAFT ===`), the VALUE TO [TEAM] section with modes A/B/C,
the THREE-YEARS minimum, the three-step anti-duplication self-check, and the 2/3 risk-count rule;
condenses the anti-hallucination and fact-quality blocks to bullet form; user prompt drops the
`OF gate passed` line and carries the retry-block token.
