# prompts/ — verbatim prompt texts from spec/

Extracted programmatically (JSON-decoded) from `spec/n8n_v21_prompts.md`:

| File | Source | Version |
|---|---|---|
| `scanner_v213_system.txt` / `scanner_v213_user.txt` | NODE 1 `Anthropic — Run Signals`, `system` / user `content` | Phase 2.1.3 (21 May 2026) |
| `writer_v213_system.txt` / `writer_v213_user.txt` | NODE 2 `Anthropic - Write Brief`, `system` / user `content` | Phase 2.1.3 (21 May 2026) |

The n8n template expressions (`{{ $today... }}`, `{{ $json.x }}`) are left in place and substituted by
`intel/scan.py` / `intel/brief.py` at run time. Do not hand-edit these files: change the spec, re-extract.

Known gap: the Phase 2.1.6 full-grid team-matching rewrite and the 2.1.8 VALUE TO [TEAM] writer prompt
(production from 22 May 2026) are described in `spec/production_roadmap.md` but their text is not in the
export; these files are the latest prompt text the spec bundle contains.
