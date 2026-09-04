# spec/ — provenance

Exported 4 September 2026 from the 1440Sports Claude Project ("1440 Sponsorship Intelligence").
These files are the source of truth referenced in docs/BUILD_BRIEF.md §2. Treat as read-only reference.

Renames applied on export:
- builder__2_.py        -> builder.py          (Railway PDF builder, Phase 2.1)
- n8n_v21_prompts__3_.md -> n8n_v21_prompts.md (canonical prompts + 13-rule audit code from n8n production)

Also included beyond §2:
- production_roadmap.md, phase3a_crunchbase_scope.md, README.md (context for later phases)
- 1440_Daily_Intelligence_Brief.json (n8n workflow export — port the logic, not the wrapper)
- 1440_Intelligence_Brief_Armada_20260521.pdf (second layout reference; Datadog remains the regression target)

Freshness caveats for Claude Code:
- active_sponsor_db.md was due a quarterly re-verification on 20 Aug 2026; treat sponsor entries as needing a check before they gate a claim.
- blocklist.md and alumni_database.md are snapshots; the live blocklist is the Sheets tab and the BLOCKED notices in Outlook. Reconcile during M6 backfill.

## Added 2026-09-04 (after PR #1)
- `n8n_workflow_production_2026-09-04.json` — the LIVE n8n workflow export (18 nodes) supplied by
  Trushil: Phase 2.1.8d `Audit Brief` code, `Parse Signal Data` (6.8k chars, FE rotation),
  `Duplicate Guard` + `Google Sheets — Read Daily Signals` (the Sheets-based 30-day guard),
  `Retry Prep`, `Format Audit Log Rows`, operator alert nodes, and the production scanner/writer
  prompt bodies. Supersedes `1440_Daily_Intelligence_Brief.json` (12-node Phase 2.1 export) as the
  canonical record of what ran in production. `pipeline/intel/audit.py` is reconciled against it.
