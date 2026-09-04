"""Build the 1440 Sports — Origination Desk pitch deck (MD: Ricky Paugh).

Brand-locked to the same system as the Intelligence Briefs: navy #191a48 /
gold #d1ae7a, Georgia serif, 1440 masthead. Landscape A4, renders to PDF via
the same WeasyPrint toolchain the engine already uses. Logos are embedded as
base64 so the PDF is fully portable.

    python3 pitch/build_deck.py        # -> pitch/1440-origination-desk.pdf (+ .html)
"""
from __future__ import annotations

import base64
import datetime as _dt
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_ASSETS = os.path.join(_ROOT, "brand", "assets")


def _b64(name: str) -> str:
    p = os.path.join(_ASSETS, name)
    with open(p, "rb") as fh:
        return "data:image/png;base64," + base64.b64encode(fh.read()).decode()


LOGO_NAVY = _b64("logo-blue-gold@3x.png")
LOGO_WHITE = _b64("logo-white@3x.png")
DATE_LONG = _dt.date(2026, 5, 30).strftime("%d %B %Y")

# ---- slide helpers ---------------------------------------------------------

def slide(inner: str, n: int, total: int, kicker: str = "", dark: bool = False) -> str:
    cls = "slide dark" if dark else "slide"
    logo = LOGO_WHITE if dark else LOGO_NAVY
    return f"""
    <section class="{cls}">
      <header class="shead">
        <img class="mark" src="{logo}" alt="1440 Sports">
        <span class="khead">{kicker or "1440 SPORTS · CONFIDENTIAL"}</span>
      </header>
      <div class="sbody">{inner}</div>
      <footer class="sfoot">
        <span>1440 SPORTS · LONDON</span>
        <span>THE ORIGINATION DESK · {DATE_LONG}</span>
        <span>{n:02d} / {total:02d}</span>
      </footer>
    </section>"""


SLIDES: list[tuple[str, str]] = []


def add(kicker: str, inner: str):
    SLIDES.append((kicker, inner))


# ---- 01 · COVER ------------------------------------------------------------
add("", f"""
  <div class="cover">
    <div class="cover-rule"></div>
    <div class="eyebrow">INTERNAL PROPOSAL · FOR RICKY PAUGH, MANAGING PARTNER</div>
    <h1>The Origination Desk</h1>
    <p class="sub">Insight-led origination for 1440 Sports — a verified,
       motorsport-matched sponsor prospect, delivered every morning,
       walked into the meeting ready.</p>
    <div class="cover-meta">
      <span>F1 &amp; FORMULA E</span><i></i>
      <span>BUILT &amp; RUNNING</span><i></i>
      <span>{DATE_LONG}</span>
    </div>
  </div>""")

# ---- 02 · THE BOTTLENECK ---------------------------------------------------
add("THE PROBLEM WORTH SOLVING", """
  <h2>Our scarcest asset is partner time — and most of it is spent <em>finding</em>, not closing.</h2>
  <div class="cols3">
    <div class="card">
      <div class="cardk">THE GRIND</div>
      <p>Every live conversation starts with the same manual work: which enterprise
      or pre-IPO company is ripe to sponsor <strong>right now</strong>, why now, which team,
      and is the claim even true. Hours of desk research per prospect.</p>
    </div>
    <div class="card">
      <div class="cardk">THE CEILING</div>
      <p>That manual top-of-funnel caps how many qualified conversations we can run
      at once. We don't have a closing problem — Ricky and the partners close.
      We have a <strong>throughput problem at origination.</strong></p>
    </div>
    <div class="card">
      <div class="cardk">THE RISK</div>
      <p>One confidently-wrong fact in front of a CMO costs a relationship.
      So the research has to be both <strong>fast and verified</strong> — the two
      things hardest to do by hand at volume.</p>
    </div>
  </div>
  <div class="band">It is the exact discipline you sold for a decade at CEB:
     reps win when they walk in with insight, not when they prospect harder.
     <strong>We have automated the insight.</strong></div>""")

# ---- 03 · THE INSIGHT ------------------------------------------------------
add("WHAT I'VE BUILT", """
  <h2>An origination engine that turns market signals into partner-ready briefs.</h2>
  <p class="lead">Not a database — the market already has those. A <strong>judgment layer</strong>:
     it decides who to call this week, why now, which team, and hands you the
     brief to send, with every load-bearing fact checked.</p>
  <div class="pipeline">
    <div class="pstep"><div class="pn">1</div><div class="pt">SENSE</div>
      <p>Sweeps live signals — funding, IPO filings, new CMOs, expiring deals,
         exec moves — across F1 &amp; FE-relevant companies.</p></div>
    <div class="parrow">→</div>
    <div class="pstep"><div class="pn">2</div><div class="pt">SCORE</div>
      <p>Deterministic 5-pillar model (/100): Timing, Capacity, Brand Fit,
         Urgency, Ops Fit. Gates out anyone already on a grid or over-pitched.</p></div>
    <div class="parrow">→</div>
    <div class="pstep"><div class="pn">3</div><div class="pt">MATCH</div>
      <p>Team-fit engine maps the prospect to the right team and flags
         category clashes — so we never overclaim an owned lane.</p></div>
    <div class="parrow">→</div>
    <div class="pstep"><div class="pn">4</div><div class="pt">VERIFY &amp; SHIP</div>
      <p>Live-checks every figure, person and date against a primary source,
         then renders the brand-locked 2-page brief.</p></div>
  </div>
  <div class="band light">One signal a day. A weekly cadence — three Formula E,
     three Formula 1, and a Sunday "decision day" GO pick across both.</div>""")

# ---- 04 · THE TRUST LAYER --------------------------------------------------
add("WHY IT CAN SHIP UNATTENDED", """
  <h2>The moat isn't the AI. It's the verification discipline.</h2>
  <div class="cols2">
    <div>
      <div class="tl"><span class="tlb"></span><div><strong>Claim-level citations.</strong>
        Every figure, name and date is bound to a primary source URL — and must
        reappear in the prose, or the engine flags drift.</div></div>
      <div class="tl"><span class="tlb"></span><div><strong>A hard trust gate.</strong>
        A generic decision-maker, an uncited number, a stale fact or a category
        overclaim is a BLOCKER — the brief will not send until it's fixed.</div></div>
      <div class="tl"><span class="tlb"></span><div><strong>Conflict-checking.</strong>
        The team-fit engine refuses to claim "open category" on a team that
        already carries a rival in that lane.</div></div>
      <div class="tl"><span class="tlb"></span><div><strong>Truth over punch.</strong>
        When a claim can't be confirmed, the engine writes the weaker true
        sentence instead of the bold unverified one.</div></div>
    </div>
    <div class="proofcard">
      <div class="pcq">"Every figure verified to a primary source."</div>
      <div class="pcg">
        <div class="pc"><b>~$1.5B</b><span>Cohesity pro-forma ARR</span></div>
        <div class="pc"><b>28%</b><span>Adjusted cash-EBITDA margin</span></div>
        <div class="pc"><b>~$7.2B</b><span>Glean Series F valuation</span></div>
        <div class="pc"><b>2030</b><span>Mahindra Gen4 commitment</span></div>
      </div>
      <div class="pcn">This is what protects the logo. It is the difference
        between a tool and something you'd put your name behind.</div>
    </div>
  </div>""")

# ---- 05 · PROOF 1 — COHESITY ----------------------------------------------
add("PROOF · 01 — FORMULA 1", """
  <h2><span class="hd-co">Cohesity</span> → Cadillac F1 Team
     <span class="scoretab">82<small>/100 · HOT</small></span></h2>
  <div class="cols2 tight">
    <div>
      <div class="kk">THE SIGNAL</div>
      <p>Nvidia-backed, ~$1.5B pro-forma ARR at 28% margin after the Veritas
         combination, steering toward a <strong>2026 IPO</strong> benchmarked against Rubrik —
         and it has never touched motorsport.</p>
      <div class="kk">WHY NOW</div>
      <p>An IPO is the single largest brand-elevation moment in a company's life.
         The 12 months around it are when leadership spends on institutional
         credibility — exactly what a multi-year F1 deal trades in.</p>
      <div class="kk">THE MATCH</div>
      <p>No pure-play backup &amp; data-resilience brand owns the F1 grid. Cadillac
         debuts in 2026 with a greenfield tech roster (IFS for ERP, TWG for AI)
         and <strong>no data-protection partner</strong> — a founding lane to own, and a US
         flag-bearer for a US-market IPO.</p>
    </div>
    <div>
      <div class="dealbox">
        <div class="db-k">DEAL ARCHITECTURE</div>
        <div class="db-h">Founding Data Resilience Partner</div>
        <div class="db-row"><span>Term</span><b>3–4 years</b></div>
        <div class="db-row"><span>Value</span><b>$4–7M / yr</b></div>
        <div class="db-row"><span>Mode</span><b>A — tech in the car</b></div>
        <div class="db-row"><span>Decision-maker</span><b>Carol Carpenter, CMO</b></div>
        <div class="db-row last"><span>Crowding</span><b>~45 — early</b></div>
      </div>
      <div class="angle">"Carol — backup and ransomware-recovery is the one
         enterprise-resilience lane no brand on the F1 grid has claimed.
         Worth 25 minutes to own it before the roadshow locks?"</div>
    </div>
  </div>
  <div class="prooffoot">Full 2-page brief generated, verified and brand-locked
     by the engine — attached as <em>cohesity.pdf</em>.</div>""")

# ---- 06 · PROOF 2 — GLEAN --------------------------------------------------
add("PROOF · 02 — FORMULA E", """
  <h2><span class="hd-co">Glean</span> → Mahindra Racing
     <span class="scoretab">72<small>/100 · WARM</small></span></h2>
  <div class="cols2 tight">
    <div>
      <div class="kk">THE SIGNAL</div>
      <p>The enterprise "Work AI" leader: $150M Series F at <strong>~$7.2B</strong>,
         ~$300M ARR, 250M+ agentic actions, an acquisition already in 2026 — on a
         clear IPO trajectory, with no motorsport footprint.</p>
      <div class="kk">WHY NOW</div>
      <p>Scaling brand hard ahead of a listing, and the enterprise-AI lane in
         Formula E is <strong>uncontested</strong>. Category exclusivity is cheapest before a
         peer notices the open lane.</p>
      <div class="kk">THE MATCH</div>
      <p>Mahindra — a founding FE manufacturer committed to <strong>Gen4 through 2030</strong> —
         de-risks a multi-year deal, and its global enterprise parent group mirrors
         exactly the complex organisations Glean sells into.</p>
    </div>
    <div>
      <div class="dealbox">
        <div class="db-k">DEAL ARCHITECTURE</div>
        <div class="db-h">Official Work AI Partner</div>
        <div class="db-row"><span>Term</span><b>3+ years (to Gen4)</b></div>
        <div class="db-row"><span>Value</span><b>$3–4M / yr</b></div>
        <div class="db-row"><span>Mode</span><b>A — working deployment</b></div>
        <div class="db-row"><span>Decision-maker</span><b>Matt Kixmoeller, CMO</b></div>
        <div class="db-row last"><span>Grid fit</span><b>PRIME — greenfield</b></div>
      </div>
      <div class="angle">"Kix — Formula E's enterprise-AI lane is wide open, and
         Mahindra's committed to 2030, so a multi-year deal is de-risked.
         You'd own the category before the IPO. 25 minutes?"</div>
    </div>
  </div>
  <div class="prooffoot">Same engine, same standard — Formula E. Full brief
     attached as <em>glean.pdf</em>.</div>""")

# ---- 07 · PIPELINE ---------------------------------------------------------
add("THE PIPELINE TODAY", """
  <h2>This isn't two briefs. It's a scored, live pipeline.</h2>
  <table class="lead-tbl">
    <thead><tr><th>#</th><th>Prospect</th><th>Series</th><th>Recommended team</th>
      <th>Signal</th><th class="r">Score</th></tr></thead>
    <tbody>
      <tr><td>1</td><td><b>Ramp</b></td><td>F1</td><td>Racing Bulls</td><td>$750M raise · London race</td><td class="r">87</td></tr>
      <tr><td>2</td><td><b>JFrog</b></td><td>F1</td><td>McLaren</td><td>CMO who built McLaren–Udemy</td><td class="r">86</td></tr>
      <tr class="hl"><td>3</td><td><b>Cohesity</b></td><td>F1</td><td>Cadillac</td><td>2026 IPO · greenfield lane</td><td class="r">82</td></tr>
      <tr><td>4</td><td><b>Quantinuum</b></td><td>F1</td><td>Aston Martin</td><td>$12.7B IPO · new C-suite</td><td class="r">76</td></tr>
      <tr><td>5</td><td><b>1Password</b></td><td>FE</td><td>Andretti</td><td>2026 IPO lock</td><td class="r">72</td></tr>
      <tr class="hl"><td>6</td><td><b>Glean</b></td><td>FE</td><td>Mahindra</td><td>$7.2B · open AI lane</td><td class="r">72</td></tr>
      <tr><td>7</td><td><b>Plaid</b></td><td>FE</td><td>Jaguar TCS</td><td>new CMO · open-banking</td><td class="r">71</td></tr>
    </tbody>
  </table>
  <div class="band light">Eleven scored prospects live now, each gated, team-matched
     and ready to verify on demand. The two proofs are simply the picks I'd
     walk into a room with first. <em>Team-side signals tracked too — e.g. the
     Alpine/BWT title slot expiring end-2026.</em></div>""")

# ---- 08 · THE VISION -------------------------------------------------------
add("THE FULL POTENTIAL", """
  <h2>The brief is step one. The destination is a deal-ready room.</h2>
  <p class="lead">Today the engine delivers the <strong>signal</strong>. The roadmap turns each
     signal into everything a partner needs to walk in and transact — so 1440
     shows up not with a lead, but with the meeting already built.</p>
  <div class="ladder">
    <div class="rung on"><div class="rn">NOW</div><div class="rt">The Signal</div>
      <p>Verified 2-page brief: who, why now, which team, the opening angle.</p></div>
    <div class="rung on"><div class="rn">NOW</div><div class="rt">The Match</div>
      <p>Team-fit &amp; category-whitespace check, conflict-flagged.</p></div>
    <div class="rung next"><div class="rn">NEXT</div><div class="rt">Meeting-Ready</div>
      <p>Decision-maker contact path, tailored outreach sequence, the deck to send.</p></div>
    <div class="rung next"><div class="rn">NEXT</div><div class="rt">The Full Proposal</div>
      <p>Activation plan, inventory, pricing model, valuation &amp; the resourcing
         to deliver — a transaction-ready package, not just a tip.</p></div>
  </div>
  <div class="band">"Clients don't only get a sales signal — they get the meeting and
     the resources to close it." That is the product. The engine is how we get there.</div>""")

# ---- 09 · THE ASK ----------------------------------------------------------
add("THE ASK", """
  <h2>A mandate to run this as 1440's origination desk.</h2>
  <div class="cols3">
    <div class="askcard">
      <div class="an">01</div><div class="at">A defined role</div>
      <p>Own the origination desk inside 1440 — the engine is the function,
         and I run it as a recognised revenue line, not a side project.</p>
    </div>
    <div class="askcard">
      <div class="an">02</div><div class="at">A small budget</div>
      <p>To cover data/signal sources, verification and the build that turns the
         brief into the full meeting-ready proposal. Modest, and it pays for
         itself in partner hours saved.</p>
    </div>
    <div class="askcard gold">
      <div class="an">03</div><div class="at">A performance kicker</div>
      <p>An override on any deal that closes from an engine-sourced brief.
         It costs nothing until the desk delivers revenue — and aligns me
         entirely with 1440 winning.</p>
    </div>
  </div>
  <div class="metrics">
    <div class="mk">MEASURE ME ON TWO NUMBERS</div>
    <div class="mrow"><div class="mc"><b>Qualified briefs</b><span>verified, partner-ready, delivered</span></div>
      <div class="mc"><b>Meetings booked</b><span>for the partners, from those briefs</span></div></div>
  </div>""")

# ---- 10 · ROADMAP / CLOSE --------------------------------------------------
add("FIRST 90 DAYS", """
  <h2>Low cost, plugs into how we already sell, no new headcount.</h2>
  <div class="road">
    <div class="rblock"><div class="rh">DAYS 0–30 · PROVE</div>
      <ul><li>Run the desk live: one verified hero brief a day on the cadence.</li>
        <li>Point the engine at 3 prospects matched to 1440's warm teams
            (McLaren, Williams, Mahindra, Jaguar, Cadillac…).</li>
        <li>Land the first partner-led meeting from an engine brief.</li></ul></div>
    <div class="rblock"><div class="rh">DAYS 30–60 · BUILD THE NEXT RUNG</div>
      <ul><li>Add the meeting-ready layer: contact paths, outreach sequences,
            the send-deck.</li>
        <li>Start outcome tracking — brief → meeting → deal — as our proof
            and our proprietary data.</li></ul></div>
    <div class="rblock"><div class="rh">DAYS 60–90 · SYSTEMATISE</div>
      <ul><li>Stand up the full-proposal package on the strongest live opportunity.</li>
        <li>Review the two numbers; formalise the desk and the kicker.</li></ul></div>
  </div>
  <div class="closing">
    <div class="cl-k">THE BOTTOM LINE</div>
    <p>1440 already has the relationships and the credibility to close.
       The desk gives us the throughput to feed them — qualified, verified,
       and ready — without adding people. <strong>Let's run it for 90 days and let the
       two numbers decide.</strong></p>
  </div>""")

# ---- assemble --------------------------------------------------------------

def build() -> str:
    total = len(SLIDES)
    body = "\n".join(slide(inner, i + 1, total, kicker,
                           dark=(kicker == ""))
                     for i, (kicker, inner) in enumerate(SLIDES))
    return TEMPLATE.replace("{{BODY}}", body)


TEMPLATE = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<title>1440 Sports · The Origination Desk</title>
<style>
  :root{ --navy:#191a48; --gold:#d1ae7a; --ink:#1a1c2e; --muted:#6b6e84;
         --hair:#e2e0ea; --panel:#f5f4f8; --paper:#ffffff; }
  @page{ size:A4 landscape; margin:0; }
  *{ box-sizing:border-box; }
  body{ font-family:Georgia,"Times New Roman",serif; color:var(--ink); margin:0; }
  .slide{ position:relative; width:297mm; height:208mm; padding:13mm 16mm 9mm;
          page-break-after:always; background:var(--paper); overflow:hidden;
          display:flex; flex-direction:column; }
  .slide:last-child{ page-break-after:auto; }
  .slide.dark{ background:var(--navy); color:#eceaf3; }
  .shead{ display:flex; justify-content:space-between; align-items:center;
          border-bottom:2px solid var(--navy); padding-bottom:8px; }
  .slide.dark .shead{ border-bottom-color:var(--gold); }
  .shead .mark{ height:24px; }
  .khead{ font-family:Arial,sans-serif; font-size:7.5pt; letter-spacing:.22em;
          text-transform:uppercase; color:var(--muted); }
  .slide.dark .khead{ color:var(--gold); }
  .sbody{ flex:1; padding-top:11px; display:flex; flex-direction:column; justify-content:center; }
  .slide.dark .sbody{ justify-content:flex-end; }
  .sfoot{ display:flex; justify-content:space-between; font-family:Georgia,serif;
          font-size:7pt; letter-spacing:.12em; color:#9a98aa; padding-top:6px; }
  .slide.dark .sfoot{ color:#6f72a0; }

  h1{ font-size:46pt; font-weight:400; letter-spacing:-1px; color:#fff; margin:6px 0 0; line-height:1.02; }
  h2{ font-size:21pt; font-weight:400; color:var(--navy); margin:0 0 12px; letter-spacing:-.3px; line-height:1.12; }
  h2 em{ color:var(--gold); font-style:italic; }
  .slide.dark h2{ color:#fff; }
  p{ font-size:10.5pt; line-height:1.5; margin:0 0 8px; }
  .lead{ font-size:12pt; line-height:1.5; color:#33354f; margin-bottom:14px; }

  /* cover */
  .cover{ display:flex; flex-direction:column; justify-content:center; }
  .cover-rule{ width:64px; height:4px; background:var(--gold); margin-bottom:20px; }
  .eyebrow{ font-family:Arial,sans-serif; font-size:9pt; letter-spacing:.28em;
            text-transform:uppercase; color:var(--gold); margin-bottom:6px; }
  .cover .sub{ font-size:14pt; line-height:1.5; color:#c9c7e0; max-width:165mm; margin-top:14px; }
  .cover-meta{ display:flex; align-items:center; gap:14px; margin-top:30px;
               font-family:Arial,sans-serif; font-size:8.5pt; letter-spacing:.2em;
               text-transform:uppercase; color:#a8a6c8; }
  .cover-meta i{ width:5px; height:5px; background:var(--gold); border-radius:50%; display:inline-block; }

  /* columns + cards */
  .cols3{ display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin-bottom:8px; }
  .cols2{ display:grid; grid-template-columns:1fr 1fr; gap:22px; }
  .cols2.tight{ gap:18px; }
  .card{ border:1px solid var(--hair); border-top:3px solid var(--navy);
         border-radius:7px; padding:13px 15px; background:var(--panel); }
  .cardk{ font-family:Arial,sans-serif; font-size:8pt; letter-spacing:.16em;
          color:var(--gold); text-transform:uppercase; font-weight:700; margin-bottom:6px; }
  .card p{ font-size:9.8pt; margin:0; }

  .band{ margin-top:16px; background:var(--navy); color:#f3f1ea; border-left:5px solid var(--gold);
         border-radius:0 7px 7px 0; padding:13px 18px; font-size:11pt; line-height:1.5; }
  .band.light{ background:var(--panel); color:var(--navy); border-left-color:var(--gold); }
  .band strong{ color:var(--gold); }
  .band.light strong{ color:var(--navy); }

  /* pipeline */
  .pipeline{ display:flex; align-items:stretch; gap:7px; margin:6px 0 4px; }
  .pstep{ flex:1; border:1px solid var(--hair); border-radius:8px; padding:12px 13px; background:var(--paper); }
  .pn{ width:24px; height:24px; border-radius:50%; background:var(--navy); color:var(--gold);
       font-family:Arial,sans-serif; font-weight:700; font-size:11pt; display:flex;
       align-items:center; justify-content:center; }
  .pt{ font-family:Arial,sans-serif; font-size:9.5pt; font-weight:700; letter-spacing:.1em;
       color:var(--navy); text-transform:uppercase; margin:8px 0 5px; }
  .pstep p{ font-size:9pt; line-height:1.42; margin:0; color:#3c3e58; }
  .parrow{ display:flex; align-items:center; color:var(--gold); font-size:17pt; font-weight:700; }

  /* trust layer */
  .tl{ display:flex; gap:10px; margin-bottom:11px; font-size:10.3pt; line-height:1.42; }
  .tlb{ flex:none; width:9px; height:9px; margin-top:5px; background:var(--gold);
        transform:rotate(45deg); }
  .tl strong{ color:var(--navy); }
  .proofcard{ background:var(--navy); border-radius:9px; padding:18px 20px; color:#eceaf3; }
  .pcq{ font-style:italic; font-size:12pt; color:var(--gold); margin-bottom:14px; }
  .pcg{ display:grid; grid-template-columns:1fr 1fr; gap:11px; }
  .pc{ border:1px solid #34356a; border-radius:6px; padding:9px 11px; }
  .pc b{ font-size:17pt; color:#fff; display:block; }
  .pc span{ font-family:Arial,sans-serif; font-size:7.6pt; letter-spacing:.05em; color:#a8a6c8; }
  .pcn{ font-size:9pt; line-height:1.45; color:#c9c7e0; margin-top:14px; }

  /* proof slides */
  .hd-co{ color:var(--gold); }
  .scoretab{ float:right; background:var(--navy); color:#fff; border-radius:6px;
             padding:4px 12px; font-size:18pt; font-weight:700; font-family:Arial,sans-serif; }
  .scoretab small{ font-size:7.5pt; color:var(--gold); letter-spacing:.08em; }
  .kk{ font-family:Arial,sans-serif; font-size:8pt; letter-spacing:.15em; color:var(--gold);
       text-transform:uppercase; font-weight:700; margin:10px 0 3px; }
  .cols2 p{ font-size:9.8pt; line-height:1.44; }
  .dealbox{ border:1px solid var(--hair); border-radius:8px; overflow:hidden; }
  .db-k{ background:var(--navy); color:var(--gold); font-family:Arial,sans-serif; font-weight:700;
         font-size:8pt; letter-spacing:.16em; padding:7px 13px; }
  .db-h{ font-size:13pt; color:var(--navy); padding:9px 13px 6px; font-weight:700; }
  .db-row{ display:flex; justify-content:space-between; padding:5px 13px; font-size:9.6pt;
           border-top:1px solid var(--hair); }
  .db-row span{ color:var(--muted); font-family:Arial,sans-serif; font-size:8.4pt;
                letter-spacing:.08em; text-transform:uppercase; }
  .db-row b{ color:var(--navy); }
  .angle{ background:var(--panel); border-left:3px solid var(--gold); border-radius:0 7px 7px 0;
          padding:11px 14px; font-style:italic; font-size:10.2pt; color:var(--navy);
          line-height:1.45; margin-top:12px; }
  .prooffoot{ margin-top:14px; font-family:Arial,sans-serif; font-size:8.4pt; letter-spacing:.06em;
              color:var(--muted); text-transform:uppercase; }
  .prooffoot em{ color:var(--navy); font-style:normal; font-weight:700; }

  /* leaderboard */
  .lead-tbl{ width:100%; border-collapse:collapse; font-size:10pt; }
  .lead-tbl th{ font-family:Arial,sans-serif; font-size:7.6pt; letter-spacing:.12em;
                text-transform:uppercase; color:var(--muted); text-align:left;
                border-bottom:2px solid var(--navy); padding:7px 9px; }
  .lead-tbl td{ padding:7px 9px; border-bottom:1px solid var(--hair); color:#33354f; }
  .lead-tbl .r{ text-align:right; font-family:Arial,sans-serif; font-weight:700; color:var(--navy); }
  .lead-tbl tr.hl{ background:#fbf8f1; }
  .lead-tbl tr.hl b{ color:var(--navy); }

  /* vision ladder */
  .ladder{ display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin:6px 0; }
  .rung{ border:1px solid var(--hair); border-radius:8px; padding:13px 14px; background:var(--paper); }
  .rung.on{ border-top:3px solid var(--gold); }
  .rung.next{ border-top:3px dashed var(--navy); background:var(--panel); }
  .rn{ font-family:Arial,sans-serif; font-size:7.6pt; letter-spacing:.14em; font-weight:700; }
  .rung.on .rn{ color:var(--gold); }
  .rung.next .rn{ color:var(--navy); }
  .rt{ font-size:12.5pt; color:var(--navy); margin:5px 0 6px; }
  .rung p{ font-size:9pt; line-height:1.42; margin:0; color:#3c3e58; }

  /* ask */
  .askcard{ border:1px solid var(--hair); border-radius:8px; padding:15px 16px; background:var(--panel); }
  .askcard.gold{ background:var(--navy); color:#eceaf3; border-color:var(--navy); }
  .askcard.gold .at{ color:#fff; } .askcard.gold p{ color:#c9c7e0; }
  .askcard.gold .an{ color:var(--gold); }
  .an{ font-family:Arial,sans-serif; font-size:19pt; font-weight:700; color:var(--gold); }
  .at{ font-size:13pt; color:var(--navy); margin:3px 0 7px; font-weight:700; }
  .askcard p{ font-size:9.6pt; line-height:1.46; margin:0; }
  .metrics{ margin-top:16px; border:1px solid var(--hair); border-radius:8px; overflow:hidden; }
  .mk{ background:var(--navy); color:var(--gold); font-family:Arial,sans-serif; font-weight:700;
       font-size:8.5pt; letter-spacing:.18em; padding:8px 16px; }
  .mrow{ display:grid; grid-template-columns:1fr 1fr; }
  .mc{ padding:13px 16px; }
  .mc + .mc{ border-left:1px solid var(--hair); }
  .mc b{ font-size:15pt; color:var(--navy); display:block; }
  .mc span{ font-family:Arial,sans-serif; font-size:8.6pt; color:var(--muted); letter-spacing:.04em; }

  /* roadmap */
  .road{ display:grid; grid-template-columns:repeat(3,1fr); gap:14px; }
  .rblock{ border:1px solid var(--hair); border-radius:8px; padding:13px 15px; }
  .rh{ font-family:Arial,sans-serif; font-size:8.6pt; letter-spacing:.12em; font-weight:700;
       color:var(--gold); text-transform:uppercase; border-bottom:1px solid var(--hair);
       padding-bottom:6px; margin-bottom:7px; }
  .rblock ul{ margin:0; padding-left:15px; }
  .rblock li{ font-size:9.4pt; line-height:1.42; margin-bottom:5px; color:#3c3e58; }
  .closing{ margin-top:16px; background:var(--navy); border-radius:8px; padding:15px 20px; color:#f3f1ea; }
  .cl-k{ font-family:Arial,sans-serif; font-size:8pt; letter-spacing:.2em; color:var(--gold);
         font-weight:700; text-transform:uppercase; margin-bottom:5px; }
  .closing p{ font-size:11pt; line-height:1.5; margin:0; }
  .closing strong{ color:var(--gold); }
</style></head><body>
{{BODY}}
</body></html>"""


if __name__ == "__main__":
    html = build()
    out_html = os.path.join(_HERE, "1440-origination-desk.html")
    with open(out_html, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("HTML ->", out_html)
    try:
        from weasyprint import HTML
        doc = HTML(string=html, base_url=_HERE).render()
        out_pdf = os.path.join(_HERE, "1440-origination-desk.pdf")
        doc.write_pdf(out_pdf)
        print(f"PDF  -> {out_pdf}  ({len(doc.pages)} slides)")
    except Exception as exc:  # pragma: no cover
        print(f"[deck] PDF skipped ({exc.__class__.__name__}: {exc})")
