"""Build the 1440 deep-dive DOSSIER for Ramp (gated Tier-2 product).

Same standard as the Glean dossier: full company deep-dive, traction, financial
profile, leadership & decision path (incl. the leadership-tie gate), competitive
moat, and the F1 fit thesis - every load-bearing claim confidence-tagged
(VERIFIED/REPORTED/GAP/ESTIMATE) and bound to a source ledger on the last page.

    python3 pitch/ramp_dossier.py   # -> pitch/ramp-deepdive.pdf (+ .html)
"""
from __future__ import annotations

import base64
import datetime as _dt
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_ASSETS = os.path.join(_ROOT, "brand", "assets")


def _b64(name: str) -> str:
    with open(os.path.join(_ASSETS, name), "rb") as fh:
        return "data:image/png;base64," + base64.b64encode(fh.read()).decode()


LOGO_NAVY = _b64("logo-blue-gold@3x.png")
DATE_LONG = _dt.date(2026, 6, 10).strftime("%d %B %Y").upper()


def cf(level: str) -> str:
    return f'<span class="cf {level.lower()}">{level}</span>'

V, R, G, E = cf("VERIFIED"), cf("REPORTED"), cf("GAP"), cf("ESTIMATE")

HTML = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<title>1440 Deep-Dive Dossier — Ramp</title>
<style>
  :root{{ --navy:#191a48; --gold:#d1ae7a; --ink:#1a1c2e; --muted:#6b6e84;
         --hair:#e2e0ea; --panel:#f5f4f8; }}
  @page{{ size:A4; margin:14mm 14mm 13mm;
    @bottom-left{{ content:"1440 SPORTS · LONDON · CONFIDENTIAL"; font-family:Georgia,serif; font-size:7pt; color:#9a98aa; letter-spacing:.1em; }}
    @bottom-center{{ content:"RAMP · DEEP-DIVE DOSSIER"; font-family:Georgia,serif; font-size:7pt; color:#9a98aa; letter-spacing:.1em; }}
    @bottom-right{{ content:counter(page) " / " counter(pages); font-family:Georgia,serif; font-size:7pt; color:#9a98aa; letter-spacing:.1em; }}
  }}
  *{{ box-sizing:border-box; }}
  body{{ font-family:Georgia,"Times New Roman",serif; color:var(--ink); margin:0; font-size:9.4pt; line-height:1.46; }}
  .mast{{ display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid var(--navy); padding-bottom:7px; }}
  .mast img{{ height:22px; }}
  .mast .meta{{ font-family:Arial,sans-serif; font-size:6.6pt; letter-spacing:.18em; color:var(--muted); text-transform:uppercase; }}
  .ribbon{{ font-family:Arial,sans-serif; font-size:6.8pt; letter-spacing:.2em; color:var(--gold); text-transform:uppercase; font-weight:700; margin:9px 0 2px; }}
  h1{{ font-size:30pt; font-weight:400; letter-spacing:-.5px; color:var(--navy); margin:2px 0 1px; }}
  .classline{{ font-size:8.6pt; color:var(--muted); font-style:italic; margin-bottom:9px; }}
  h2{{ font-family:Arial,sans-serif; font-size:7.6pt; text-transform:uppercase; letter-spacing:.16em; color:var(--gold); border-bottom:1px solid var(--hair); padding-bottom:2px; margin:13px 0 5px; font-weight:700; }}
  p{{ margin:0 0 6px; }}
  strong{{ color:var(--navy); }}
  .snap{{ display:grid; grid-template-columns:repeat(4,1fr); gap:7px; margin:4px 0; }}
  .sc{{ border:1px solid var(--hair); border-radius:6px; padding:7px 9px; background:var(--panel); }}
  .sc .v{{ font-size:13pt; font-weight:700; color:var(--navy); line-height:1.05; }}
  .sc .k{{ font-family:Arial,sans-serif; font-size:6.2pt; color:var(--muted); letter-spacing:.04em; text-transform:uppercase; margin-top:3px; }}
  .thesis{{ background:var(--navy); border-left:4px solid var(--gold); border-radius:0 7px 7px 0; padding:10px 14px; color:#f3f1ea; margin:4px 0 2px; }}
  .thesis .k{{ font-family:Arial,sans-serif; font-size:6.4pt; font-weight:700; letter-spacing:.18em; color:var(--gold); text-transform:uppercase; }}
  .thesis p{{ font-size:10pt; line-height:1.45; margin:3px 0 0; color:#f3f1ea; }}
  .thesis strong{{ color:var(--gold); }}
  .action{{ border:1px solid var(--hair); border-left:3px solid var(--navy); border-radius:0 6px 6px 0; background:#fbf8f1; padding:7px 11px; font-size:8.8pt; margin:6px 0 2px; }}
  .action b{{ color:var(--navy); font-family:Arial,sans-serif; font-size:7pt; letter-spacing:.1em; text-transform:uppercase; }}
  .vtrend{{ margin:6px 0 2px; }}
  .vtcap{{ font-family:Arial,sans-serif; font-size:6.6pt; letter-spacing:.04em; text-transform:uppercase; color:var(--muted); margin-bottom:4px; }}
  .vt-row{{ display:flex; align-items:center; gap:8px; margin-bottom:4px; }}
  .vt-lab{{ font-family:Arial,sans-serif; font-size:6.8pt; color:var(--muted); width:58px; text-transform:uppercase; letter-spacing:.03em; }}
  .vt-bar{{ height:12px; background:linear-gradient(90deg, var(--navy), var(--gold)); border-radius:3px; min-width:6px; }}
  .vt-val{{ font-family:Arial,sans-serif; font-size:8.4pt; font-weight:700; color:var(--navy); }}
  .thermo{{ border:1px solid var(--hair); border-left:3px solid #2f7d4f; border-radius:0 6px 6px 0; background:#f6faf7; padding:7px 11px; font-size:8.4pt; margin:6px 0 2px; }}
  .thermo b{{ color:#2f7d4f; font-family:Arial,sans-serif; font-size:7pt; letter-spacing:.08em; text-transform:uppercase; }}
  .cf{{ font-family:Arial,sans-serif; font-size:5.6pt; font-weight:700; letter-spacing:.08em; padding:1px 4px; border-radius:3px; vertical-align:middle; margin-left:2px; }}
  .cf.verified{{ background:#eaf4ec; color:#2f7d4f; border:1px solid #cfe6d6; }}
  .cf.reported{{ background:#fbf3e6; color:#9a6b1f; border:1px solid #efe0c4; }}
  .cf.gap{{ background:#f7eaea; color:#9a2f2f; border:1px solid #ecd2d2; }}
  .cf.estimate{{ background:#eef0f7; color:#3b3f63; border:1px solid #d8dcec; }}
  .twocol{{ display:flex; gap:16px; }}
  .twocol > div{{ flex:1; }}
  .lead{{ border:1px solid var(--hair); border-radius:6px; padding:8px 11px; margin-bottom:6px; }}
  .lead .nm{{ font-size:11pt; color:var(--navy); }}
  .lead .rl{{ font-family:Arial,sans-serif; font-size:6.6pt; color:var(--muted); text-transform:uppercase; letter-spacing:.06em; margin-bottom:3px; }}
  .lead .bio{{ font-size:8.4pt; line-height:1.32; }}
  .mtable{{ width:100%; border-collapse:collapse; font-size:8.8pt; margin-top:2px; }}
  .mtable td{{ padding:5px 8px; border-bottom:1px solid var(--hair); vertical-align:top; }}
  .mtable td.k{{ font-family:Arial,sans-serif; font-size:7.4pt; letter-spacing:.04em; text-transform:uppercase; color:var(--muted); width:34%; }}
  .mtable td.v b{{ color:var(--navy); }}
  ul.tight{{ margin:2px 0 6px; padding-left:15px; }}
  ul.tight li{{ margin-bottom:4px; line-height:1.4; }}
  .moatgrid{{ display:grid; grid-template-columns:1fr 1fr; gap:10px; }}
  .moatcard{{ border:1px solid var(--hair); border-radius:6px; padding:8px 11px; }}
  .moatcard.edge{{ border-top:3px solid #2f7d4f; }}
  .moatcard.risk{{ border-top:3px solid #9a2f2f; }}
  .moatcard .mh{{ font-family:Arial,sans-serif; font-size:7pt; font-weight:700; letter-spacing:.1em; text-transform:uppercase; margin-bottom:4px; }}
  .moatcard.edge .mh{{ color:#2f7d4f; }} .moatcard.risk .mh{{ color:#9a2f2f; }}
  .moatcard p{{ font-size:8.4pt; line-height:1.36; margin:0 0 4px; }}
  .dealbox{{ border:1px solid var(--hair); border-radius:7px; overflow:hidden; margin-top:3px; }}
  .dealbox .dk{{ background:var(--navy); color:var(--gold); font-family:Arial,sans-serif; font-weight:700; font-size:7pt; letter-spacing:.14em; padding:6px 12px; text-transform:uppercase; }}
  .dr{{ display:flex; justify-content:space-between; padding:5px 12px; font-size:9pt; border-top:1px solid var(--hair); }}
  .dr span{{ color:var(--muted); font-family:Arial,sans-serif; font-size:7.6pt; letter-spacing:.06em; text-transform:uppercase; }}
  .dr b{{ color:var(--navy); }}
  .risk{{ font-size:8.6pt; line-height:1.36; margin-bottom:5px; }}
  .risk .rt{{ font-family:Arial,sans-serif; font-weight:700; font-size:7.2pt; letter-spacing:.04em; color:var(--navy); text-transform:uppercase; }}
  .risk b{{ color:var(--gold); }}
  .tie{{ background:var(--panel); border:1px solid var(--hair); border-left:3px solid var(--gold); border-radius:0 6px 6px 0; padding:8px 11px; font-size:8.6pt; margin-top:4px; }}
  .ledger{{ width:100%; border-collapse:collapse; font-size:7.4pt; }}
  .ledger th{{ font-family:Arial,sans-serif; font-size:6.4pt; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); text-align:left; border-bottom:1.5px solid var(--navy); padding:5px 6px; }}
  .ledger td{{ padding:4px 6px; border-bottom:1px solid var(--hair); vertical-align:top; }}
  .ledger td.src{{ font-size:6.6pt; color:var(--muted); word-break:break-all; }}
  .pageb{{ page-break-before:always; }}
  .note{{ font-family:Arial,sans-serif; font-size:7pt; color:var(--muted); font-style:normal; }}
</style></head><body>

<div class="mast">
  <img src="{LOGO_NAVY}" alt="1440 Sports">
  <span class="meta">Deep-Dive Dossier · Confidential · Ramp</span>
</div>
<div class="ribbon">Gated Intelligence · Tier 2 &nbsp;·&nbsp; {DATE_LONG}</div>

<h1>Ramp</h1>
<div class="classline">Fintech · Financial Operations / Corporate Spend &amp; AI Finance · New York · Private (~$44B)</div>

<div class="snap">
  <div class="sc"><div class="v">~$44B</div><div class="k">Valuation · Series F, Jun 2026 {V}</div></div>
  <div class="sc"><div class="v">~$1.4B</div><div class="k">Revenue; $1B+ annualized, FCF+ {R}</div></div>
  <div class="sc"><div class="v">70,000+</div><div class="k">Business customers {R}</div></div>
  <div class="sc"><div class="v">+170%</div><div class="k">Purchase-volume growth YoY {R}</div></div>
</div>

<div class="thesis">
  <div class="k">The Scarce Thing — 1440's Read</div>
  <p>A category-defining fintech at a just-closed <strong>$44B</strong> valuation, $1B+ ARR and
  free-cash-flow-positive, launching in the UK/EU this summer - and <strong>no spend-management
  brand sits anywhere on the F1 grid.</strong> Visa Cash App Racing Bulls is the structural fit:
  Ramp's deepened Visa issuing relationship lets it sit as the spend-intelligence layer
  <em>above</em> the existing Visa rail. Move on the just-raised brand-reckoning moment.
  Opportunity score: 84/100 (HOT).</p>
</div>

<div class="action">
  <b>Recommended action</b> &nbsp; Open CEO Eric Glyman within 6-10 weeks - ahead of the
  British GP and Ramp's UK/EU launch this summer. Lead with the structural Visa fit (not an
  inside relationship - the leadership-tie gate is clear), and offer a short-form LOI to hold
  spend-management category exclusivity while terms form. Owner: 1440 partner-led.
</div>
<div class="thermo">
  <b>Deal read</b> &nbsp; WARM (84/100). Key dependency: a founder-level brand-spend decision
  with no inside champion (leadership-tie gate is clear). What breaks it: Ramp keeps all spend on
  direct go-to-market and treats motorsport as off-strategy. Mitigant: the structural Visa fit +
  the just-closed raise. &nbsp;·&nbsp; <em>Tracked in the outcomes loop: brief → meeting → deal.</em>
</div>

<h2>1 · What Ramp Is</h2>
<p>Ramp is a <strong>financial-operations platform</strong> - corporate cards, expense management,
bill pay / AP automation, procurement and travel, increasingly run by <strong>AI finance
agents</strong> - on a single system. {V} Its wedge and brand promise is distinctive in the
category: where rivals help companies <em>spend</em>, Ramp is built to help them <em>save</em>
(automated savings, spend controls, anomaly detection), which aligns its pitch with the
CFO's mandate. {R} It monetises primarily through interchange on card volume plus
software, and has extended into <strong>Ramp Stack</strong> (a platform for accounting firms) and
AI-era categories such as token/AI-spend management. {R}</p>

<h2>2 · Traction &amp; Momentum</h2>
<div class="vtrend">
  <div class="vtcap">Valuation trajectory — ~3&times; in 18 months, on a $750M Series F (Jun 2026) {V}</div>
  <div class="vt-row"><span class="vt-lab">Early 2025</span><span class="vt-bar" style="width:30%"></span><span class="vt-val">~$15B</span></div>
  <div class="vt-row"><span class="vt-lab">Nov 2025</span><span class="vt-bar" style="width:66%"></span><span class="vt-val">$32B</span></div>
  <div class="vt-row"><span class="vt-lab">Jun 2026</span><span class="vt-bar" style="width:91%"></span><span class="vt-val">$44B</span></div>
</div>
<ul class="tight">
  <li><strong>Growth drivers:</strong> emerging AI categories (incl. token/AI-spend management) plus Ramp Stack, its platform for accounting firms. {R}</li>
  <li><strong>Customers:</strong> 70,000+ businesses (Jun 2026, up from ~50,000 at the start of the year); ~2,200 paying $100K+ (Nov 2025, +133% YoY enterprise growth). {R}</li>
  <li><strong>Purchase volume:</strong> ~$100B+ annualized, growing ~170% YoY (Mar 2026) - its fastest in three years despite ~20&times; prior scale. {R}</li>
  <li><strong>UK/EU:</strong> acquired payments platform <strong>Billhop</strong> (Mar 2026); onboarding UK/EU businesses this summer. {V}</li>
</ul>

<h2>3 · Financial Profile <span class="note">— private company: figures are disclosures/estimates, not audited statements</span></h2>
<table class="mtable">
  <tr><td class="k">Status</td><td class="v"><b>Private.</b> No audited public statements; figures below are company/press disclosures. {G}</td></tr>
  <tr><td class="k">Revenue / ARR</td><td class="v"><b>~$1.4B</b> revenue (2026); $1B+ annualized, <b>FCF-positive</b> - rare at this growth rate {R}</td></tr>
  <tr><td class="k">Profitability</td><td class="v">Underlying profitability +153% YoY (to Nov 2025); FCF-positive since ~Nov 2025 {R}</td></tr>
  <tr><td class="k">Revenue model</td><td class="v">Interchange on card volume + software; exposed to card-spend and interest-rate cycles {E}</td></tr>
</table>

<h2>4 · Leadership &amp; The Decision Path</h2>
<div class="twocol">
  <div>
    <div class="lead"><div class="rl">Co-Founder &amp; CEO — PRIMARY ENTRY {V}</div><div class="nm">Eric Glyman</div>
      <div class="bio">Co-founded Ramp (and earlier Paribus, acquired by Capital One). Drives strategic capital allocation and partnership decisions - the $750M raise and the deepened Visa partnership are his office. <strong>A sponsorship of this scale is his call.</strong></div></div>
    <div class="lead"><div class="rl">Co-Founder &amp; CTO {V}</div><div class="nm">Karim Atiyeh</div>
      <div class="bio">Owns Ramp's technical and product architecture; the right co-decision-maker for any working integration (e.g. the team's treasury/settlement stack).</div></div>
  </div>
  <div>
    <div class="lead"><div class="rl">Chief Financial Officer (Jan 2025) {V}</div><div class="nm">William Petrie</div>
      <div class="bio">Owns the capital and spend discipline; a marquee multi-year sponsorship runs through his approval. The natural co-decision-maker on commercial terms.</div></div>
    <div class="lead"><div class="rl">CPO · CBO {V}</div><div class="nm">Geoff Charles · Colin Kennedy</div>
      <div class="bio">Geoff Charles (Chief Product Officer) and Colin Kennedy (Chief Business Officer) round out the bench. No standalone CMO is publicly confirmed - brand decisions sit with the CEO. {G}</div></div>
  </div>
</div>
<div class="tie">
  <strong>Leadership-tie gate (F1/FE or deal-structuring history):</strong> CHECKED — none found {G}.
  No senior Ramp leader has prior F1/FE-ecosystem or sponsorship-deal experience, so this is a
  <em>cold, thesis-led</em> approach (the opposite of a JFrog/Genefa-Murphy warm path). Lead with the
  structural Visa fit and the just-raised brand moment, not an inside relationship.
</div>

<h2>5 · Competitive Moat — How Durable Is The Budget?</h2>
<div class="moatgrid">
  <div class="moatcard edge"><div class="mh">◆ The Edge</div>
    <p><strong>One integrated platform + a cost-savings wedge.</strong> Cards, expense, AP, procurement and AI finance agents on one system, sold as "save money," not "spend it" - which is why Ramp has out-grown Brex. {R}</p>
    <p><strong>Profitable hyper-growth:</strong> $1B+ ARR, FCF-positive, ~170% purchase-volume growth - a balance sheet that makes a multi-year deal immaterial. {R}</p>
  </div>
  <div class="moatcard risk"><div class="mh">▲ The Pressure</div>
    <p><strong>A crowded feature war.</strong> Brex, BILL, Navan, Rho, Mercury, Airwallex and SAP Concur all compete; spend management risks commoditising, and switching is a feature/price fight. {R}</p>
    <p><strong>Model exposure:</strong> interchange-led revenue is sensitive to card-spend volume and interest rates - a macro downturn pressures the engine. {E}</p>
  </div>
</div>
<p><strong>1440 read:</strong> the moat is real (integration + cost-savings alignment + profitable scale)
but the category is contested - which makes a differentiated, CFO-credible brand stage <em>more</em>
valuable to Ramp, not less. The Visa structural angle is the sharpest differentiator a rival can't copy.</p>

<h2>6 · Fit Into The F1 Ecosystem — Visa Cash App Racing Bulls</h2>
<p>No spend-management or AI-finance brand holds a position anywhere in F1, and direct rival
<strong>Brex has no motorsport deal</strong> - the entire corporate-spend category is open. {R} The slot that
fits Ramp's profile is <strong>Visa Cash App Racing Bulls</strong>: Ramp's deepened multi-year Visa issuing
relationship (Visa Intelligent Commerce, Trusted Agent Protocol, AI bill-pay agents) makes
co-presence with the team's Visa title <strong>structural, not conflicting</strong> - Ramp sits as the
spend-intelligence layer above the Visa rail. {V} The team's founder/CFO-suite audience is exactly
Ramp's buyer, and the UK/EU launch lines up with a home-market activation at the British GP.</p>
<p><strong>MODE B - real operational value, off-car.</strong> Ramp's payments rail and back-office stack map
onto the team's commercial machine: paddock supplier settlements, sponsor-activation treasury
flows, and a partner-onboarding funnel of venture-backed, CFO-led companies - the exact audience
the team wants. The team gains a modern finance stack and aligned co-marketing; Ramp gets a
CFO-audience stage and a calendar anchor.</p>
<div class="twocol">
  <div>
    <div class="dealbox">
      <div class="dk">Recommended Deal Architecture</div>
      <div class="dr"><span>Tier</span><b>Official Spend Management Partner</b></div>
      <div class="dr"><span>Term</span><b>4 years</b></div>
      <div class="dr"><span>Value</span><b>~$6-9M / yr (est.)</b></div>
      <div class="dr"><span>Scope</span><b>Visa co-activation + CFO hospitality</b></div>
      <div class="dr"><span>Anchor</span><b>British GP + Las Vegas / UK launch</b></div>
    </div>
  </div>
  <div>
    <h2 style="margin-top:0">Opening Angle</h2>
    <p style="font-style:italic; color:var(--navy); background:var(--panel); border-left:3px solid var(--gold); border-radius:0 6px 6px 0; padding:9px 12px; font-size:9.4pt;">
    "Eric, the $44B round and your UK/EU launch this summer line up exactly with Racing Bulls -
    Ramp as the spend layer above the Visa rail - and the British GP is a ready-made home-market
    activation. 25 minutes before a rival notices the open lane?"</p>
  </div>
</div>
<p class="note" style="margin-top:6px"><strong style="color:var(--navy)">Why ~$6-9M/yr:</strong>
mid-tier F1 partner programmes typically run ~$5-15M/yr; $6-9M positions Ramp as an Official
(not title) partner, calibrated to its $1B+ revenue (immaterial spend) and the value of direct
CFO/founder-audience access plus Visa co-activation, with category exclusivity carrying the
premium. {E} Directional only - validate against Racing Bulls' actual rate card before any number
reaches the prospect.</p>

<h2>7 · Risks &amp; Counters</h2>
<div class="risk"><span class="rt">Visa channel conflict</span> — Ramp's Visa issuing deal could read as a conflict with the Visa title. <b>Counter:</b> it is a structural bridge - Ramp is the spend-intelligence layer above the rail; the two roles are architecturally distinct and mutually reinforcing.</div>
<div class="risk"><span class="rt">Off-car relevance (MODE B)</span> — spend management isn't in-car tech. <b>Counter:</b> lead with the Visa co-presence and a CFO/founder-audience hospitality + pipeline play; the value is audience and the Visa bridge, not a garage integration.</div>
<div class="risk"><span class="rt">No inside champion</span> — the leadership-tie gate is clear, so there's no warm motorsport buyer. <b>Counter:</b> this is a founder-level, thesis-led call; anchor to the just-closed raise and the UK launch, and bring the CFO in early on measurable pipeline/brand outcomes.</div>

<h2>8 · Confidence &amp; Source Ledger <span class="note">— every load-bearing claim, its confidence, and its source</span></h2>
<table class="ledger">
  <tr><th>Claim</th><th>Conf.</th><th class="src">Source</th></tr>
  <tr><td>$750M Series F at $44B (Jun 2026); ICONIQ/GIC/Ontario Teachers'</td><td>VERIFIED</td><td class="src">cnbc.com · techcrunch.com · pulse2.com</td></tr>
  <tr><td>$32B Nov 2025 (+38% to $44B); ~3&times; in 18 months</td><td>VERIFIED</td><td class="src">prnewswire.com · cnbc.com</td></tr>
  <tr><td>Revenue ~$1.4B; $1B+ annualized; FCF-positive</td><td>REPORTED</td><td class="src">getlatka.com · sacra.com · Ramp blog</td></tr>
  <tr><td>70,000+ customers (Jun 2026); 2,200 &gt;$100K (+133% YoY)</td><td>REPORTED</td><td class="src">prnewswire.com · Ramp blog</td></tr>
  <tr><td>Purchase volume +170% YoY (Mar 2026); $100B+ annualized</td><td>REPORTED</td><td class="src">Ramp blog · Contrary Research</td></tr>
  <tr><td>Leadership: Glyman (CEO), Atiyeh (CTO), Petrie (CFO, Jan 2025), Charles (CPO), Kennedy (CBO)</td><td>VERIFIED</td><td class="src">Ramp blog; Clay/Craft exec listings</td></tr>
  <tr><td>No public CMO; no senior leader with F1/FE/deal history</td><td>GAP</td><td class="src">no primary source found — flagged, not assumed</td></tr>
  <tr><td>Deepened multi-year Visa issuing partnership; Billhop acquisition (Mar 2026)</td><td>VERIFIED</td><td class="src">prnewswire.com (Ramp–Visa; Ramp–Billhop)</td></tr>
  <tr><td>Competitors Brex/BILL/Navan/Rho/Mercury/SAP Concur; no spend brand on the F1 grid</td><td>REPORTED</td><td class="src">brex.com · fylehq.com · 1440 team data</td></tr>
  <tr><td>Deal value ~$6-9M/yr; opportunity score 84/100</td><td>ESTIMATE</td><td class="src">1440 scoring model — directional, not a quote</td></tr>
</table>
<p class="note" style="margin-top:8px">Discipline: VERIFIED = primary source · REPORTED = credible secondary ·
GAP/ESTIMATE = explicitly not confirmed. Private-company financials are inherently limited;
where audited numbers don't exist, we say so rather than invent them.</p>

</body></html>"""

if __name__ == "__main__":
    out_html = os.path.join(_HERE, "ramp-deepdive.html")
    with open(out_html, "w", encoding="utf-8") as fh:
        fh.write(HTML)
    print("HTML ->", out_html)
    try:
        from weasyprint import HTML as WHTML
        doc = WHTML(string=HTML, base_url=_HERE).render()
        out_pdf = os.path.join(_HERE, "ramp-deepdive.pdf")
        doc.write_pdf(out_pdf)
        print(f"PDF  -> {out_pdf}  ({len(doc.pages)} pages)")
    except Exception as exc:  # pragma: no cover
        print(f"[dossier] PDF skipped ({exc.__class__.__name__}: {exc})")
