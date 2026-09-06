# Gatik → Lola Yamaha ABT Formula E Team — verification log (N° 234, 25 Aug 2026)

An n8n-engine row (4 Sep 2026, score 77, WARM, person Gautam Narang) rebuilt as a full case at no
model-API cost. Nothing n8n recorded was carried over; the trigger, the score, the person and the
team were all re-derived from live search.

**Sandbox limitation, stated plainly:** direct fetches of gatik.ai, qia.qa, williamsf1.com,
forbes.com, fleetowner.com and motorsport.com were blocked by the egress proxy. Every claim below
was checked against the search summary of the primary page named as the evidence URL. Treat each
VERIFIED line as REPORTED until a person opens the link. Confidence is MEDIUM and the footer reads
VERIFY BEFORE CIRCULATION.

## The trigger

**$200M Series D, announced 25 August 2026**, co-led by the **Qatar Investment Authority** and
**Koch Disruptive Technologies**, with Millennium Management, ARK Invest and Intact Private Capital
participating. It carries on **both** Gatik's own newsroom and QIA's own newsroom, so it is
company-confirmed rather than press-reported — the strongest class of trigger the engine takes.
It is 12 days before today, well inside the 90-day window, so the signal sits on 25 Aug 2026 rather
than on the 4 Sep row date n8n recorded.

## Ledger

| Claim | Status | Evidence |
|---|---|---|
| $200M Series D, 25 Aug 2026, co-led by QIA and Koch Disruptive Technologies | VERIFIED | gatik.ai and qia.qa newsrooms; Business Wire; Forbes 25 Aug 2026 |
| Millennium Management, ARK Invest, Intact Private Capital participating | VERIFIED | same release |
| >$600M contracted revenue, 85,000 driverless orders, 99% on-time | VERIFIED as the company's own stated figures — the copy says "the company reports" | Gatik release, 25 Aug 2026 |
| Walmart, Kroger, PepsiCo as named customers; ambient, refrigerated and frozen middle-mile routes | VERIFIED | Gatik release; FleetOwner, Sourcing Journal |
| Target of more than 100 driverless trucks by end 2026, thousands beyond | VERIFIED | Gatik release |
| HQ Santa Clara, California | VERIFIED | Gatik release dateline |
| Isuzu invested $30M in 2024; joint Level 4 chassis on NVIDIA compute; mass production from 2027 | VERIFIED | gatik.ai press release; Business Wire 20240514977000; Gatik/Isuzu/NVIDIA announcement Mar 2025 |
| Gautam Narang CEO & Co-Founder; Arjun Narang CTO; Apeksha Kumavat Chief Engineer; Patrick Archambault CFO; Paul Dilaura CCO; Judi Otteson CLO; no CMO listed | VERIFIED | gatik.ai/about, The Org, Craft |
| Zoox, Official Regional Partner of Williams Racing since Nov 2024, Formula 1's first autonomous-vehicle partnership, running at the team's American races | VERIFIED | williamsf1.com; GlobeNewswire 13 Nov 2024 |
| No autonomy/ADAS partner on any 2026 FE roster; Lola Yamaha ABT majors are Castore, OMP, Shell only; Andretti has TWG AI; Envision has Sand Technologies; Jaguar has TCS and Chase; Mahindra has Tech Mahindra; Porsche has TDK; DHL at championship level in both series; Ceva at Ferrari; Luminar departed Mercedes | VERIFIED | sponsor table (`seeds/sponsors.json`) |
| Season 13: 21 races, 13 cities; Jeddah opener 18 Dec 2026; Austin 6 Feb 2027; Miami 20 Feb 2027; Tokyo finale 24-25 Jul 2027 | VERIFIED | calendar table (`seeds/calendar_fe.json`) |
| DS Automobiles leaving Formula E after the London finale; Penske squad expected to stay | REPORTED — labelled "reported" in the rule-out | Motorsport.com |

## The screen-out that was considered and rejected, twice

This case was drafted as a **screen-out** and then re-opened, and the reasoning is worth recording.

1. **First pass — below threshold.** Autonomous freight has no operational workstream at a race
   team; the buyer is a Fortune 50 supply-chain executive who is not in the grandstand; the $200M is
   earmarked for fleet and safety validation; and a driverless-trucking brand arguably cannot afford
   to be associated with speed. On those pillars the honest score landed at 67 — below 70, so no case.
2. **What changed it.** A clash-check of the sponsor table turned up **Zoox, active at Atlassian
   Williams Racing**, and Luminar (lidar) as a departed Mercedes partner. An autonomous-vehicle
   company has therefore already bought a Formula 1 seat, in a multi-year deal that both parties
   billed as the sport's first AV partnership. That is a verified category precedent, and it answers
   the off-brand objection empirically rather than by assertion. Brand fit moves from 12 to 14 and
   the signal clears at **71** — a genuine HOT, not an inflated one.

The first-pass objections are not buried: the off-brand risk is the first risk row, the earmarked
capital is the second, and the Mode B disclosure is the first paragraph of the value section on the
app page.

## The team choice, and a false lead that was killed

**DS Penske was the first pick and it was wrong.** The thesis was that Penske Truck Leasing — a
440,000-vehicle North American fleet business — would give Gatik a commercial path through the
team's owner. A live check killed it: the Formula E entry is **Jay Penske's** Penske Autosport
(formerly Dragon Racing), not Roger Penske's Penske Corporation, and DS Automobiles is reported to
be leaving the championship after the London finale. Neither half of the thesis survived, and DS
Penske is ruled out on the record rather than quietly dropped.

**The manufacturer clash-check drove the final choice.** Isuzu is a $30M investor co-developing
Gatik's 2027 truck, so Formula E entries fronted by commercial-vehicle manufacturers are out on
conflict: Nissan, Mahindra, Citroen and Cupra Kiro (Volkswagen Group). Andretti and Envision are out
on an occupied AI lane, Jaguar on TCS, Porsche on TDK. Lola Yamaha ABT is what survives — and it
survives positively, not by elimination: it has no software, data or technology partner at all, its
parents are a constructor, an operator and an engine maker rather than a car marque, and Season 13
finishes at Yamaha's home round in Tokyo.

## Honest score — what holds it back (71, not the 77 n8n recorded)

- **Ops fit 12/20.** Mode B. No team deploys an autonomous-freight stack, and the brief says so in
  the first line of the value section. That single pillar is what keeps this out of the 80s.
- **Urgency 12/20.** There is no deadline. The Isuzu mass-production launch in 2027 is a ramp, not
  a cliff, and the decision can slip two quarters at no cost.
- **Brand fit 14/20.** Zoox proves the category will buy racing, but Gatik's purchase decision sits
  with a supply-chain executive at Walmart or PepsiCo, not with a Formula E viewer.
- **Capacity 16/20.** $200M is real money, but it is raised against a fleet target, and a Series D
  company is a smaller cheque than the mature public names this desk usually scores in the 80s.

## Leadership ties

`leadership_ties`: **none found**. Gautam Narang, Arjun Narang, Apeksha Kumavat, Patrick
Archambault, Paul Dilaura and Judi Otteson show no Formula 1 or Formula E role in any listing
checked, and no prior sponsorship deal structured by any of them was found.

## Not claimed

- **No revenue figure is presented as audited.** "$600M of contracted revenue" is the company's own
  number from its own release and is attributed that way in the copy.
- **No valuation** is stated: none was disclosed with the Series D and none is inferred.
- **No total-funding figure** is used: the reported totals varied across secondary sources.
- **Deal size ($1.5-3M a year) is an ESTIMATE** and is labelled as such on the app page.
- **DHL holds logistics at championship level in both series** and Ceva Logistics sits at Ferrari.
  Gatik is autonomous-driving software rather than a freight forwarder, so this is treated as an
  adjacency and named in the rule-outs, not as a hard clash.

## Ledger as built (N° 234, 26 verified)

| Section | Type | Load-bearing | Status | Claim |
|---|---|---|---|---|
| decision_maker | person_role | yes | verified | Gautam Narang, CEO & Co-Founder at Gatik |
| decision_maker | person_role | yes | verified | Gautam Narang, CEO & Co-Founder, Gatik at Gatik |
| key_facts | funding | yes | verified | $200M Series D co-led by the Qatar Investment Authority and Koch Disruptive Technologies, announced 25 August 2026 |
| deck | funding | yes | verified | Gatik announced a $200M Series D on 25 August, co-led by the Qatar Investment Authority and Koch Disruptive Technologies, on more than $600M of contracted drive |
| key_facts | funding | yes | verified | QIA and Koch Disruptive Technologies as co-leads, with Millennium Management, ARK Invest and Intact Private Capital participating; Isuzu invested $30M in 2024 |
| the_case_p1 | funding | yes | verified | Gatik announced $200M of Series D financing from Santa Clara on 25 August, co-led by the Qatar Investment Authority and Koch Disruptive Technologies, with Mille |
| key_facts | revenue | yes | verified | More than $600M of contracted revenue, 85,000 completed fully driverless orders and 99% on-time delivery, per the company's own announcement |
| the_case_p1 | revenue | yes | verified | The company reports more than $600M of contracted revenue, 85,000 completed fully driverless orders and 99% on-time delivery, moving ambient, refrigerated and f |
| key_facts | date | yes | verified | $200M Series D announced from Santa Clara on 25 August 2026 |
| bottom_line | revenue | yes | verified | A $200M Series D on 25 August, more than $600M of contracted revenue and a direct peer already running on a Formula 1 car put Gatik at the moment an autonomy br |
| key_facts | sponsorship | yes | verified | Zoox, Amazon's robotaxi business, has been an Official Regional Partner of Atlassian Williams Racing since November 2024 in Formula 1's first autonomous-vehicle |
| extended | funding | no | verified | Gatik announced $200M of Series D financing on 25 August 2026 from its Santa Clara headquarters, co-led by the Qatar Investment Authority and Koch Disruptive Te |
| key_facts | other | yes | verified | Isuzu, a $30M investor since 2024, is jointly developing a Level 4 chassis with Gatik on NVIDIA compute for mass production from 2027; the fleet target is more  |
| extended | revenue | no | verified | Gatik states more than $600M of contracted revenue, 85,000 completed fully driverless orders and 99% on-time delivery. |
| key_facts | other | yes | verified | Headquarters in Santa Clara, California, running driverless middle-mile routes for Walmart, Kroger and PepsiCo |
| extended | funding | no | verified | Isuzu put $30M into Gatik in 2024 and the two are jointly developing a chassis built for a Level 4 system, running on NVIDIA compute, targeting mass production  |
| trigger | date | yes | verified | funding round |
| extended | funding | no | verified | And a Formula E designation is affordable for a company whose $200M round is earmarked for fleet and safety validation, which a Formula 1 team-major position is |
| extended | funding | no | verified | Estimated at $1.5-3M a year - an estimate, not a quoted price. |
| why_now_callout | event | yes | verified | Jeddah E-Prix |
| why_now_callout | event | yes | verified | Austin E-Prix and the Miami E-Prix follow in February 2027 |
| extended | event | no | verified | Jeddah E-Prix on 18 December 2026 |
| extended | event | no | verified | Austin E-Prix on 6 February 2027 |
| extended | event | no | verified | Miami E-Prix |
| extended | event | no | verified | Tokyo E-Prix closing on 24-25 July 2027 |
| extended | event | no | verified | Austin E-Prix |
