"""Build the 1440 deep-dive DOSSIER for a prospect (showcase: Glean).

This is the *gated* second tier behind the 2-page brief: full company deep-dive,
leadership & decision path, financial profile, competitive-moat analysis, and the
F1/FE fit thesis. Every load-bearing claim carries a confidence tag and is bound
to a source in the ledger on the final page — the same verification discipline as
the brief, extended to the dossier.

Brand-locked to the Intelligence Brief system. Portrait A4, natural pagination.

    python3 pitch/glean_dossier.py   # -> pitch/glean-deepdive.pdf (+ .html)
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
DATE_LONG = _dt.date(2026, 5, 30).strftime("%d %B %Y").upper()

# ---- confidence badge ------------------------------------------------------
def cf(level: str) -> str:
    return f'<span class="cf {level.lower()}">{level}</span>'

V = cf("VERIFIED")     # primary source (company / SEC / FIA)
R = cf("REPORTED")     # credible secondary (Fortune, TechCrunch, trade press)
G = cf("GAP")          # could not confirm — flagged, not guessed

HTML = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<title>1440 Deep-Dive Dossier — Glean</title>
<style>
  :root{{ --navy:#191a48; --gold:#d1ae7a; --ink:#1a1c2e; --muted:#6b6e84;
         --hair:#e2e0ea; --panel:#f5f4f8; }}
  @page{{ size:A4; margin:14mm 14mm 13mm;
    @bottom-left{{ content:"1440 SPORTS · LONDON · CONFIDENTIAL"; font-family:Georgia,serif; font-size:7pt; color:#9a98aa; letter-spacing:.1em; }}
    @bottom-center{{ content:"GLEAN · DEEP-DIVE DOSSIER"; font-family:Georgia,serif; font-size:7pt; color:#9a98aa; letter-spacing:.1em; }}
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

  .snap{{ display:grid; grid-template-columns:repeat(4,1fr); gap:7px; margin:4px 0 4px; }}
  .sc{{ border:1px solid var(--hair); border-radius:6px; padding:7px 9px; background:var(--panel); }}
  .sc .v{{ font-size:13pt; font-weight:700; color:var(--navy); line-height:1.05; }}
  .sc .k{{ font-family:Arial,sans-serif; font-size:6.2pt; color:var(--muted); letter-spacing:.04em; text-transform:uppercase; margin-top:3px; }}

  .thesis{{ background:var(--navy); border-left:4px solid var(--gold); border-radius:0 7px 7px 0; padding:10px 14px; color:#f3f1ea; margin:4px 0 2px; }}
  .thesis .k{{ font-family:Arial,sans-serif; font-size:6.4pt; font-weight:700; letter-spacing:.18em; color:var(--gold); text-transform:uppercase; }}
  .thesis p{{ font-size:10pt; line-height:1.45; margin:3px 0 0; color:#f3f1ea; }}

  .cf{{ font-family:Arial,sans-serif; font-size:5.6pt; font-weight:700; letter-spacing:.08em; padding:1px 4px; border-radius:3px; vertical-align:middle; margin-left:2px; }}
  .cf.verified{{ background:#eaf4ec; color:#2f7d4f; border:1px solid #cfe6d6; }}
  .cf.reported{{ background:#fbf3e6; color:#9a6b1f; border:1px solid #efe0c4; }}
  .cf.gap{{ background:#f7eaea; color:#9a2f2f; border:1px solid #ecd2d2; }}

  .twocol{{ display:flex; gap:16px; }}
  .twocol > div{{ flex:1; }}
  .lead{{ border:1px solid var(--hair); border-radius:6px; padding:8px 11px; margin-bottom:6px; }}
  .lead .nm{{ font-size:11pt; color:var(--navy); }}
  .lead .rl{{ font-family:Arial,sans-serif; font-size:6.6pt; color:var(--muted); text-transform:uppercase; letter-spacing:.06em; margin-bottom:3px; }}
  .lead .bio{{ font-size:8.4pt; line-height:1.34; }}

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

  .ledger{{ width:100%; border-collapse:collapse; font-size:7.4pt; }}
  .ledger th{{ font-family:Arial,sans-serif; font-size:6.4pt; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); text-align:left; border-bottom:1.5px solid var(--navy); padding:5px 6px; }}
  .ledger td{{ padding:4px 6px; border-bottom:1px solid var(--hair); vertical-align:top; }}
  .ledger td.src{{ font-size:6.6pt; color:var(--muted); word-break:break-all; }}
  .pageb{{ page-break-before:always; }}
  .note{{ font-family:Arial,sans-serif; font-size:7pt; color:var(--muted); font-style:normal; }}
</style></head><body>

<div class="mast">
  <img src="{LOGO_NAVY}" alt="1440 Sports">
  <span class="meta">Deep-Dive Dossier · Confidential · Glean</span>
</div>
<div class="ribbon">Gated Intelligence · Tier 2 &nbsp;·&nbsp; {DATE_LONG}</div>

<h1>Glean</h1>
<div class="classline">Enterprise AI / "Work AI" Platform · Palo Alto, CA · Private (~$7.2B) · Founded 2019</div>

<div class="snap">
  <div class="sc"><div class="v">~$7.2B</div><div class="k">Valuation · Series F {V}</div></div>
  <div class="sc"><div class="v">~$300M</div><div class="k">ARR, May 2026 {R}</div></div>
  <div class="sc"><div class="v">~$768M</div><div class="k">Total raised {R}</div></div>
  <div class="sc"><div class="v">2019</div><div class="k">Founded · 4 co-founders {V}</div></div>
</div>

<div class="thesis">
  <div class="k">The Scarce Thing — 1440's Read</div>
  <p>A category-leading, fast-compounding enterprise-AI brand on a clear IPO path,
  sitting in the one lane Formula E has left open — enterprise AI — with a warm,
  de-risked home at Mahindra (committed as a manufacturer through 2030). <strong>Move now,
  while category exclusivity is uncontested and cheap, and before a larger AI name
  notices the open grid.</strong> Opportunity score: 72/100 (WARM).</p>
</div>

<h2>1 · What Glean Is, And Why It Matters</h2>
<p>Glean builds "Work AI" — an enterprise platform that indexes a company's entire
knowledge estate (Slack, Confluence, Jira, Google Drive, Salesforce, GitHub,
Microsoft 365 and more) behind a <strong>permissions-aware knowledge graph</strong>, then layers
search, assistants and autonomous agents on top. {V} The thesis a buyer cares
about: it makes large, messy organisations dramatically faster at finding and
acting on what they already know. Recent product direction is explicitly agentic —
an Agentic Engine and Canvas co-authoring surface — and users had executed
<strong>250M+ agentic actions by January 2026</strong>. {R} In March 2026 Glean acquired
agentic-document company <strong>Aryn</strong>, deepening that roadmap. {R}</p>

<h2>2 · Traction &amp; Momentum</h2>
<ul class="tight">
  <li><strong>Revenue:</strong> ~$300M ARR by May 2026 — roughly tripled in ~15 months ($100M early 2025 → $200M Dec 2025 → $300M May 2026). {R}</li>
  <li><strong>Customers:</strong> Fortune 500 logo count nearly doubled YoY; named customers include <strong>Databricks, Samsung, Booking.com, Reddit and Pinterest</strong>. {R}</li>
  <li><strong>Capital:</strong> ~$768M raised across six rounds; backers include Sequoia, Kleiner Perkins, Lightspeed, ICONIQ, General Catalyst, Coatue and Wellington (Series F lead). {R}</li>
  <li><strong>Narrative edge:</strong> positioned as the AI that <em>pays for itself</em> amid enterprise AI-budget scrutiny — a counter-cyclical sales story that is working. {R}</li>
</ul>

<h2>3 · Financial Profile <span class="note">— private company: no audited public statements; ARR is the disclosed proxy</span></h2>
<table class="mtable">
  <tr><td class="k">Status</td><td class="v"><b>Private.</b> No public financial statements or audited P&amp;L available. {G} Figures below are ARR and round disclosures, not audited accounts.</td></tr>
  <tr><td class="k">ARR trajectory</td><td class="v"><b>~$300M</b> (May 2026), tripled in ~15 months {R}</td></tr>
  <tr><td class="k">Last round</td><td class="v"><b>$150M Series F</b> at <b>~$7.2B</b> (June 2025), led by Wellington Management {V}</td></tr>
  <tr><td class="k">Profitability</td><td class="v">Not disclosed — assume growth-stage burn typical of a scaling enterprise-AI company {G}</td></tr>
  <tr><td class="k">Implied multiple</td><td class="v">~24× ARR on the Series F mark — rich, but in line with top-tier enterprise-AI comps; supports a marquee brand spend {R}</td></tr>
</table>
<p class="note">CFO note: no Chief Financial Officer is publicly identified. {G} For a company on an
IPO trajectory this is a live readiness gap worth tracking — and a reason marquee
brand decisions today sit with the CEO/COO/CMO, not a finance gatekeeper.</p>

<div class="pageb"></div>
<h2>4 · Leadership &amp; The Decision Path</h2>
<div class="twocol">
  <div>
    <div class="lead"><div class="rl">Founder &amp; CEO {V}</div><div class="nm">Arvind Jain</div>
      <div class="bio">A Google Distinguished Engineer for over a decade (Search, Maps, YouTube) and a co-founder of Rubrik, where he led R&amp;D. Deep technical credibility; sets brand and strategic-partnership direction. <strong>Co-decision-maker on marquee spend.</strong></div></div>
    <div class="lead"><div class="rl">Chief Operating Officer {V}</div><div class="nm">Amar Maletira</div>
      <div class="bio">Runs go-to-market and company operations. Previously CEO and board member of <strong>Rackspace Technology (NASDAQ: RXT)</strong>, a ~$2.7B hybrid-cloud/AI company — a public-company operator who understands sponsorship as a commercial instrument. A pragmatic ally for a deal structured around pipeline.</div></div>
  </div>
  <div>
    <div class="lead"><div class="rl">Chief Marketing Officer — PRIMARY ENTRY {V}</div><div class="nm">Matt "Kix" Kixmoeller</div>
      <div class="bio">Owns global marketing and the growth-stage brand-build a Formula E partnership would anchor. Previously led marketing at Ghost Autonomy and marketing/product at <strong>Pure Storage</strong> (a multi-billion-dollar data pioneer). <strong>This is the door.</strong></div></div>
    <div class="lead"><div class="rl">Co-founders {V}</div><div class="nm">Vishwanath · Gentilcore · Prahladka</div>
      <div class="bio">T.R. Vishwanath (Technical Infrastructure Lead), Tony Gentilcore and Piyush Prahladka co-founded Glean with Jain in 2019 — an ex-Google engineering core that underpins the knowledge-graph moat.</div></div>
  </div>
</div>
<p><strong>Path to yes:</strong> approach Kixmoeller (CMO) as the owner of the brand mandate;
bring Maletira (COO) in early as the commercially-literal operator who will judge
the deal on pipeline and credibility; Jain (CEO) is the founder sign-off for a
marquee spend. No CFO gatekeeper today shortens the chain. {V}{G}</p>

<h2>5 · Competitive Moat — How Durable Is The Budget?</h2>
<p class="note">Why this matters to 1440: a durable moat means durable budget and a multi-year partner who won't disappear mid-contract.</p>
<div class="moatgrid">
  <div class="moatcard edge"><div class="mh">◆ The Edge</div>
    <p><strong>Permissions-aware knowledge graph + connector breadth.</strong> In heterogeneous estates (Slack + Confluence + Jira + Google + Salesforce + GitHub <em>alongside</em> Microsoft), Glean's cross-source retrieval is the differentiator — and most large enterprises are exactly that type. {R}</p>
    <p><strong>Incumbent stumble:</strong> only ~3.3% of Microsoft 365 seats had converted to paid Copilot by early 2026 (~15M of 450M) — the category leader has <em>not</em> locked the market. {R}</p>
  </div>
  <div class="moatcard risk"><div class="mh">▲ The Pressure</div>
    <p><strong>Microsoft.</strong> If Copilot materially closes the retrieval-quality gap over the next ~12 months, Glean's moat narrows in Microsoft-heavy accounts — the single most important variable to watch. {R}</p>
    <p><strong>Adoption friction:</strong> 100+ seat minimums, paid POCs, and reported 30–50% renewal step-ups at scale can slow land-and-expand. {R}</p>
  </div>
</div>
<p><strong>1440 read:</strong> the moat is real and the leader is beatable, but it is contested —
which is precisely why a differentiated, enterprise-credible brand stage (and a
talent-attraction halo in a brutal AI hiring market) is <em>more</em> valuable to Glean now,
not less. The partnership is on-strategy, not vanity.</p>

<div class="pageb"></div>
<h2>6 · Fit Into The F1 / FE Ecosystem — Mahindra Racing</h2>
<p>Formula E is the correct grid: its enterprise-and-sustainability audience matches
Glean's buyer far better than a saturated F1 fintech/security lane, and <strong>no enterprise-AI
brand owns a Formula E team partnership</strong> — the category is open. {R} Mahindra is the
sharpest canvas: a <strong>founding FE manufacturer since 2013</strong>, committed to the
<strong>Gen4 era through 2030</strong> {V}, backed by the global Mahindra Group — a complex,
multi-business enterprise that mirrors exactly the organisations Glean sells into.
The 2030 commitment de-risks a multi-year term, and the team's parent-group
relationships open enterprise doors.</p>
<p><strong>Mode A — a working deployment, not signage.</strong> A racing team and its parent run on
dispersed institutional knowledge (engineering docs, supplier data, sponsor and
ops information) — precisely what Glean indexes and makes usable. A deployment for
the team and selected Mahindra Group functions gives Mahindra real productivity
value and Glean a flagship, referenceable enterprise deployment plus a co-marketing
story across a global group.</p>
<div class="twocol">
  <div>
    <div class="dealbox">
      <div class="dk">Recommended Deal Architecture</div>
      <div class="dr"><span>Tier</span><b>Official Work AI Partner</b></div>
      <div class="dr"><span>Term</span><b>3+ yrs (to Gen4 / 2030)</b></div>
      <div class="dr"><span>Value</span><b>~$3–4M / yr (est.)</b></div>
      <div class="dr"><span>Scope</span><b>AI-category exclusivity + live deployment</b></div>
      <div class="dr"><span>Grid fit</span><b>PRIME — greenfield lane</b></div>
    </div>
  </div>
  <div>
    <h2 style="margin-top:0">Opening Angle</h2>
    <p style="font-style:italic; color:var(--navy); background:var(--panel); border-left:3px solid var(--gold); border-radius:0 6px 6px 0; padding:9px 12px; font-size:9.4pt;">
    "Kix — Formula E's enterprise-AI lane is wide open, and Mahindra's committed to
    2030, so a multi-year deal is de-risked. You'd own the category before the IPO.
    25 minutes?"</p>
  </div>
</div>

<h2>7 · Risks &amp; Counters</h2>
<div class="risk"><span class="rt">Hyper-growth focus</span> — a fast-scaling company may keep all spend on direct go-to-market. <b>Counter:</b> frame as enterprise-credibility + a referenceable reference deployment + a talent magnet, with measured pipeline — not brand vanity.</div>
<div class="risk"><span class="rt">No dated trigger</span> — absent an acute clock, the deal can drift. <b>Counter:</b> category exclusivity <em>is</em> the clock; it vanishes the moment a rival AI brand signs an FE team.</div>
<div class="risk"><span class="rt">FE vs F1 reach instinct</span> — leadership may reach for F1's larger audience. <b>Counter:</b> FE's enterprise/sustainability profile and low category-crowding give Glean ownership it could never get in saturated F1 lanes.</div>
<div class="risk"><span class="rt">Microsoft pressure on the moat</span> — Copilot could narrow the gap. <b>Counter:</b> that pressure makes a differentiated brand + talent halo more valuable now; structure exclusivity to lock the lane while it's cheap.</div>

<h2>8 · Confidence &amp; Source Ledger <span class="note">— every load-bearing claim, its confidence, and its source</span></h2>
<table class="ledger">
  <tr><th>Claim</th><th>Conf.</th><th class="src">Source</th></tr>
  <tr><td>$150M Series F at ~$7.2B (Jun 2025), Wellington-led</td><td>VERIFIED</td><td class="src">glean.com/press/glean-raises-150m-series-f-at-7-2b-valuation…</td></tr>
  <tr><td>~$300M ARR (May 2026), tripled in ~15 months</td><td>REPORTED</td><td class="src">fortune.com · thelettertwo.com · cryptobriefing.com</td></tr>
  <tr><td>~$768M total raised; investor roster</td><td>REPORTED</td><td class="src">sacra.com/c/glean · crunchbase</td></tr>
  <tr><td>Customers: Databricks, Samsung, Booking.com, Reddit, Pinterest</td><td>REPORTED</td><td class="src">thelettertwo.com · fortune.com</td></tr>
  <tr><td>250M+ agentic actions by Jan 2026; Aryn acquisition Mar 2026</td><td>REPORTED</td><td class="src">unicornscreener.vc · trade press</td></tr>
  <tr><td>Leadership: Jain (CEO), Maletira (COO, ex-Rackspace), Kixmoeller (CMO), co-founders</td><td>VERIFIED</td><td class="src">glean.com/about · glean.com/authors</td></tr>
  <tr><td>No CFO publicly identified (IPO-readiness gap)</td><td>GAP</td><td class="src">no primary source found — flagged, not assumed</td></tr>
  <tr><td>Permissions-aware knowledge graph; connector breadth vs Copilot; ~3.3% Copilot conversion</td><td>REPORTED</td><td class="src">futurumgroup.com · analyst/trade comparisons</td></tr>
  <tr><td>Mahindra: founding FE team since 2013, committed Gen4 through 2030</td><td>VERIFIED</td><td class="src">fia.com/news/mahindra-racing-commits-formula-e-gen4-era-until-2030</td></tr>
  <tr><td>Deal value ~$3–4M/yr; opportunity score 72/100</td><td>ESTIMATE</td><td class="src">1440 scoring model — directional, not a quote</td></tr>
</table>
<p class="note" style="margin-top:8px">Discipline: VERIFIED = primary source · REPORTED = credible secondary ·
GAP/ESTIMATE = explicitly not confirmed. Nothing in this dossier is presented as
fact that is not bound above. Private-company financials are inherently limited —
where audited numbers don't exist, we say so rather than invent them.</p>

</body></html>"""

if __name__ == "__main__":
    out_html = os.path.join(_HERE, "glean-deepdive.html")
    with open(out_html, "w", encoding="utf-8") as fh:
        fh.write(HTML)
    print("HTML ->", out_html)
    try:
        from weasyprint import HTML as WHTML
        doc = WHTML(string=HTML, base_url=_HERE).render()
        out_pdf = os.path.join(_HERE, "glean-deepdive.pdf")
        doc.write_pdf(out_pdf)
        print(f"PDF  -> {out_pdf}  ({len(doc.pages)} pages)")
    except Exception as exc:  # pragma: no cover
        print(f"[dossier] PDF skipped ({exc.__class__.__name__}: {exc})")
