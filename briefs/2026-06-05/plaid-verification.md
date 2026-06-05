# Plaid — verification log (2026-06-05)

Hero for 2026-06-05 (FE, by MD request — Mistral excluded). Every load-bearing
claim re-checked live before rendering. Format: claim → status.

| Claim | Status | Source |
|---|---|---|
| Valuation | **CORRECTED — STALE** ~$6.1B → **~$8B** (Feb 2026 tender offer, +31%) | Crunchbase; FinTech Futures; TechFundingNews |
| $575M secondary at $6.1B (prior round) | **VERIFIED** | FinTech Magazine; This Week in Fintech |
| "IPO 'very likely' 2026" | **CORRECTED — OVERCLAIM** → IPO-track but CEO Perret sees conditions unfavourable; no S-1 filed | TechFundingNews; Crunchbase |
| CMO Hannah Hughes (joined 2026) | **VERIFIED** | Hughes' own appointment announcement |
| President Jen Taylor (ex-Cloudflare CPO) | **VERIFIED** | Plaid blog; FinTech Futures |
| Co-founder & CEO Zachary Perret | **VERIFIED** | TechFundingNews; Plaid |
| HQ San Francisco | **VERIFIED** | multiple |
| Decision-maker resume detail (Cash App/Affirm/etc.) | **TRIMMED — UNVERIFIED** | could not re-confirm this session; removed from bio rather than assert |
| **Recommended team Jaguar — category clash** | **CORRECTED — RE-POINTED** | Jaguar signed **Chase as Official Financial Services Partner (2025/26)** → financial lane TAKEN. TCS.com; Jaguar Racing media |
| Re-point → Andretti FE (explicit fintech open; American team; no financial partner) | **VERIFIED** | Andretti Global partners page |

## Corrections applied
1. Valuation ~$6.1B → **~$8B** (Feb 2026 tender).
2. IPO framing softened from "very likely 2026" to **IPO-track, CEO unhurried, no S-1**.
3. **Re-pointed team Jaguar TCS → Andretti FE** because Jaguar took Chase (financial
   services). Also updated `data/teams.json`: added Chase to Jaguar's roster +
   `competitor_locks: ["financial services (Chase)"]`, so the engine now flags the
   clash (Grid Fit shows Jaguar = TAKEN).
4. Trimmed unverified resume detail from the decision-maker bio.
5. Stamped verified `key_facts`, `fit_lane`/`fit_domain`, `thesis`, `last_verified`.

Score 71/100 (WARM). Trust gate clean (0 blockers, 0 warnings). 2-page locked.
Note: Glean was the engine's #1 today but is a repeat (shipped 2026-05-30 with a
dossier); Mistral was excluded by the MD — so Plaid, the top *fresh* FE prospect,
was selected.
