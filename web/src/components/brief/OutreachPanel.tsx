"use client";

import { useEffect, useState } from "react";
import { ApiError, briefs, outreach } from "@/lib/api";
import { fmtDateTime } from "@/lib/format";
import type { OutreachDraft } from "@/lib/types";
import { useToast } from "../Toast";

export function OutreachPanel({
  number,
  enabled,
  disabledReason,
  onContacted,
}: {
  number: number;
  enabled: boolean;
  disabledReason: string | null;
  onContacted?: () => void;
}) {
  const toast = useToast();
  const [drafts, setDrafts] = useState<OutreachDraft[]>([]);
  const [current, setCurrent] = useState<OutreachDraft | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [inline, setInline] = useState<string | null>(null);

  useEffect(() => {
    briefs
      .drafts(number)
      .then((rows) => {
        setDrafts(rows);
        setCurrent(rows[0] ?? null);
      })
      .catch(() => {});
  }, [number]);

  const draft = async () => {
    setBusy("draft");
    setInline(null);
    try {
      const d = await briefs.draft(number);
      setDrafts((xs) => [d, ...xs]);
      setCurrent(d);
    } catch (err) {
      setInline(err instanceof ApiError ? err.detail : "Could not draft the email.");
    } finally {
      setBusy(null);
    }
  };

  const copy = async () => {
    if (!current) return;
    try {
      await navigator.clipboard.writeText(`Subject: ${current.subject}\n\n${current.body}`);
      toast("Copied.", "ok");
    } catch {
      toast("Copy is not available in this browser.", "error");
    }
  };

  const outlook = async () => {
    if (!current) return;
    setBusy("outlook");
    setInline(null);
    try {
      const d = await outreach.outlookDraft(current.id);
      setCurrent(d);
      setDrafts((xs) => xs.map((x) => (x.id === d.id ? d : x)));
      toast("Draft is in your Outlook drafts — nothing was sent.", "ok");
    } catch (err) {
      setInline(err instanceof ApiError ? err.detail : "Could not create the Outlook draft.");
    } finally {
      setBusy(null);
    }
  };

  const contacted = async () => {
    if (!current) return;
    setBusy("contacted");
    setInline(null);
    try {
      await outreach.contacted(current.id);
      toast("Marked contacted.", "ok");
      onContacted?.();
    } catch (err) {
      setInline(err instanceof ApiError ? err.detail : "Could not record the action.");
    } finally {
      setBusy(null);
    }
  };

  return (
    <section id="outreach" className="scroll-mt-20">
      <h2 className="h-rule">Outreach</h2>
      {!enabled && (
        <div className="mb-3 rounded-lg border border-warn-line bg-warn-bg p-3 font-ui text-sm text-warn">
          {disabledReason || "Outreach is disabled until the decision-maker's role is verified."}
        </div>
      )}
      <div className="flex flex-wrap gap-2">
        <button type="button" className="btn btn-primary" disabled={!enabled || busy !== null} onClick={draft}>
          {busy === "draft" ? "Drafting…" : current ? "Draft again" : "Draft outreach"}
        </button>
        {drafts.length > 1 && (
          <select
            className="field w-auto"
            value={current?.id ?? ""}
            onChange={(e) => setCurrent(drafts.find((d) => d.id === Number(e.target.value)) ?? null)}
            aria-label="Previous drafts"
          >
            {drafts.map((d) => (
              <option key={d.id} value={d.id}>
                Draft {d.id} · {fmtDateTime(d.created_at)}
              </option>
            ))}
          </select>
        )}
      </div>
      {inline && <p className="mt-3 rounded-lg border border-bad-line bg-bad-bg p-3 font-ui text-sm text-bad">{inline}</p>}

      {current ? (
        <div className="card mt-4 p-5">
          <div className="chip-k">Subject</div>
          <p className="mt-0.5 font-ui font-medium text-ink">{current.subject}</p>
          <div className="chip-k mt-4">Body</div>
          <pre className="mt-1 whitespace-pre-wrap font-display text-[0.97rem] leading-relaxed text-ink">{current.body}</pre>
          <p className="kicker mt-3">
            Drafted {fmtDateTime(current.created_at)} · built from verified claims only
            {current.outlook_draft_id && " · in Outlook drafts"}
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            <button type="button" className="btn" onClick={copy}>
              Copy
            </button>
            <button type="button" className="btn" disabled={busy !== null} onClick={outlook}>
              {busy === "outlook" ? "Creating…" : "Create Outlook draft"}
            </button>
            <button type="button" className="btn" disabled={busy !== null} onClick={contacted}>
              Mark contacted
            </button>
          </div>
        </div>
      ) : (
        enabled && <p className="mt-3 text-sm text-muted">No draft yet. It is written in brand voice from the opening angle and verified claims, ending with the 25-minute ask.</p>
      )}
    </section>
  );
}
