# Phase 3a — Crunchbase Pro Integration

**Status:** Unblocked 21 May 2026 (Crunchbase Pro credentials confirmed)
**Predecessor:** Phase 2.1 (5-dim × /20, /100 cap) — live
**Successor unblocks:** Phase 3b (CRM integration), Phase 4 (NEWCO Track)

---

## What changes when Crunchbase wires in

Today (Phase 2.1), the **Anthropic — Run Signals** scanner does two things in one pass: it searches the web for triggers, and it eyeballs valuation/funding figures from whatever Tier 1 article it surfaced. That coupling means the Gate 3 capacity check ("≥ $1B valuation OR ≥ $100M ARR") relies on whatever number happens to be quoted in the article the scanner picked — which is often a 6-12-month-old figure, sometimes a TechCrunch headline rounded for effect, and occasionally a number invented to fit the narrative.

Phase 3a separates the two passes: **capacity ground-truth comes from Crunchbase, narrative trigger comes from web search**. The scanner's job becomes finding the trigger; Crunchbase's job becomes confirming the capacity. The two streams meet at the scoring stage and feed the same `score_breakdown` object.

Net effect: Gate 3 stops being a heuristic and starts being a structured lookup. Confidence Card row 3 ("Funding / valuation figure") gets a real freshness signal instead of a manual gut check.

---

## API endpoints used

Phase 3a uses the Crunchbase v4 REST API. Three endpoints carry the load:

### 1. `/entities/organizations/{uuid}` — company core
Single GET per candidate. Returns the structured company record. Fields we consume:

| Crunchbase field | Used for | V2.1 dimension |
| --- | --- | --- |
| `properties.short_description` | Industry meta line for the brief | brief metadata |
| `properties.location_identifiers` | City for industry_meta | brief metadata |
| `properties.valuation` (when public) | Gate 3 capacity check | CAPACITY |
| `properties.last_funding_total.value_usd` | Recent raise visible? | CAPACITY |
| `properties.last_funding_at` | Freshness of capacity figure | Confidence Card |
| `properties.num_employees_enum` | Headcount scale | CAPACITY tiebreaker |
| `properties.revenue_range` | ARR band when private | CAPACITY |
| `properties.operating_status` | Active vs dormant | gate 0 |
| `properties.website` | Sanity cross-check | source verification |
| `properties.updated_at` | Last_updated stamp for the Card | Confidence Card |

### 2. `/entities/organizations/{uuid}/cards/funding_rounds` — round history
Single GET per candidate, sorted by `announced_on` desc, limit 5. Returns the funding-round timeline. Fields:

| Field | Used for |
| --- | --- |
| `announced_on` | Time-since-last-raise — feeds URGENCY (recent raise = brand-reckoning window) |
| `money_raised_usd` | Round size — feeds CAPACITY |
| `investor_identifiers[]` | Investor list — feeds investor-overlap intelligence |
| `funding_type` | Series A vs C vs Growth vs Debt — informs deal-architecture tier |

### 3. `/entities/organizations/{uuid}/cards/event_appearances` and `/jobs` — exec change events
Single GET per candidate. Returns CXO transitions. Fields:

| Field | Used for |
| --- | --- |
| `properties.title` | Match against alumni database |
| `properties.started_on` | Recency of hire (12-month gate) |
| `person_identifiers` | Cross-reference against alumni database for warm-intro paths |

The `/searches/organizations` endpoint is **not** used at the gate stage — we already have a candidate name from the web-search trigger. Phase 3a does single-record lookups, not Crunchbase-native search. (Crunchbase search becomes relevant in Phase 4 when we want NEWCO discovery without a web trigger.)

---

## Candidate name → Crunchbase UUID

Crunchbase's `permalink` field is the canonical lookup key, derived from company name as URL-safe slug. The scanner already returns `company` as a string. The new node resolves it to `permalink` via:

1. Try direct slug derivation (`stripe` → `stripe`, `mistral ai` → `mistral-ai`).
2. If `/entities/organizations/{slug}` returns 404, fall back to `/searches/organizations` with the company name as `name` query, take the top result if its `entity_def_id` matches and its website domain overlaps with the trigger source URL's domain (sanity cross-check to stop confusing "Anthropic" the AI lab with "Anthropic" a defunct apparel brand).
3. Cache resolved `permalink` values in a Google Sheets tab so subsequent runs skip the search call.

---

## New n8n nodes to add

Three new nodes slot into the workflow between **Anthropic — Run Signals** and **Parse Claude Response**. Schematic:

```
6am Trigger
  → Anthropic — Run Signals   [unchanged — still 10 candidates out]
  → Resolve Crunchbase UUIDs   [NEW: code node, batch-lookup permalinks]
  → Crunchbase — Fetch Company [NEW: HTTP, parallel 10x]
  → Crunchbase — Fetch Funding [NEW: HTTP, parallel 10x]
  → Merge CB Into Signals      [NEW: code node, attach CB block to each candidate]
  → Parse Claude Response      [unchanged interface — receives augmented signals]
  → (rest of workflow unchanged)
```

### Node A — `Resolve Crunchbase UUIDs` (code node)

Reads the 10 signals array. For each candidate, derives a slug from the `company` field, checks the cached-permalinks Sheet, and outputs a parallel array of `{ company, permalink, cached: bool }`. Emits a single item with `cb_lookups` array attached. Pseudocode:

```javascript
const cached = await fetchPermalinkCache();   // returns Map<company, permalink>
const items = $input.first().json.signals;
const lookups = items.map(s => ({
  company: s.company,
  permalink: cached.get(s.company.toLowerCase()) || slugify(s.company),
  cached: cached.has(s.company.toLowerCase())
}));
return [{ json: { signals: items, cb_lookups: lookups } }];
```

### Node B — `Crunchbase — Fetch Company` (HTTP, batch)

10 parallel GET calls to `/entities/organizations/{permalink}` with the field card mask `properties.short_description,location_identifiers,valuation,last_funding_total,last_funding_at,num_employees_enum,revenue_range,operating_status,updated_at`. Auth is `X-Cb-User-Key` header pulled from the n8n credential store (key never appears in chat or workflow JSON).

For 404 responses, fall back to the search-then-match path described above. For 429 responses (rate limit), retry with exponential backoff up to 3 attempts.

### Node C — `Crunchbase — Fetch Funding` (HTTP, batch)

10 parallel GET calls to `/entities/organizations/{permalink}/cards/funding_rounds` with `order=announced_on DESC` and `limit=5`. Same auth header.

### Node D — `Merge CB Into Signals` (code node)

Joins the three streams (original signals, company data, funding data) by `permalink`. Attaches a `crunchbase` block to each signal object:

```json
"crunchbase": {
  "valuation_usd": 14000000000,
  "valuation_source": "Series C close, March 2026",
  "last_funding_amount_usd": 1700000000,
  "last_funding_type": "Series C",
  "last_funding_at": "2026-03-11",
  "days_since_raise": 71,
  "last_5_investors": ["Andreessen Horowitz", "General Catalyst", "..."],
  "headcount_band": "501-1000",
  "revenue_band": "$10M-$50M",
  "cb_updated_at": "2026-05-19",
  "cb_freshness": "<=90d"
}
```

Then re-emits the signals array with each entry now augmented. Downstream parser and brief writer consume the same structure they did before plus this new `crunchbase` block.

---

## V2.1 prompt changes (Phase 3a layer)

Both Anthropic prompts get small additions. They are *additive*, not breaking — the prompts still work without the Crunchbase block if a lookup failed, because the existing web-search-derived figures stay as fallback.

### `Anthropic — Run Signals` — Gate 3 rewrite

Replace the current Gate 3 paragraph:

> (3) Capacity — $1B+ valuation OR $100M+ ARR OR equivalent strategic scale. Sourced from the Tier 1 article; cite the figure.

with:

> (3) Capacity — $1B+ valuation OR $100M+ ARR OR equivalent strategic scale. Capacity is verified against the Crunchbase block attached to each candidate (`crunchbase.valuation_usd`, `crunchbase.revenue_band`, `crunchbase.last_funding_amount_usd`). If `crunchbase.cb_freshness <= 90d`, treat the figures as authoritative. If `cb_freshness > 90d` or the Crunchbase block is missing for this candidate, fall back to the Tier 1 article figure and flag `capacity_confidence: MEDIUM`. Cite the source (`crunchbase` or `web`) and the exact figure used.

Add to the JSON output template:

```json
"capacity_source": "crunchbase | web",
"capacity_confidence": "HIGH | MEDIUM | LOW",
"capacity_figure_used": "$14B post-money (Crunchbase, March 2026)"
```

### `Anthropic - Write Brief` — CAPACITY cell rewrite

The CAPACITY score-cell note can now reference the Crunchbase figure directly. Add to the system prompt:

> CAPACITY score-cell note should cite the specific figure used and its source. Examples (rescaled to /20 from Cerebras N°007): "$26.6B post-money (S-1/A, May 26)" or "$14B Series C (Crunchbase, 11 Mar 26)". Maximum 12 words for this cell only (other cells stay at 8).

The user-message template gains:

```
Crunchbase block:
- Valuation: {{ $json.crunchbase.valuation_usd }}
- Last raise: {{ $json.crunchbase.last_funding_amount_usd }} ({{ $json.crunchbase.last_funding_type }})
- Days since raise: {{ $json.crunchbase.days_since_raise }}
- Top investors: {{ $json.crunchbase.last_5_investors }}
- CB freshness: {{ $json.crunchbase.cb_freshness }}
```

---

## Investor-overlap intelligence (the unlock)

Crunchbase's investor data turns the engine from a single-candidate scanner into a network-aware one. Once we have `last_5_investors[]` for every candidate, we can cross-reference against:

1. **The team's investor list.** Williams Racing's ownership/investor structure is public; if a candidate's lead investor also sits on Williams' cap table, that's a warm intro path.
2. **The alumni database.** If an alumni-DB executive previously closed a deal at a team backed by a particular VC, and the new candidate is also backed by that VC, the alumni route compounds.
3. **Other in-pipeline targets.** If two active candidates share a lead investor, we can sequence the outreach (the second-mover effect — closing the second deal gets easier once the first lands inside the same investor's portfolio).

Implementation: a fourth new node, `Investor Overlap Scan`, runs after Merge CB Into Signals. It loads three small Google Sheets tabs (team_investors, alumni_deal_history, blocklist_with_investors) and emits an `investor_overlap` array per candidate. The scanner prompt reads this and adds a `warm_intro_path` field to its output JSON. The brief writer surfaces it under PRIMARY DECISION-MAKER as a "warm intro candidate" line when a strong overlap exists.

This is the highest-leverage piece of Phase 3a — and the bit that's hard to do well without Crunchbase. **Recommendation: do investor-overlap as a Phase 3a.1 follow-up two weeks after the core capacity rewire is stable, not in the same drop.**

---

## Confidence Card — new field rules

The Confidence Card has 7 rows. Phase 3a changes how three of them get filled:

| Card row | Phase 2.1 rule | Phase 3a rule |
| --- | --- | --- |
| **Funding / valuation figure** | Manual gut check on article freshness | ✅ if `cb_freshness ≤ 90d`. ⚠ if 90-365d. ❌ if >365d or CB missing and only web figure available. |
| **Investor list** | Often blank | ✅ when CB returns ≥ 3 investors. ⚠ when 1-2. ❌ when 0 or CB missing. |
| **Days since last raise** | Computed from web search if mentioned at all | ✅ when CB returns `last_funding_at`. ❌ when CB missing. |

The HIGH-confidence threshold stays at 6/7 ✅, MEDIUM at 4-5/7 with no ❌. LOW briefs are still not generated. The change is that the Card becomes more deterministic — the same target on the same day gets the same Card, regardless of which web articles happened to surface.

---

## Failure modes and fallback behaviour

| Failure | Behaviour |
| --- | --- |
| Crunchbase 404 (company not in CB) | Scanner falls back to web figures, sets `capacity_source: web`, `capacity_confidence: MEDIUM`. Card row 3 = ⚠. |
| Crunchbase 429 (rate-limited) | Node B/C retries with exponential backoff up to 3 attempts. If all fail, scanner falls back to web. |
| Crunchbase 5xx (CB service down) | Same fallback path. Workflow does not block. Slack alert posts on >50% failure rate for that day's run. |
| Stale CB data (cb_updated_at > 365d) | Scanner uses CB figure but flags `capacity_confidence: MEDIUM`. Card row 3 = ⚠. |
| Permalink resolution ambiguous (search returns 2+ matches with no clear winner) | Skip the candidate; emit warning. Better to lose a signal than to attach the wrong company's funding history to it. |

The fallback path means **Phase 3a is not load-bearing**. If Crunchbase goes down, the engine degrades to Phase 2.1 behaviour automatically. That's the right design — the daily brief still ships on a bad CB day; it just carries an honest MEDIUM confidence label.

---

## Phase 3a deployment checklist

1. ✅ Crunchbase Pro credentials confirmed (21 May 2026). API key to land in n8n credential store as `CRUNCHBASE_API_KEY` — never in chat, never in workflow JSON exports.
2. ⬜ Add the four new nodes (Resolve UUIDs, Fetch Company, Fetch Funding, Merge) to the workflow. Test against a known target (e.g. Cerebras — already in the Phase 2 calibration data).
3. ⬜ Build the permalink-cache Sheet (one tab, two columns: `company_lowercase`, `permalink`). Pre-populate with active_sponsor_db.md entries (40-50 rows) to skip the first-day search calls.
4. ⬜ Update the two Anthropic prompts with the Phase 3a additions documented above. Push to the workflow JSON.
5. ⬜ Run a shadow week: scanner emits both web-derived and CB-derived capacity figures into the Google Sheets log without changing the brief. Compare for systematic drift. Adjust the prompt's `capacity_confidence` thresholds based on what shadow-week reveals.
6. ⬜ Cut over: the brief CAPACITY cell reads CB-first, web-fallback. Slack alert added for CB failure rate >50%.
7. ⬜ Plan Phase 3a.1 (investor-overlap) for ~14 days after cut-over once the capacity path is stable.

---

## What Phase 3a unblocks

- **Phase 3b (CRM integration).** Once Crunchbase identifiers are stable in the workflow, mapping them to Salesforce/HubSpot account IDs becomes a 1-2-day job. The CRM stop-gap was previously the absence of a canonical ID; CB permalinks fill that gap.
- **Phase 4 (NEWCO Track).** The NEWCO play depends on watching for M&A close events where the acquirer is an existing F1/FE sponsor and the target is a relevant tech company. Crunchbase's `/cards/acquisitions` endpoint feeds that watcher. Without Phase 3a, the NEWCO Track has no data source.
- **Deeper investor-overlap intelligence.** Phase 3a.1 (above) is the immediate next step; longer term, a "VC-portfolio heatmap" view becomes possible — showing which VCs have the densest concentration of qualified targets, suggesting which VCs to build direct relationships with.

---

## Update history

- **21 May 2026.** Phase 3a scope drafted. Crunchbase Pro credentials confirmed. Implementation order: capacity rewire first (this doc), investor-overlap second (3a.1), NEWCO/CRM third (3b, Phase 4).
