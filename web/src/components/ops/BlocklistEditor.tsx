"use client";

import { useEffect, useState } from "react";
import { ApiError, ops } from "@/lib/api";
import { fmtDate } from "@/lib/format";
import type { BlocklistRow } from "@/lib/types";
import { useToast } from "../Toast";

const STATUSES = ["active", "cooling", "closed_lost"] as const;

export function BlocklistEditor() {
  const toast = useToast();
  const [rows, setRows] = useState<BlocklistRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ company: "", status: "active", reason: "", cooling_until: "", notes: "" });
  const [busy, setBusy] = useState(false);

  const load = () =>
    ops
      .blocklist()
      .then(setRows)
      .catch((err) => setError(err instanceof ApiError ? err.detail : "Could not load the blocklist."));

  useEffect(() => {
    void load();
  }, []);

  const add = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    try {
      await ops.addBlocklist({
        company: form.company.trim(),
        status: form.status,
        reason: form.reason.trim() || null,
        cooling_until: form.cooling_until || null,
        notes: form.notes.trim() || null,
      });
      setForm({ company: "", status: "active", reason: "", cooling_until: "", notes: "" });
      await load();
      toast("Blocklist updated.", "ok");
    } catch (err) {
      toast(err instanceof ApiError ? err.detail : "Could not add.", "error");
    } finally {
      setBusy(false);
    }
  };

  const remove = async (row: BlocklistRow) => {
    if (!window.confirm(`Remove ${row.company} from the blocklist?`)) return;
    try {
      await ops.deleteBlocklist(row.id);
      setRows((xs) => (xs ? xs.filter((x) => x.id !== row.id) : xs));
    } catch (err) {
      toast(err instanceof ApiError ? err.detail : "Could not delete.", "error");
    }
  };

  return (
    <div className="space-y-6">
      <form onSubmit={add} className="panel grid gap-2 p-4 font-ui text-sm sm:grid-cols-6">
        <input className="field sm:col-span-2" required placeholder="Company" value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value })} />
        <select className="field" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
          {STATUSES.map((s) => (
            <option key={s} value={s}>
              {s.replace(/_/g, " ")}
            </option>
          ))}
        </select>
        <input className="field" type="date" value={form.cooling_until} onChange={(e) => setForm({ ...form, cooling_until: e.target.value })} aria-label="Cooling until" />
        <input className="field sm:col-span-2" placeholder="Reason" value={form.reason} onChange={(e) => setForm({ ...form, reason: e.target.value })} />
        <input className="field sm:col-span-5" placeholder="Notes" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
        <button type="submit" className="btn btn-primary" disabled={busy}>
          {busy ? "Saving…" : "Add"}
        </button>
      </form>

      {error && <p className="text-sm text-bad">{error}</p>}
      {!rows ? (
        <p className="kicker">Loading…</p>
      ) : rows.length === 0 ? (
        <p className="text-sm text-muted">The blocklist is empty.</p>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-hair">
          <table className="w-full min-w-[44rem] text-left font-ui text-xs">
            <thead className="kicker bg-panel">
              <tr>
                <th className="px-3 py-2">Company</th>
                <th className="px-3 py-2">Status</th>
                <th className="px-3 py-2">Cooling until</th>
                <th className="px-3 py-2">Reason</th>
                <th className="px-3 py-2">Added</th>
                <th className="px-3 py-2" />
              </tr>
            </thead>
            <tbody className="divide-y divide-hair">
              {rows.map((r) => (
                <tr key={r.id}>
                  <td className="px-3 py-2 font-medium text-ink">
                    {r.company}
                    <span className="block text-[0.65rem] text-muted">{r.company_norm}</span>
                  </td>
                  <td className="px-3 py-2">
                    <span className={r.status === "active" ? "pill pill-bad" : r.status === "cooling" ? "pill pill-warn" : "pill pill-muted"}>{r.status.replace(/_/g, " ")}</span>
                  </td>
                  <td className="px-3 py-2">{r.cooling_until ? fmtDate(r.cooling_until) : "—"}</td>
                  <td className="px-3 py-2 text-ink/80">
                    {r.reason || "—"}
                    {r.notes && <span className="block text-muted">{r.notes}</span>}
                  </td>
                  <td className="px-3 py-2 text-muted">
                    {fmtDate(r.added_at)}
                    {r.added_by && <span className="block">{r.added_by}</span>}
                  </td>
                  <td className="px-3 py-2 text-right">
                    <button type="button" className="btn btn-danger px-3 py-1" onClick={() => remove(r)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
