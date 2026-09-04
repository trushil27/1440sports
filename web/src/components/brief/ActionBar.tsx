"use client";

import { useState } from "react";
import { ApiError, briefs } from "@/lib/api";
import { fmtDateTime } from "@/lib/format";
import type { ActionRow, BriefActionKind } from "@/lib/types";
import { useToast } from "../Toast";

const LABEL: Record<BriefActionKind, string> = {
  pursuing: "Pursuing",
  snoozed: "Snoozed 30 days",
  killed: "Killed",
  contacted: "Contacted",
};

export function ActionBar({
  number,
  company,
  actions,
  onChange,
}: {
  number: number;
  company: string;
  actions: ActionRow[];
  onChange: (rows: ActionRow[]) => void;
}) {
  const toast = useToast();
  const [busy, setBusy] = useState<BriefActionKind | null>(null);

  const run = async (action: BriefActionKind) => {
    if (action === "killed" && !window.confirm(`Kill ${company}? It goes on the cooling list until an operator lifts it.`)) return;
    setBusy(action);
    try {
      const r = await briefs.action(number, action);
      onChange(r.actions);
      toast(
        action === "pursuing"
          ? `${company} marked as pursuing.`
          : action === "snoozed"
            ? `${company} snoozed for 30 days.`
            : action === "killed"
              ? `${company} killed.`
              : `${company} marked contacted.`,
        "ok",
      );
    } catch (err) {
      toast(err instanceof ApiError ? err.detail : "Could not record the action.", "error");
    } finally {
      setBusy(null);
    }
  };

  return (
    <section id="actions" className="scroll-mt-20">
      <h2 className="h-rule">Actions</h2>
      <div className="flex flex-wrap gap-2">
        <button type="button" className="btn btn-gold" disabled={busy !== null} onClick={() => run("pursuing")}>
          Pursuing
        </button>
        <button type="button" className="btn" disabled={busy !== null} onClick={() => run("snoozed")}>
          Snooze 30d
        </button>
        <button type="button" className="btn btn-danger" disabled={busy !== null} onClick={() => run("killed")}>
          Kill
        </button>
        <button type="button" className="btn" disabled={busy !== null} onClick={() => run("contacted")}>
          Mark contacted
        </button>
      </div>
      <p className="kicker mt-2">Snooze and Kill write to the cooling list, so the pipeline respects them.</p>
      {actions.length > 0 && (
        <ol className="mt-3 divide-y divide-hair rounded-xl border border-hair font-ui text-sm">
          {[...actions].reverse().map((a) => (
            <li key={a.id} className="flex flex-wrap items-baseline gap-x-3 gap-y-0.5 px-3 py-2">
              <span className="font-medium text-ink">{LABEL[a.action] ?? a.action}</span>
              <span className="text-muted">{a.by}</span>
              <span className="ml-auto text-xs text-muted">{fmtDateTime(a.at)}</span>
              {a.note && <span className="basis-full text-xs text-muted">{a.note}</span>}
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}
