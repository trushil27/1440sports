# 1440Sports Sponsorship Intelligence — Complete Skill Bundle

State as of **22 May 2026**. **Phase 2.1.8 deployed** — VALUE TO [TEAM] section with three content modes, 13-rule audit with retry loop, FE rotation Tue/Fri, full-grid team matching, three-year deal minimum. Phase 3a (Crunchbase) scoped; Phase 3b (Salesforce, confirmed) and Phase 3c (passive executive tracking) drafted in roadmap.

## Folder Layout

```
1440-sponsorship-intelligence/        ← the skill itself
├── SKILL.md                            ← entry point; Claude reads this first
├── references/                         ← detailed prompts and data
│   ├── v21_prompt.md                   Track 1 scoring prompt (5 dims × /20, /100 cap)
│   ├── v22_alumni.md                   Track 2 alumni intelligence layer
│   ├── pdf_brief_template.md           Brief format spec (Phase 2.1.8 — VALUE TO [TEAM])
│   ├── active_sponsor_db.md            F1/FE sponsor database — the anti-hallucination spine
│   ├── team_needs_taxonomy.md          F1/FE operational needs map
│   ├── alumni_database.md              5 strict-tier confirmed
│   ├── blocklist.md                    Active deal pipeline — USER MAINTAINS
│   ├── scoring_calibration.md          24 historical /100 signals + calibration table
│   ├── brand_voice.md                  How 1440 communicates
│   ├── production_roadmap.md           Build path: Phase 0 through Phase 5 (current = 2.1.8)
│   ├── n8n_v21_prompts.md              Node-by-node n8n prompt replacements (current = 2.1.8)
│   └── phase3a_crunchbase_scope.md     Phase 3a Crunchbase implementation plan
└── assets/
    ├── build_brief_template.py         Local one-shot PDF builder
    └── 1440_logo.png                   Brand logo — transparent RGBA 4000×700

railway-builder/                       ← separate — for Railway deployment
├── builder.py                            Function version of the PDF builder (Phase 2.1.8 — VALUE TO [TEAM])
└── 1440_logo.png                         Same transparent RGBA logo
```

## Where to Put These Files

### 1. The skill folder
Upload all files to the Claude project's file area. Folder structure may flatten — file names alone are enough.

### 2. The Railway builder files
`railway-builder/builder.py` and `railway-builder/1440_logo.png` go into the Railway-connected Git repo. Replace existing files. Commit and push. Railway auto-redeploys in ~60-90s.

### 3. The n8n workflow
The Anthropic node bodies (`Anthropic — Run Signals` and `Anthropic - Write Brief`), Parse Signal Data code, Audit Brief code, Retry Prep code, and Format Audit Log Rows code need replacing with the Phase 2.1.8 versions documented in `references/n8n_v21_prompts.md`.

Also required: the Audit Route switch node configuration, Google Sheets — Audit Log node, Google Sheets — Cooling List Mirror node, Outlook — Operator Manual Review Alert node. Wiring diagram in production_roadmap.md.

## What Changed Since the Previous Bundle

### Phase 2.1.3 — Anti-Duplication + Date Hygiene
- Anti-duplication self-check in brief writer (deck, p1, p2, why_now must not contain the WHY [TEAM] claim).
- Anti-hallucination rules hardened (£100 test, dated figures, anchored percentages, named investors, no hollow adjectives, quantified reach, venue specificity).
- footer_date always TODAY; industry_meta strips trailing date.
- FE quota enforced at scanner level (≥3 of 10).

### Phase 2.1.4 — Dedup Visibility
- Parse Signal Data revisit fallback rewritten in three tiers.
- Cooling list mirrored to Google Sheets "Cooling List" tab via new parallel nodes.

### Phase 2.1.6 — Full-Grid Team Matching
- Scanner rewritten to walk all 11 F1 teams + current FE teams per candidate.
- Explicit prohibition on default reasoning ("Williams = engineering heritage" etc.).
- Audi, Cadillac, Haas, Alpine, Racing Bulls named with documented open category gaps.
- Verified live: non-default teams (Jaguar TCS Racing, BWT Alpine, NEOM McLaren, Audi) regularly surface.

### Phase 2.1.7 — Autonomous Audit + Retry Loop
- New nodes added: Audit Brief, Audit Route, Format Audit Log Rows, Retry Prep, Google Sheets — Audit Log, Outlook — Operator Manual Review Alert.
- Wiring: Parse Claude Response → Audit Brief → Audit Route → {pass/retry/manual_review}.
- Retry budget: 1. Failed retries route to operator review, never to MD.

### Phase 2.1.8 — VALUE TO [TEAM] + Audit Refinement (current)
- **WHERE THE TECH FITS renamed to VALUE TO [TEAM]** (dynamic label).
- **Three content modes by archetype:**
  - MODE A operational (on-car/factory/broadcast) for OF ≥ 14.
  - MODE B commercial back-office (paddock settlements, treasury) for OF 11-13 or fintech/payments/insurance.
  - MODE C audience/brand-pipeline (user base demographics, race-weekend activation) for OF ≤ 10 + consumer/lifestyle/media/B2C.
- **Renders at score ≥ 70.** Below 70 the section is suppressed.
- **Deal architecture minimum: THREE YEARS** (no two-year option).
- **Deck rule hardened:** no team-vacancy claims in deck; team named only as destination; if unsure, no team in deck.
- **FE rotation:** Tuesdays + Fridays force FE if eligible; Mon/Wed/Thu/Sat/Sun pick by score.
- **13-rule audit:** deal duration, opening quote, opening intro, footer date, industry meta, team-vacancy proximity in deck/p2, word counts, confidence level, track label, risk count, page-2 char budget, value section required at ≥70, phrase overlap p2/why_team_para.
- **Regression-tested** against four real briefs (Datadog passes; Strava/Nscale/Primer correctly flagged).

## Next Steps

1. Verify Railway redeploy of `builder.py` lands cleanly (section header reads VALUE TO [TEAM]).
2. Decide weekend behaviour — workflow now runs Sat/Sun; FE rotation rule doesn't cover them.
3. Begin Phase 3a Crunchbase build per `references/phase3a_crunchbase_scope.md`.
4. Scope Phase 3b Salesforce integration (user has access; need API auth design + object mapping).
5. Scope Phase 3c passive executive tracking architecture (data sources, legality review, convergence trigger logic).

## Future Phases

- **Phase 3a:** Crunchbase Pro integration — replaces Gate 2 web-search heuristics with structured API data.
- **Phase 3b:** Salesforce CRM integration (user has access).
- **Phase 3c:** Passive executive tracking — conferences, events, board appointments, patent co-filings, GitHub activity. Convergence detection across signals over 90-day windows.
- **Phase 4:** NEWCO / Spinoff Track V2.3 — catches new billion-dollar entities at brand-formation moment.
- **Phase 5:** Convergence Intelligence V2.4 — emerges from Phase 3c data accumulation as standalone track.

Full plan in `references/production_roadmap.md`.
