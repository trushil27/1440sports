import type { BriefDetail } from "@/lib/types";

function GateValue({ value }: { value: unknown }) {
  if (typeof value === "boolean") return <span className={value ? "pill pill-ok" : "pill pill-bad"}>{value ? "Pass" : "Fail"}</span>;
  if (value === null || value === undefined) return <span className="text-muted">—</span>;
  if (typeof value === "object") {
    const o = value as Record<string, unknown>;
    const passed = "passed" in o ? o.passed : "pass" in o ? o.pass : "ok" in o ? o.ok : undefined;
    const note = (o.reason ?? o.note ?? o.detail ?? o.value) as unknown;
    return (
      <span className="inline-flex flex-wrap items-center gap-2">
        {typeof passed === "boolean" && <span className={passed ? "pill pill-ok" : "pill pill-bad"}>{passed ? "Pass" : "Fail"}</span>}
        {note !== undefined && <span className="text-sm">{typeof note === "string" ? note : JSON.stringify(note)}</span>}
        {typeof passed !== "boolean" && note === undefined && <code className="text-xs">{JSON.stringify(o)}</code>}
      </span>
    );
  }
  return <span className="text-sm">{String(value)}</span>;
}

export function ScoreComposition({ comp, score }: { comp: BriefDetail["score_composition"]; score: number | null }) {
  const cells = comp.cells ?? [];
  const gates = comp.gate_results && typeof comp.gate_results === "object" ? Object.entries(comp.gate_results) : [];
  const breakdown = comp.breakdown && typeof comp.breakdown === "object" ? Object.entries(comp.breakdown) : [];
  return (
    <section id="score" className="scroll-mt-20">
      <h2 className="h-rule">Score composition</h2>
      {cells.length === 0 ? (
        <p className="text-sm text-muted">No score cells stored for this brief.</p>
      ) : (
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-5">
          {cells.map((c, i) => (
            <div key={i} className="panel p-3">
              <div className="chip-k">{c.label}</div>
              <div className="mt-1 font-ui text-xl font-bold text-navy dark:text-gold">
                {c.num}
                <span className="ml-1 text-xs font-normal text-muted">{c.denom}</span>
              </div>
              <p className="mt-1 text-xs leading-snug text-ink/80">{c.note}</p>
            </div>
          ))}
        </div>
      )}
      <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 font-ui text-xs text-muted">
        <span>
          Total <b className="text-ink">{score ?? "—"}</b> / 100
        </span>
        {typeof comp.alumni_boost === "number" && comp.alumni_boost !== 0 && (
          <span>
            Alumni boost <b className="text-ink">+{comp.alumni_boost}</b>
          </span>
        )}
      </div>
      {(gates.length > 0 || breakdown.length > 0) && (
        <details className="mt-3">
          <summary className="kicker cursor-pointer">Gate results &amp; raw breakdown</summary>
          <div className="mt-2 grid gap-4 md:grid-cols-2">
            {gates.length > 0 && (
              <dl className="panel divide-y divide-hair">
                {gates.map(([k, v]) => (
                  <div key={k} className="flex items-start justify-between gap-3 px-3 py-2">
                    <dt className="font-ui text-xs uppercase tracking-wider text-muted">{k.replace(/_/g, " ")}</dt>
                    <dd className="text-right">
                      <GateValue value={v} />
                    </dd>
                  </div>
                ))}
              </dl>
            )}
            {breakdown.length > 0 && (
              <dl className="panel divide-y divide-hair">
                {breakdown.map(([k, v]) => (
                  <div key={k} className="flex items-start justify-between gap-3 px-3 py-2">
                    <dt className="font-ui text-xs uppercase tracking-wider text-muted">{k.replace(/_/g, " ")}</dt>
                    <dd className="text-right text-sm">{typeof v === "object" ? <code className="text-xs">{JSON.stringify(v)}</code> : String(v)}</dd>
                  </div>
                ))}
              </dl>
            )}
          </div>
        </details>
      )}
    </section>
  );
}
