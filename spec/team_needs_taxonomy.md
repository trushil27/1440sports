# Team Needs Taxonomy

Structured map of the genuine operational needs F1 and Formula E teams have, used by the engine to identify how a target company's product could plug into a team beyond pure brand sponsorship. This is the foundation of the Operational Fit scoring dimension introduced in Phase 2.

**Purpose:** when scoring a company, the engine cross-references its product against this taxonomy to identify which team needs it could credibly meet. A match here unlocks the "What Could Run On The Car" brief section and contributes to Operational Fit /25.

**Source basis:** team sponsor lineups in `active_sponsor_db.md` reveal who currently fills each operational slot. Where a category is empty across the grid, that's a structural opportunity. Where a category has 8+ teams filled, the slot is mature and a target must enter through a specific carve-out.

**Last refresh:** 20 May 2026 — reflects 2026 power unit shake-up (Ford with Red Bull + Racing Bulls, Honda with Aston Martin, Audi works entry, Cadillac entry, Mercedes/Ferrari/Renault carry-overs).

---

## Category A — Compute & AI

### A1. Race Strategy & Decision Support
**The need:** Live race strategy is decided in <30 seconds. Teams run pit-wall optimisers that ingest tyre wear, fuel state, weather, competitor pace and recommend stop windows. The 2026 rule changes (active aero, override modes, energy deployment strategy) make this more software-intensive than ever.

**Who currently fills this:**
- F1 championship: AWS (machine learning fan and team products)
- Mercedes: AMD (AI compute, joined as partner specifically for AI capability), Microsoft (joined 2026)
- McLaren: Google Cloud (joined 2026 — replacing Workday/cloud activation), Groq (inference)
- Red Bull: Oracle (cloud), Hexagon (engineering compute)
- Williams: Atlassian (title; collaboration ecosystem rather than strategy directly)
- Ferrari: Bitdefender (security-side), IBM (joined Ferrari recent)

**What's open:** Specialised AI inference platforms beyond Groq, GenAI-for-engineering tools, agentic systems for race-week decision flow. Aston Martin, Alpine, Audi, Cadillac, Haas, Racing Bulls all have no dedicated AI / race-strategy compute partner.

**Engine fit indicators for this slot:**
- Company sells inference / training compute / GPU access → strong fit
- Company sells generative AI for technical workflows → strong fit  
- Company sells decision-intelligence platforms → strong fit
- Company sells general business AI without engineering relevance → weak fit

### A2. Vehicle Dynamics / Multibody Simulation
**The need:** Teams simulate the car's behaviour millions of times pre-event. The simulation stack runs on commercial multibody software (IPG CarMaker, dSPACE, AVL, Ansys) plus custom code.

**Who currently fills this:** Mostly enterprise legacy tools, rarely sponsor-branded. Red Bull has Ansys publicly; most teams keep these tools internal.

**What's open:** Modern cloud-native simulation, GPU-accelerated dynamics, ML-augmented simulation. Almost no team has a sponsor in this space publicly.

**Engine fit indicators:** Physics AI companies (Luminary Cloud-style), HPC simulation platforms, digital-twin specialists.

### A3. Aerodynamics — CFD
**The need:** Every team runs CFD continuously to refine bodywork. F1 limits CFD compute hours via the Aerodynamic Testing Restrictions (ATR), making *efficient* CFD a real competitive variable.

**Who currently fills this:**
- Red Bull: Siemens (and Ansys for engineering more broadly)
- Other teams: most use Ansys, OpenFOAM, or proprietary stacks; sponsor relationships rare

**What's open:** GPU-accelerated CFD providers, mesh-AI startups, surrogate-model platforms.

**Engine fit indicators:** Engineering-simulation SaaS, AI-for-physics startups (Luminary, Genesis, NeuralConcept), HPC vendors.

---

## Category B — Engineering & Manufacturing Stack

### B1. CAD / PLM
**The need:** Teams manage tens of thousands of parts across the season. CAD + PLM + product lifecycle is the engineering team's central nervous system.

**Who currently fills this:**
- Red Bull: Siemens (NX, Teamcenter, broader Siemens stack)
- Most teams: Dassault Systèmes (CATIA), Siemens, or PTC (Creo, Windchill)

**What's open:** Modern cloud-native PLM (Onshape, OpenBOM), generative-design tools. Newer entrants underrepresented.

### B2. Additive Manufacturing
**The need:** F1 teams print hundreds of bespoke components per race weekend — bracketry, ducting, suspension prototypes, wind-tunnel models.

**Who currently fills this:**
- Alpine: 3D Systems
- McLaren: previously Stratasys (departed); now under refresh

**What's open:** Carbon (DLS technology), Markforged (composite printing), Velo3D (metal printing), Desktop Metal subsidiaries. Most teams have a 3D-print partner relationship but few are headline sponsors.

### B3. CNC / Machining / Manufacturing Execution
**Who currently fills this:**
- Red Bull: DMG Mori (machine tools)
- Williams: Komatsu (industrial machinery)
- Haas: Haas Automation (parent — the team is built around Haas CNC)

**What's open:** Modern MES platforms (Tulip, ABB Symphony, Plex), digital-thread vendors.

### B4. Composites & Materials Science
**The need:** Carbon-fibre and exotic-composite work is intrinsic; suppliers like Hexcel and Toray have legacy relationships but rarely sponsor-branded.

**What's open:** Sustainable-composite startups (flax-based, bio-resin), recycled-carbon scaleups. Major opening on FE side given materials angle of championship.

---

## Category C — Data & Software Infrastructure

### C1. Cloud / Hyperscaler
**Who currently fills this:**
- Championship: AWS
- Mercedes: Microsoft (joined 2026)
- McLaren: Google Cloud (joined 2026)
- Red Bull: Oracle
- Other teams: open or undisclosed

**What's open:** Sovereign cloud, hybrid cloud, specialised compute clouds (CoreWeave at Aston Martin already, joined recent — this is the model).

### C2. Cybersecurity
**Who currently fills this:**
- Mercedes: CrowdStrike
- McLaren: Cisco, Rubrik (joined 2026)
- Ferrari: Bitdefender
- Aston Martin: (SentinelOne departed; gap)
- Williams, Alpine, Audi, Cadillac, Haas, Racing Bulls: no headline cyber partner

**What's open:** Identity / zero-trust (CrowdStrike + Okta already have McLaren/Mercedes; mid-market cybersec opens at 5+ teams), SaaS security, security observability. Strong fit for Series C-D cybersec scaleups.

### C3. Observability / DevOps / Data Platform
**Who currently fills this:**
- McLaren: Splunk, Dropbox
- Williams: Atlassian (title)
- Racing Bulls: Confluent (data streaming), Dynatrace (observability)
- Mercedes: SAP (ERP)
- Ferrari: Genesys (CX, IBM (joined recent)

**What's open:** Datadog-class observability (none on grid yet — Dynatrace at Racing Bulls is the closest), data warehouses (Snowflake/Databricks unrepresented), real-time analytics.

### C4. Identity / Productivity / Collaboration
**Who currently fills this:**
- McLaren: Okta, Workday, Dropbox, Smartsheet, Medallia, Freshworks
- Mercedes: SAP, WhatsApp (Meta), BetterUp, Microsoft (joined 2026), Meta AI (joined 2026)
- Red Bull: 1Password
- Aston Martin: ServiceNow, UKG (joined 2026)

**What's open:** Slack, Zoom, Notion, Linear all absent. Plenty of room for collaboration scaleups.

---

## Category D — Connectivity & Race-Weekend Operations

### D1. Comms / Radio / Broadcast
**Who currently fills this:**
- F1 championship: Tata Communications (network), Paramount+ (broadcast)
- Ferrari + Racing Bulls: Riedel (intercom, comms)
- Red Bull: AT&T (US)
- Aston Martin: Atlas Air (charter logistics)

**What's open:** Most teams have legacy comms but few headline sponsor-branded.

### D2. Connectivity / Networking
**Who currently fills this:**
- Williams: VAST Data, Atlassian
- Audi: Extreme Networks (joined 2026)
- McLaren: Cisco

**What's open:** SD-WAN, edge networking, 5G for paddock.

---

## Category E — Commercial Systems & Fan

### E1. CRM / Marketing Automation
**Who currently fills this:**
- F1 championship: Salesforce (Agentforce-powered fan companion launched 2026)
- McLaren: Salesforce departed for 2026 — significant slot now open
- Mercedes: SAP (operational), Marriott Bonvoy (partner), BetterUp
- Most teams: undisclosed or fragmented stacks

**What's open:** Hubspot (mid-market), Klaviyo (e-comm), Braze (mobile-first), enterprise marketing AI.

### E2. E-commerce / Ticketing / Hospitality
**Who currently fills this:**
- F1 championship: Salesforce, American Express
- Alpine: viagogo
- Red Bull: Hard Rock International (hospitality)
- Mercedes: Marriott Bonvoy
- McLaren: Hilton

**What's open:** Shopify-class commerce, headless commerce vendors, modern hospitality CRM.

### E3. Esports / Sim-Racing / Fan ML
**Who currently fills this:**
- F1 championship: Fanatec (sim hardware), AWS (fan ML), Salesforce (Agentforce fan)
- Cadillac: TWG AI, TWG Motorsports
- McLaren: OKX (NFTs), Dropbox

**What's open:** Modern fan platforms, sports-tech ML, second-screen experiences.

---

## Category F — Sustainability & Energy *(FE-natural, F1 increasingly relevant)*

### F1. Sustainable Fuels & Lubricants
**Who currently fills this:**
- Aston Martin: Aramco (fuel), Valvoline (lubricants)
- Mercedes: Petronas (fuel + lubricants, longest-standing)
- Ferrari: Shell
- McLaren: previously had Castrol; now refresh
- Audi: bp / Castrol (joined 2026)
- Red Bull: Mobil 1, Esso
- Alpine: Eni
- Williams: Gulf
- Racing Bulls: Mobil 1
- Cadillac: (none disclosed yet)
- Haas: (none disclosed)

**What's open:** F1 is mandatedly 100% sustainable fuel from 2026 — partners are mostly legacy oil-major brands rebranded. Real sustainable-fuel startups (Prometheus Fuels, Twelve, Ineratec for e-fuels, Aether) have **no representation**. Material opening.

### F2. Battery / Energy Storage / Recycling
**Who currently fills this:**
- FE championship: ABB (title — electrification stack), Hankook (tyres with renewable materials)
- F1 side: nobody at team level

**What's open across F1 + FE:** Battery analytics (Stem, Twaice), battery recycling (Redwood Materials, Li-Cycle, Ascend Elements), EV charging software (Wallbox, ChargePoint enterprise, Electrify America), energy management platforms. **The single biggest gap in the FE roster.**

### F3. Carbon Accounting & ESG SaaS
**Who currently fills this:** Nobody at championship level on either side.

**What's open:** Watershed, Persefoni, Sweep, Plan A, Greenly, Climatiq, Salesforce Net Zero Cloud. **Empty category, perfect FE fit.**

### F4. Renewable Energy & Clean Power
**Who currently fills this:**
- FE: Envision Racing (parent Envision Group is renewable energy)
- F1: Aggreko (generators at races — championship), Schneider Electric at McLaren (joined 2026)

**What's open:** Solar/wind operators, virtual power plant operators, grid software.

---

## Category G — Human Performance & Wellness

### G1. Wearables & Biometrics
**Who currently fills this:**
- Ferrari: WHOOP (joined 2026)
- Aston Martin: Eight Sleep (joined 2026)

**What's open:** Oura, Garmin, Polar, Apple Health-stack, mental-performance wearables. Eight of ten F1 teams have no biometrics partner.

### G2. Nutrition & Recovery
**Who currently fills this:**
- McLaren: Optimum Nutrition (ON)
- Aston Martin: Celsius (energy, joined 2026)

**What's open:** Sports nutrition, hydration, recovery supplements, protein scaleups.

### G3. Mental Performance / Coaching
**Who currently fills this:**
- Mercedes: BetterUp

**What's open:** Headspace, Calm, Lyra, executive-coaching platforms, sports-psych SaaS. Effectively empty across grid.

### G4. Apparel / Race-Suits / PPE
**Who currently fills this:**
- Pirelli at race level
- Team-by-team: Alpinestars (Mercedes, McLaren, Aston Martin, Cadillac, Haas), Sparco (Williams, Red Bull), Sabelt (Ferrari, Audi), OMP (recently departed Aston Martin), Schuberth (Haas helmets), Bell (Ferrari helmets)

**What's open:** Premium consumer apparel (Puma already widespread, Castore at Williams + Haas + others, adidas at Mercedes + Audi 2026); sportswear category is dense.

---

## Category H — Premium Consumer & Hospitality Partners

### H1. Watches
- Red Bull: TAG Heuer (LVMH)
- Mercedes: IWC Schaffhausen
- Aston Martin: Breitling (joined 2026)
- McLaren: Richard Mille
- Racing Bulls: Tudor
- Williams: Girard Perregaux (joined 2026)
- Alpine: H. Moser & Cie
- Audi: (no watch partner — open)
- Cadillac: (no watch partner)
- Haas: (no watch partner)
- F1 championship: Rolex departed; TAG Heuer Spanish GP title sponsor

**What's open:** Audi, Cadillac, Haas, Ferrari (Richard Mille is at McLaren) — limited room.

### H2. Eyewear, Fashion, Lifestyle
Already dense: Ray-Ban (Ferrari), Oakley (Aston Martin), Maui Jim (Red Bull), Hugo Eyewear (Racing Bulls), ic! berlin (Audi 2026), Tommy Hilfiger (Cadillac).

### H3. Hospitality / Hotels / Travel
- Mercedes: Marriott Bonvoy
- McLaren: Hilton
- Audi: World of Hyatt (joined 2026)
- Red Bull: Hard Rock International

**What's open:** Independent luxury hotels, Hilton/Marriott/Hyatt alternatives, premium short-stay platforms (Sonder, Plum Guide).

---

## Section 2 — Operational Fit Scoring Rubric (0-25)

When scoring Operational Fit for a target company, the engine answers four sub-questions:

### Sub-score 1: Product-to-Need Match (0-10)
- **9-10**: Company's flagship product directly answers a specific named need above (e.g. a battery-analytics scaleup for F2 Battery / Energy Storage)
- **7-8**: Strong adjacent fit — product addresses a related need but isn't perfectly aligned
- **5-6**: Workable fit — product could be positioned for a team need with creative framing
- **3-4**: Stretched — product would need significant adaptation
- **0-2**: No real operational fit; brand-only play

### Sub-score 2: Slot Availability (0-5)
*(Cross-reference with `active_sponsor_db.md`)*
- **5**: Category empty across the grid OR specific team's slot in this category is open
- **3-4**: 1-3 teams already filled; slot exists at 7+ teams
- **1-2**: 4-7 teams filled; tight market
- **0**: Category saturated, no slot

### Sub-score 3: On-Camera Demonstrability (0-5)
Can the partnership be visibly activated during a race weekend in a way that proves the product?
- **5**: Product can be visibly running (data on pit-wall screens, logo on engineer headsets, tech in livery, real-time data fed to broadcast)
- **3-4**: Product visible at activations and team facility tours, not on race-broadcast
- **1-2**: Product behind the scenes only
- **0**: No demonstrable activation

### Sub-score 4: Strategic Lock-In Potential (0-5)
Does the partnership create technical lock-in that elevates the deal to multi-year strategic alliance rather than pure sponsorship?
- **5**: Product becomes operationally embedded — switching cost is high (cloud, PLM, security stacks)
- **3-4**: Strong embed but switchable in off-season
- **1-2**: Lightly integrated tool
- **0**: Pure brand placement, no technical embed

### Operational Fit Total: 0 / 25

**Sum the four sub-scores. Total is the Operational Fit dimension feeding into V2.1's overall /125 score.**

---

## Section 3 — Reading This Taxonomy as the Engine

When scoring a company, run this mental sequence:

1. **Identify the company's primary product.** What does it actually sell to enterprises?
2. **Match against Categories A–H above.** Which one or two named needs does the product address?
3. **Check incumbents.** Is the category filled at championship or team level (`active_sponsor_db.md`)?
4. **Pick top 1-2 teams** where the slot is genuinely open OR where the slot is at lower tier and an upgrade is possible.
5. **Score the four sub-questions** to derive Operational Fit /25.
6. **Surface the "What Could Run On The Car"** specifics in the brief — name the team, name the operational need, name the activation.

**Example reasoning trace** *(hypothetical — Datadog as target)*:
- Primary product: cloud observability and SaaS monitoring
- Category match: C3 — Observability/DevOps/Data Platform
- Incumbents: Splunk at McLaren; Dynatrace at Racing Bulls; Datadog itself absent
- Open teams: 8 of 10 F1 teams have no headline observability partner
- Top team match: Aston Martin (CoreWeave is there; data infrastructure story building) or Alpine (modernising stack)
- Sub-score 1 (product fit): 9 — direct match to category
- Sub-score 2 (availability): 5 — category open across most of grid
- Sub-score 3 (demonstrability): 4 — race-weekend dashboards, observable in pit-wall ops
- Sub-score 4 (lock-in): 5 — observability is sticky, switching cost is high
- **Operational Fit total: 23 / 25**

---

## Section 4 — Maintaining This File

This taxonomy is a living document. Quarterly review minimum.

- **New rule changes** (e.g. 2026 active aero, future regulations) shift what teams need — re-evaluate Category A and Category F when regulations move.
- **New partner announcements** detected in daily scans → cross-reference the operational category and update incumbent lists.
- **New tech categories** (e.g. quantum sensing, neuromorphic compute when they hit commercial relevance) get added as new sub-categories.
- **Avoid speculative categories** — only add a category once at least one team is plausibly buying in it. Otherwise the taxonomy becomes aspirational and the engine starts scoring against fiction.
