# 1440 Sports — Product & Business Assessment
*Prepared as an operator's read (CEO/CFO/BD lens). Date: 2026-05-30.*

This is the honest version, not the pitch version. I separate **what we have**,
**is it an MVP**, **can it be a business**, **the numbers**, and **what to change** —
in that order.

---

## 1. What we actually have today

A well-engineered **vertical prototype** of a sponsorship-prospecting pipeline:

- A deterministic **scoring model** (5 pillars × /20 → /100) with eligibility
  gates (series, ≥3-yr, already-on-grid, oversaturation).
- A **cadence** that emits **one curated "hero" brief per day** (3 FE / 3 F1 / 1
  decision), brand-locked to a 2-page format.
- A **trust layer** I just built: live-verification discipline, claim-level
  citations (`key_facts`), freshness/decay, and a **team-fit/conflict engine**
  that blocks category-exclusivity overclaims.
- ~**18 hand-curated prospects** (11 F1, 7 FE), one fully live-verified (Cohesity).

Read that list carefully. The **engine and the editorial standard are real and
unusually polished**. The **data is a hand-built sample**, the system is
**single-tenant** ("1440", one recipient), and **discovery is mostly manual**.
That distinction drives everything below.

---

## 2. Is it an MVP?

**Not yet a sellable MVP — it is a strong "concierge-MVP / demo-ready slice."**

An MVP has to let a *paying stranger* get value without me in the loop. Today the
value depends on a human (me) curating and verifying prospects, and the output
goes to one hard-coded brand. That's a **proof-of-concept**, not a product a
customer can self-serve.

The good news: it's the *right kind* of prototype. It's polished enough to win
design-partner meetings and to run as a **concierge service** (deliver the
output manually to 3–5 customers while the product catches up). To become a true
MVP it needs four things (see §5): **multi-tenant config, automated discovery at
scale, outcome tracking, and 2–3 paying design partners**. That's weeks, not
quarters — but it isn't done.

**Verdict: ~60% of the way to an MVP. The hard, differentiated part (judgment +
verification + matching) exists; the boring scale plumbing does not.**

---

## 3. Can we sell it / build a scalable business?

Yes — **but not as "another sponsorship data platform."** That lane is taken.
[SponsorUnited](https://www.sponsorunited.com/) already does **~$70.6M revenue**,
~450 staff, and tracks **350K sponsors / 700K deals**
([getlatka](https://getlatka.com/companies/sponsorunited),
[crunchbase](https://www.crunchbase.com/organization/sponsorunited)). We will
never out-data them, and we shouldn't try.

**Our wedge is the last mile they don't own: decision-ready, verified,
conflict-checked, team-matched briefs — an "AI sponsorship BD analyst," not a
database.** SponsorUnited tells you *who exists*; we tell you *who to call this
week, why now, which team, and hand you the brief to send* — with the facts
checked and the category-clash risk flagged. That judgment layer is the
defensible bit, and it's exactly what we built.

The market is large and tailwind-rich:
- Global sports sponsorship: **$64.1B (2024) → $144.9B (2034), 8.5% CAGR**
  ([market.us](https://market.us/report/sports-sponsorship-market/)).
- F1 sponsorship alone: **$2.54B in 2025 (+22%), heading past $3B in 2026**; the
  **tech sector is $769M of that, +40.8% YoY**
  ([the-race](https://www.the-race.com/formula-1/f1-sponsorship-two-and-a-half-billion-2025-nfl-gap-slashed/),
  [thestreet](https://www.thestreet.com/retail/why-f1-sponsorship-boom-is-nearing-3-billion-formula-1)).
  Our entire seeded pipeline (B2B tech → motorsport) sits in the fastest-growing
  slice of the fastest-growing major sport.

**Three viable business models** (pick a primary, keep one as upside):

| Model | What you sell | Pricing analog | Margin | Scalability | Risk |
|---|---|---|---|---|---|
| **A. Vertical SaaS** ("AI BD analyst") | Self-serve verified pipeline + briefs, per-tenant | ZoomInfo $15–140K/yr; Apollo $49–119/seat/mo | High (70–85%) | High | Needs data/discovery infra; long-ish sales cycle |
| **B. Productized service / concierge** | We run the engine, deliver briefs as a managed feed | Sponsorship retainers $5–12K/mo ([Power Sponsorship](https://powersponsorship.com/how-much-should-you-pay-a-sponsorship-broker/)) | Medium (50–65%) | Medium (people-gated) | Doesn't scale past ~human capacity without productizing |
| **C. AI-enabled brokerage** | We source + broker deals, take commission | 10–30% of deal, + retainer | Very high per deal, lumpy | Low–Med | Relationship/luck-driven, long cycles, founder-dependent |

**Recommendation: start B → graduate to A, hold C as opportunistic upside.**
Concierge first to get *outcome data* and refine the ICP with near-zero product
risk; productize into SaaS once 3–5 customers prove what they'll pay for; let any
broker commissions be gravy, not the plan (lumpy revenue scares investors and
cash flow).

**Who pays (ICP, in priority order):**
1. **Sponsorship sales agencies** (RTR, Wasserman rights-sales, Two Circles,
   boutiques) — they live on deal flow and would pay for qualified prospecting.
2. **Mid-tier / new teams** (Cadillac's 2026 entry, FE teams, F2/F3, WEC,
   IndyCar) that lack a big commercial team and can't get a top broker to take
   them on retainer.
3. **Brand-side BD teams** evaluating *which* property to back (smaller segment).

---

## 4. Realistic numbers

Conservative, operator-grade — not hockey sticks. The addressable buyer count in
pure motorsport is **small** (~10 F1 + ~11 FE teams, plus a few hundred other
properties and ~100–200 relevant agencies). That caps the *motorsport-only* SaaS
TAM at perhaps **$15–40M/yr** — fine for a profitable boutique, thin for a
venture outcome. The upside case requires broadening beyond motorsport.

**Base case — disciplined niche execution:**

| Horizon | Motion | Customers | ACV | ARR |
|---|---|---|---|---|
| Year 1 | Concierge / design partners | 3–8 | $30–60K | **$120–350K** |
| Year 2 | Early SaaS, motorsport niche | 15–40 | $15–30K | **$350K–1.0M** |
| Year 3 | SaaS + light services, niche maturing | 40–90 | $18–35K | **$1.0–2.5M ARR** |

**Upside case — broaden to all sports / all sponsorship categories** (the
SponsorUnited-adjacent path): **$5–15M ARR in ~5 years** is *possible* but needs
real data infrastructure, ~$3–8M of capital, and a team. SponsorUnited took ~10
years and ~$40M raised to reach $70M revenue — that's the ceiling-shaped comp.

**Brokerage upside (Model C), illustrative:** broker even **$10–30M** of new
sponsorship/yr at 12–15% = **$1.2–4.5M** commission — high-margin but lumpy and
relationship-bound. Treat as a kicker, not the forecast.

**My realistic "good outcome" call:** a **$1–3M ARR profitable vertical business
in ~3 years**, optionally with a brokerage kicker — *attractive as a bootstrapped
/ lightly-funded company, sub-scale as a classic VC bet* unless you commit to the
horizontal expansion.

---

## 5. What I'd change (priority order)

**Must-do to reach a real MVP:**
1. **Multi-tenant.** Turn "1440" into a tenant: each customer gets their own
   team relationships, target categories, inventory, brand on the brief, and
   recipient list. This is the single biggest gap between "demo" and "product."
2. **Automated discovery at scale.** 18 hand-seeded prospects won't sell. Wire
   the scorer to live signal sources — funding rounds, exec hires (new CMO =
   buying signal), IPO filings, ad-spend/marketing-hiring signals — so the
   pipeline refreshes itself. This is the hardest engineering work and the real
   moat alongside verification.
3. **Outcome tracking.** Log brief → open → meeting → deal. This becomes your
   sales proof *and* your proprietary data asset ("our signals convert at X%").
   Nothing else compounds defensibility as fast.
4. **2–3 design partners under paid pilots.** Validate ICP and willingness-to-pay
   before building more. Charge from day one, even if small — free pilots don't
   tell you anything.

**Should-do for durability:**
5. **Defensible, licensed data sourcing** at scale (avoid scraping liability;
   the verification layer is your differentiator — protect its inputs).
6. **Broaden the signal beyond "one brief/day."** The daily ritual is great
   retention UX but thin as the *whole* product — add a searchable pipeline,
   saved targets, alerts, and CRM/export so it's a workspace, not a newsletter.
7. **Pricing experiments anchored to value.** A single 3-yr F1 deal is worth
   millions; $25–50K/yr is a rounding error to the buyer. Don't underprice.

**Watch-outs (the things that kill this):**
- **Buyer concentration & relationship-driven market** — few teams, agencies may
  view you as competitive. Sell *to* agencies, not around them, early.
- **Data-accuracy liability** — one confidently-wrong brief loses a logo client.
  The trust layer mitigates this; never relax it.
- **Founder-dependent curation** — if the quality lives in one person's judgment,
  it doesn't scale and isn't sellable. Encode the judgment (we started: scoring,
  team-fit, verification gates) until the engine, not a person, is the product.
- **"AI hype" discount** — buyers in this space trust relationships over models.
  Lead with *verified outcomes*, not "AI."

---

## Bottom line
- **MVP?** Not yet — a strong concierge-MVP / demo, ~60% there. The differentiated
  half exists; the scale plumbing doesn't.
- **Sellable / scalable?** Yes, as a **vertical "AI BD analyst,"** not a data
  platform. Start concierge, productize to SaaS, keep brokerage as upside.
- **Numbers?** Realistic **$1–3M ARR in 3 years** in the niche; **$5–15M in ~5
  years** only if you broaden beyond motorsport and raise to fund data infra.
- **Biggest unlock:** multi-tenant + automated discovery + outcome tracking +
  paid pilots. Do those four and you have a real company; skip them and you have
  an excellent demo.
