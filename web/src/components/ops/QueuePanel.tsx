"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ApiError, ops } from "@/lib/api";
import { auditClass, auditLabel, fmtDateShort } from "@/lib/format";
import type { BriefCard } from "@/lib/types";
import { VerificationBadge } from "../Badges";

export function QueuePanel() {
  const [rows, setRows] = useState<BriefCard[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    ops
      .queue()
      .then(setRows)
      .catch((err) => setError(err instanceof ApiError ? err.detail : "Could not load the queue."));
  }, []);

  if (error) return <p className="text-sm text-bad">{error}</p>;
  if (!rows) return <p className="kicker">Loading…</p>;
  if (rows.length === 0) return <p className="text-sm text-muted">Nothing blocked or awaiting review.</p>;

  return (
    <ul className="divide-y divide-hair rounded-xl border border-hair">
      {rows.map((b) => (
        <li key={b.number}>
          <Link href={`/brief/${b.number}`} className="flex flex-wrap items-center gap-x-3 gap-y-1 px-4 py-3 hover:bg-panel">
            <span className="w-14 font-ui text-xs text-muted">{fmtDateShort(b.date)}</span>
            <span className="font-medium text-ink">{b.company}</span>
            <span className="kicker">{b.label}</span>
            <VerificationBadge badge={b.badge} />
            <span className={auditClass(b.audit)}>{auditLabel(b.audit)}</span>
            <span className="ml-auto font-ui font-bold text-navy dark:text-gold">{b.score ?? "—"}</span>
          </Link>
        </li>
      ))}
    </ul>
  );
}
