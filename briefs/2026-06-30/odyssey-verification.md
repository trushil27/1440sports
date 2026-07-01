# Verification log — Odyssey (2026-06-30 F1 hero)

**Re-verified live via WebSearch on 2026-06-30.** One line per load-bearing claim →
VERIFIED / CORRECTED / UNVERIFIED, with the source checked. (Record was built by a
prior session on 2026-06-21 and never shipped; every fact re-checked from scratch.)

> Tooling note: `verify_brief.py --net` is non-functional in this container (no
> outbound network from the shell → all citations show `cite_dead`, incl. on the
> known-good Cohesity brief). Live verification is done via WebSearch/WebFetch.

## Already-sent check (log + disk)
- **VERIFIED net-new.** `odyssey` never appears in the history log and there is no
  `odyssey.pdf` on disk before today. Never featured or bench-rendered.

## Load-bearing claims
1. **$310M Series B at a $1.45B valuation; announced 17 Jun 2026.**
   → **VERIFIED.** TechCrunch (17 Jun 2026), HPCwire, Unite.AI, theaiinsider, Odyssey's
   own release. Consistent across all.
2. **Round led by Natural Capital; participants Amazon, AMD Ventures, GV (Alphabet),
   EQT, In-Q-Tel.** → **VERIFIED.** TechCrunch + Odyssey release. AWS named as
   preferred cloud provider (AWS Trainium + AMD compute).
3. **NVIDIA as an investor (was in the prior-session record).**
   → **CORRECTED / REMOVED.** Not listed by TechCrunch, HPCwire, or Odyssey's own
   release; the round syndicate is Natural Capital/Amazon/AMD/GV/EQT/IQT and the
   compute stack is AWS+AMD. Only a single secondary outlet's headline implied NVIDIA;
   treated as unconfirmed and struck from thesis, the_case, headline, score_rationale,
   value_to_team, key_facts and sources.
4. **Founders: CEO Oliver Cameron (built Voyage, acquired by Cruise); CTO Jeff Hawke
   (ex-Wayve).** → **VERIFIED.** TechCrunch, Unite.AI.
5. **Builds generative "world models" (neural simulation of physical environments;
   robotics/AV/science/gaming).** → **VERIFIED.** Odyssey release, TechCrunch.
6. **Odyssey has no existing motorsport presence (already_present = false).**
   → **VERIFIED.** Searched; none found.

## Conflict check (prospect's backers/partners vs recommended team's rivals)
- **Team CORRECTED: Williams → Alpine.** The prior record pointed at **Williams**, but
  Williams's official AI partner is **Anthropic** ("Thinking Partner," multi-year,
  explicitly covering race strategy, car development and simulator work) — a direct
  collision with an AI world-model/simulation deal. Verified via Axios/SI/AI Magazine.
- **F1 AI lane is crowded** (also verified): CoreWeave–Aston Martin (AI cloud; wind
  tunnel named for it), TWG AI–Cadillac, Google–McLaren. **CoreWeave was itself
  screened out today as already_present** before landing on Odyssey.
- **Alpine chosen:** works F1 team with a full-scale simulator and **no incumbent AI or
  simulation partner** (open lane). Odyssey's backers (Amazon/AWS, AMD, Alphabet's GV,
  Natural Capital, In-Q-Tel) are diversified VCs/vendors — **none is an OEM with a
  board seat or an Alpine rival**, so no partner-politics conflict (the ProLogium–
  Mercedes failure mode does not apply here).

## Honest limitations (kept in the brief, not scored away)
- Early **research lab** — sponsorship appetite/budget unproven → capacity 14, WARM.
- Workstream is **frontier**, not turnkey → ops_fit scored MODE-A but "emerging."
- F1 AI/simulation is **contested** → brand_fit trimmed; distinct sub-lane argued honestly.

## Result
6 load-bearing claims VERIFIED; 1 fabricated investor (NVIDIA) CORRECTED-OUT; team
CORRECTED off a conflict (Williams→Alpine). Score 72 WARM, honest. Alpine reads PRIME
LANE (open roster). 0 blockers, 2 pages.
