"use client";

import { useEffect, useState } from "react";
import { ApiError, ops } from "@/lib/api";
import type { AlumniRow } from "@/lib/types";
import { useToast } from "../Toast";

type Draft = Pick<AlumniRow, "current_role" | "current_company" | "outreach_status" | "active">;

export function AlumniTable() {
  const toast = useToast();
  const [rows, setRows] = useState<AlumniRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState<number | null>(null);
  const [draft, setDraft] = useState<Draft | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    ops
      .alumni()
      .then(setRows)
      .catch((err) => setError(err instanceof ApiError ? err.detail : "Could not load alumni."));
  }, []);

  const start = (a: AlumniRow) => {
    setEditing(a.id);
    setDraft({ current_role: a.current_role, current_company: a.current_company, outreach_status: a.outreach_status, active: a.active });
  };

  const save = async (id: number) => {
    if (!draft) return;
    setBusy(true);
    try {
      const updated = await ops.updateAlumni(id, {
        current_role: draft.current_role || undefined,
        current_company: draft.current_company || undefined,
        outreach_status: draft.outreach_status || undefined,
        active: draft.active,
      });
      setRows((xs) => (xs ? xs.map((x) => (x.id === id ? updated : x)) : xs));
      setEditing(null);
      toast("Alumni record saved.", "ok");
    } catch (err) {
      toast(err instanceof ApiError ? err.detail : "Could not save.", "error");
    } finally {
      setBusy(false);
    }
  };

  if (error) return <p className="text-sm text-bad">{error}</p>;
  if (!rows) return <p className="kicker">Loading…</p>;
  if (rows.length === 0) return <p className="text-sm text-muted">No alumni records stored.</p>;

  return (
    <div className="overflow-x-auto rounded-xl border border-hair">
      <table className="w-full min-w-[60rem] text-left font-ui text-xs">
        <thead className="kicker bg-panel">
          <tr>
            <th className="px-3 py-2">Name</th>
            <th className="px-3 py-2">Previously</th>
            <th className="px-3 py-2">Deal</th>
            <th className="px-3 py-2">Current role</th>
            <th className="px-3 py-2">Current company</th>
            <th className="px-3 py-2">Tier</th>
            <th className="px-3 py-2">Outreach</th>
            <th className="px-3 py-2">Active</th>
            <th className="px-3 py-2" />
          </tr>
        </thead>
        <tbody className="divide-y divide-hair">
          {rows.map((a) => {
            const ed = editing === a.id && draft;
            return (
              <tr key={a.id} className={a.active ? "" : "opacity-60"}>
                <td className="px-3 py-2 font-medium text-ink">{a.name}</td>
                <td className="px-3 py-2 text-ink/80">
                  {a.previous_role || "—"}
                  {a.previous_company && <span className="block text-muted">{a.previous_company}</span>}
                </td>
                <td className="px-3 py-2 text-ink/80">{a.deal_involvement || "—"}</td>
                <td className="px-3 py-2">
                  {ed ? <input className="field py-1" value={draft.current_role ?? ""} onChange={(e) => setDraft({ ...draft, current_role: e.target.value })} /> : a.current_role || "—"}
                </td>
                <td className="px-3 py-2">
                  {ed ? <input className="field py-1" value={draft.current_company ?? ""} onChange={(e) => setDraft({ ...draft, current_company: e.target.value })} /> : a.current_company || "—"}
                </td>
                <td className="px-3 py-2">
                  <span className={a.tier === "strict" ? "pill pill-navy" : "pill pill-muted"}>{a.tier}</span>
                  {typeof a.boost_applied === "number" && <span className="block text-muted">+{a.boost_applied}</span>}
                </td>
                <td className="px-3 py-2">
                  {ed ? <input className="field py-1" value={draft.outreach_status ?? ""} onChange={(e) => setDraft({ ...draft, outreach_status: e.target.value })} /> : a.outreach_status || "—"}
                </td>
                <td className="px-3 py-2">
                  {ed ? <input type="checkbox" checked={draft.active} onChange={(e) => setDraft({ ...draft, active: e.target.checked })} /> : a.active ? "Yes" : "No"}
                </td>
                <td className="px-3 py-2 text-right whitespace-nowrap">
                  {ed ? (
                    <>
                      <button type="button" className="btn btn-primary px-3 py-1" disabled={busy} onClick={() => save(a.id)}>
                        Save
                      </button>{" "}
                      <button type="button" className="btn px-3 py-1" onClick={() => setEditing(null)}>
                        Cancel
                      </button>
                    </>
                  ) : (
                    <button type="button" className="btn px-3 py-1" onClick={() => start(a)}>
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
  );
}
