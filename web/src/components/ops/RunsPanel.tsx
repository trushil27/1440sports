"use client";

import { useEffect, useState } from "react";
import { ApiError, ops } from "@/lib/api";
import { decisionLabel, fmtDate, fmtDateTime } from "@/lib/format";
import type { CandidateReason, OpsRun } from "@/lib/types";

function statusClass(s: string) {
  if (s === "success") return "pill pill-ok";
  if (s === "failed") return "pill pill-bad";
  if (s === "no_signal") return "pill pill-warn";
  return "pill pill-muted";
}

export function RunsPanel() {
  const [runs, setRuns] = useState<OpsRun[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [open, setOpen] = useState<number | null>(null);
  const [cands, setCands] = useState<Record<number, CandidateReason[] | "loading" | string>>({});

  useEffect(() => {
    ops
      .runs(60)
      .then(setRuns)
      .catch((err) => setError(err instanceof ApiError ? err.detail : "Could not load runs."));
  }, []);

  const toggle = async (id: number) => {
    if (open === id) {
      setOpen(null);
      return;
    }
    setOpen(id);
    if (cands[id]) return;
    setCands((c) => ({ ...c, [id]: "loading" }));
    try {
      const rows = await ops.candidates(id);
      setCands((c) => ({ ...c, [id]: rows }));
    } catch (err) {
      setCands((c) => ({ ...c, [id]: err instanceof ApiError ? err.detail : "Could not load candidates." }));
    }
  };

  if (error) return <p className="text-sm text-bad">{error}</p>;
  if (!runs) return <p className="kicker">Loading…</p>;
  if (runs.length === 0) return <p className="text-sm text-muted">No runs recorded yet.</p>;

  return (
    <div className="space-y-2">
      {runs.map((r) => {
        const c = cands[r.id];
        return (
          <div key={r.id} className="panel overflow-hidden">
            <button type="button" onClick={() => toggle(r.id)} className="flex w-full flex-wrap items-center gap-x-3 gap-y-1 px-4 py-3 text-left hover:bg-panel-2">
              <span className="font-ui font-medium">{fmtDate(r.date)}</span>
              <span className={statusClass(r.status)}>{r.status.replace(/_/g, " ")}</span>
              <span className="pill pill-muted">{r.mode.replace(/_/g, " ")}</span>
              {r.attempt > 1 && <span className="kicker">attempt {r.attempt}</span>}
              <span className="kicker">{r.candidates} candidates</span>
              <span className="ml-auto font-ui text-xs text-muted">
                {r.started_at && fmtDateTime(r.started_at)}
                {r.finished_at && ` → ${fmtDateTime(r.finished_at)}`}
              </span>
            </button>
            {open === r.id && (
              <div className="border-t border-hair px-4 py-3 text-sm">
                {r.summary && <p className="mb-2">{r.summary}</p>}
                {r.error && <p className="mb-2 text-bad">{r.error}</p>}
                {r.models && (
                  <p className="kicker mb-3">
                    {Object.entries(r.models)
                      .map(([k, v]) => `${k}: ${v}`)
                      .join(" · ")}
                  </p>
                )}
                {c === "loading" || c === undefined ? (
                  <p className="kicker">Loading candidates…</p>
                ) : typeof c === "string" ? (
                  <p className="text-bad">{c}</p>
                ) : c.length === 0 ? (
                  <p className="text-muted">No candidates recorded for this run.</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full min-w-[40rem] text-left font-ui text-xs">
                      <thead className="kicker">
                        <tr>
                          <th className="py-1 pr-3">#</th>
                          <th className="py-1 pr-3">Company</th>
                          <th className="py-1 pr-3">Score</th>
                          <th className="py-1 pr-3">Decision</th>
                          <th className="py-1">Reason</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-hair">
                        {c.map((row, i) => (
                          <tr key={i} className={row.decision === "selected" ? "bg-ok-bg/40" : ""}>
                            <td className="py-1.5 pr-3 text-muted">{row.rank ?? "—"}</td>
                            <td className="py-1.5 pr-3 font-medium text-ink">{row.company}</td>
                            <td className="py-1.5 pr-3">{row.score ?? "—"}</td>
                            <td className="py-1.5 pr-3">
                              <span className={row.decision === "selected" ? "pill pill-ok" : "pill pill-muted"}>{decisionLabel(row.decision)}</span>
                            </td>
                            <td className="py-1.5 text-ink/80">{row.reason || "—"}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
