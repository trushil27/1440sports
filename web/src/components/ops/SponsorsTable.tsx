"use client";

import { useEffect, useState } from "react";
import { ApiError, ops } from "@/lib/api";
import { fmtDate } from "@/lib/format";
import type { SponsorRow } from "@/lib/types";
import { useToast } from "../Toast";

const STATUSES = ["active", "joined", "departed", "unverified"] as const;

export function SponsorsTable() {
  const toast = useToast();
  const [rows, setRows] = useState<SponsorRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [series, setSeries] = useState("");
  const [team, setTeam] = useState("");
  const [q, setQ] = useState("");
  const [editing, setEditing] = useState<number | null>(null);
  const [draft, setDraft] = useState<{ category: string; status: SponsorRow["status"] } | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const t = window.setTimeout(() => {
      setRows(null);
      ops
        .sponsors({ series: series || undefined, team: team || undefined, q: q || undefined })
        .then(setRows)
        .catch((err) => setError(err instanceof ApiError ? err.detail : "Could not load sponsors."));
    }, 250);
    return () => window.clearTimeout(t);
  }, [series, team, q]);

  const save = async (s: SponsorRow) => {
    if (!draft) return;
    setBusy(true);
    try {
      const updated = await ops.updateSponsor(s.id, {
        series: s.series,
        level: s.level,
        team: s.team,
        brand: s.brand,
        category: draft.category || null,
        status: draft.status,
        season: s.season,
        notes: s.notes,
        source: null,
      });
      setRows((xs) => (xs ? xs.map((x) => (x.id === s.id ? updated : x)) : xs));
      setEditing(null);
      toast("Sponsor saved.", "ok");
    } catch (err) {
      toast(err instanceof ApiError ? err.detail : "Could not save.", "error");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="grid gap-2 font-ui text-sm sm:grid-cols-4">
        <select className="field" value={series} onChange={(e) => setSeries(e.target.value)} aria-label="Series">
          <option value="">All series</option>
          <option value="F1">Formula 1</option>
          <option value="FE">Formula E</option>
        </select>
        <input className="field" placeholder="Team" value={team} onChange={(e) => setTeam(e.target.value)} />
        <input className="field sm:col-span-2" placeholder="Brand or category" value={q} onChange={(e) => setQ(e.target.value)} />
      </div>
      {error && <p className="text-sm text-bad">{error}</p>}
      {!rows ? (
        <p className="kicker">Loading…</p>
      ) : rows.length === 0 ? (
        <p className="text-sm text-muted">No sponsors match.</p>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-hair">
          <table className="w-full min-w-[56rem] text-left font-ui text-xs">
            <thead className="kicker bg-panel">
              <tr>
                <th className="px-3 py-2">Series</th>
                <th className="px-3 py-2">Team</th>
                <th className="px-3 py-2">Brand</th>
                <th className="px-3 py-2">Level</th>
                <th className="px-3 py-2">Category</th>
                <th className="px-3 py-2">Status</th>
                <th className="px-3 py-2">Season</th>
                <th className="px-3 py-2">Verified</th>
                <th className="px-3 py-2" />
              </tr>
            </thead>
            <tbody className="divide-y divide-hair">
              {rows.map((s) => {
                const ed = editing === s.id && draft;
                return (
                  <tr key={s.id}>
                    <td className="px-3 py-2">{s.series}</td>
                    <td className="px-3 py-2 text-ink/80">{s.team || "—"}</td>
                    <td className="px-3 py-2 font-medium text-ink">{s.brand}</td>
                    <td className="px-3 py-2 text-muted">{s.level.replace(/_/g, " ")}</td>
                    <td className="px-3 py-2">
                      {ed ? <input className="field py-1" value={draft.category} onChange={(e) => setDraft({ ...draft, category: e.target.value })} /> : s.category || "—"}
                    </td>
                    <td className="px-3 py-2">
                      {ed ? (
                        <select className="field py-1" value={draft.status} onChange={(e) => setDraft({ ...draft, status: e.target.value as SponsorRow["status"] })}>
                          {STATUSES.map((st) => (
                            <option key={st} value={st}>
                              {st}
                            </option>
                          ))}
                        </select>
                      ) : (
                        <span className={s.status === "active" || s.status === "joined" ? "pill pill-ok" : s.status === "departed" ? "pill pill-muted" : "pill pill-warn"}>{s.status}</span>
                      )}
                    </td>
                    <td className="px-3 py-2 text-muted">{s.season || "—"}</td>
                    <td className="px-3 py-2 text-muted">
                      {s.verified_at ? fmtDate(s.verified_at) : "—"}
                      {s.source && <span className="block max-w-[12rem] truncate" title={s.source}>{s.source}</span>}
                    </td>
                    <td className="px-3 py-2 text-right whitespace-nowrap">
                      {ed ? (
                        <>
                          <button type="button" className="btn btn-primary px-3 py-1" disabled={busy} onClick={() => save(s)}>
                            Save
                          </button>{" "}
                          <button type="button" className="btn px-3 py-1" onClick={() => setEditing(null)}>
                            Cancel
                          </button>
                        </>
                      ) : (
                        <button
                          type="button"
                          className="btn px-3 py-1"
                          onClick={() => {
                            setEditing(s.id);
                            setDraft({ category: s.category ?? "", status: s.status });
                          }}
                        >
                          Edit
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
