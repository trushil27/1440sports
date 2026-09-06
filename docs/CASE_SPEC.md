# Building a full case from a case spec (no API key)

A **case spec** is a JSON file that supplies what the pipeline's three model stages would
otherwise produce — the scanned signal, the evidence behind every claim, and the written
brief — so that `python -m intel.session_case` can run the CODE stages unchanged (freshness,
dedup, scoring, the claims ledger with the calendar + sponsor-table checks, the 13-rule
audit, the strict 2-page render, the app page) and store the result as the same case record
(`pipeline/intel/cases/<date>/<stem>.run.json` + `.pdf` + `.html` + `.web.html` +
`.verification.md`) the desk app and `intel.backfill --cases` understand.

The worked example is `pipeline/intel/cases/2026-09-06/fluidstack.case.json` (N° 127,
today's signal on 6 Sep 2026). Copy its shape exactly.

```bash
python -m intel.session_case spec.json check        # audit + word ceilings + claim coverage
python -m intel.session_case spec.json build        # temp Postgres → case record in cases/
```

`check` must print `audit route: pass` and `uncovered: 0` before `build`. `build` starts a
throw-away Postgres (needs the local server binaries; ~2 min), loads the repo's memory,
runs the day in rebuild mode and exports the record. Exit 0 = verified case written;
2 = a claim had no evidence (fix the spec, do not ship); 3 = a claim was contradicted by the
calendar or sponsor table (a phantom race or a wrong "Brand at Team": fix the copy).

## The standard (non-negotiable, from CLAUDE.md)

- **Re-verify, don't recall.** Every figure, name, date and title comes from a live source
  you actually opened or a search summary of the primary page. Never from memory.
- **Never invent.** No guessed CMOs, CFOs, valuations, races or partner names. If a fact is
  not sourced, leave it out or say GAP. "Reported" facts (press, not company) say *reported*
  in the copy and in `note`.
- **Verified decision path**: the real sponsorship owner from the company's own leadership
  page (CEO / CMO / commercial lead), plus the path (president / COO / CFO). If there is no
  CMO listed, say so.
- **Real grid occupancy only.** Team fit and "the lane is open" are judged against
  `pipeline/intel/seeds/sponsors.json` (the sponsor table) — never against other 1440
  prospects. Name the teams ruled out and why.
- **Real workstream (MODE A) or honest halo (MODE B)** in `value_content` — concrete
  mechanics the *specific* team would use; never vague.
- **Honest score.** Say what holds it back. Do not inflate to reach 70.
- **Screen-outs are the product.** If research shows the signal is wrong (fact contradicted,
  company already a partner of a team, event never happened, stale beyond 90 days of the
  row's date), do NOT build a case: write
  `pipeline/intel/cases/<date>/<stem>.screened.json` —
  `{"company", "date", "verdict": "contradicted|existing_partner|stale|duplicate_of",
  "reason", "sources": [urls]}` — and move on.

## Spec fields

| Key | What |
|---|---|
| `run_date` | The date the row sits on in the desk (the brief is issued for that day). |
| `signal_date` | The trigger's date (ISO). Must be within 90 days before `run_date`. |
| `stem` | File stem, lowercase ASCII letters/digits (`formenergy`). |
| `number` | The brief number assigned to you for this company (given in the batch). |
| `session_model` | `claude-session-<today>`. |
| `signal` | The scanner output: see below. |
| `evidence` | List of `{needles, url, excerpt, method}`: see below. |
| `brief` | The written brief: see below. |
| `note` | Markdown verification log: what was checked, what is only REPORTED, screen-outs, decision path, leadership ties (say `none found` after checking). |

### `signal` (ScannedSignal)

`company`, `signal_date`, `score` (0–100), `tier` (HOT/WARM), `track` (1), `person`, `role`,
`horizon_weeks` ("6-10"), `source_url` (the trigger's primary source), `industry_meta`,
`recommended_team` (exact display name from `seeds/team_profiles.json`),
`recommended_series` (F1/FE), `timing_label` (HOT/WARM/WATCH), `trigger_reason` (short),
`key_facts` {`funding`, `investors`, `revenue` ("" if none public), `trigger`,
`competitor_signal`, `strategic_hook`, `us_presence`, `alumni_match` (""),
`taxonomy_category`, `ops_fit_note`}, `score_breakdown` {`timing`, `capacity`, `brand_fit`,
`urgency`, `ops_fit` (each /20), `ops_fit_subscores` {`product_to_need`, `slot_availability`,
`on_camera`, `lock_in`}}, `of_gate_passed` (true), `confidence_level` (MEDIUM/HIGH; LOW fails
the audit).

Every non-empty `key_facts` value becomes a **load-bearing claim** and must be covered by
evidence. Keep them factual and sourced; put nothing in `key_facts` you cannot cover.

### `evidence`

Each entry: `needles` (lower-case substrings; a claim is covered when ANY needle appears in
its text — use distinctive tokens such as `"$550m"`, `"g2 venture"`, `"series c"`, the
person's surname, `"30 jul"`), `url` (the primary page), `excerpt` (what that page states,
in your words, with the figures), `method` (`manual`; use `sponsor_db` / `calendar` for
table-backed entries). Entries are tried in order: put the specific ones first.

`check` lists every claim the ledger extracts: the decision-maker line, every `key_facts`
value, the trigger, and every sentence with a money/percentage figure in `deck`,
`the_case_p1/p2`, `why_now_callout`, `bottom_line` and the `extended.*` texts. Race
mentions ("British GP", "Austin round") and "Brand at Team" sponsorship sentences are checked
against the tables at build time — a race that is not on the 2026 calendar, or a partner
not in the sponsor table, blocks the case.

### `brief` (WrittenBrief) — the 2-page format

Rule 7 word ceilings (JS word count, +5 grace): `deck` 50 · `the_case_p1` 95 ·
`the_case_p2` 75 · `why_now_callout` 55 · `why_team_para` 85 · `value_content` 75 ·
`deal_arch_para` 70 · `decision_maker_bio` 50 · `opening_angle_intro` 18 ·
`opening_angle_quote` 45. Page-2 character budget (why_team + value + deal + bio + intro +
quote + risks): **2300** with the value section (2100 without). Trim copy until `check`
passes — the renderer refuses a third page.

Other audit rules: `deal_arch_para` names **THREE YEARS** (or FOUR/FIVE) in
`<font name='Poppins-Bold' size='9.5'>THREE YEARS</font>`, never two; `opening_angle_quote`
ends with `?` and asks for "25 minutes" literally; `opening_angle_intro` is declarative;
`why_now_callout` starts `<font name='Poppins-Bold' size='9'>WHY NOW</font>&nbsp;&nbsp;`;
`footer_date` is the run date as `6 SEP 2026`; `industry_meta` set; `track_label` "";
`confidence_level` not LOW; score ≥ 70 ⇒ `value_section: true` with `value_content`
(MODE A operational / MODE B halo) and exactly **2** `risks` (3 without the value section);
no 5-word phrase shared between `the_case_p2` and `why_team_para`; do not write "<Team> is the
only team …" / "<Team> has no …" vacancy claims in `the_case_p2` or `deck` (say it in
`why_team_para` from the sponsor table).

Fields: `brief_number` (""), `track_label` (""), `company`, `industry_meta`, `hq`, `ticker`
(or "Private (…)"), `deck`, `score`, `timing_label`, `series_label`, `team_label`,
`horizon_label` ("6-10 WKS"), `hot_top_tier` (false), `confidence_level`, `the_case_p1`,
`the_case_p2`, `why_now_callout`, `why_team_label` ("WHY <TEAM UPPER>"), `why_team_para`,
`value_section`, `value_section_label` ("VALUE TO <TEAM UPPER>"), `value_mode` ("A"/"B"),
`value_content`, `deal_arch_para`, `decision_maker_name`, `decision_maker_role`,
`decision_maker_bio`, `opening_angle_intro`, `opening_angle_quote`, `score_cells` (5 rows
`[LABEL, "17", "/ 20", rationale]`), `risks` (`[TITLE, detail, counter]`), `bottom_line`,
`signals` (tags), `footer_company` (UPPER), `footer_date`, `extended` {`why_now` [4 ×
{label, text}], `why_team` [4], `value` [4], `ruled_out` [{team, reason} for every
conflicting team], `ask`}.

`extended` is the app page (no word ceiling; business language; figures still go through
the ledger, so cover them with evidence too).

## Workflow for one company

1. Read the row (company, date, series, team, trigger, person) from your batch.
2. Research live: trigger (primary source + one credible secondary), funding history,
   leadership page (decision maker + path), motorsport ties of the leaders, US presence,
   category rivals on the grid (`seeds/sponsors.json`, grep the category), the team's roster.
   About 15 searches per company; open primary pages where the proxy allows.
3. Decide: build, or screen out (write the `.screened.json`).
4. Write the spec; run `check` until READY; run `build`; open the PDF pages (PyMuPDF
   `page.get_pixmap()`) and look at both pages once.
5. Commit only `pipeline/intel/cases/<date>/<stem>.*` (record, pdf, html, web.html,
   verification.md, case.json / screened.json). Never commit secrets or scratch files.
