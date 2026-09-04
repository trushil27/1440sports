"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ApiError, briefs } from "@/lib/api";
import { fmtDate, plain } from "@/lib/format";
import type { TodayResponse } from "@/lib/types";
import { Tag, TierBadge, VerificationBadge } from "./Badges";
import { useToast } from "./Toast";

export function TodayView() {
  const [data, setData] = useState<TodayResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const toast = useToast();
  const router = useRouter();

  useEffect(() => {
    briefs
      .today()
      .then(setData)
      .catch((err) => setError(err instanceof ApiError ? err.detail : "Could not reach the API."));
  }, []);

  if (error) {
    return (
      <Empty title="Nothing to show" body={error} />
    );
  }
  if (!data) {
    return <div className="px-5 py-16 text-center kicker">Loading today’s signal…</div>;
  }
  const b = data.brief;
  if (!b) {
    return (
      <Empty
        title={data.message || "No verified signal yet."}
        body={
          data.last_run
            ? `Last run: ${fmtDate(data.last_run.date)} · ${data.last_run.status.replace(/_/g, " ")}.`
            : "The pipeline has not recorded a run yet."
        }
      />
    );
  }

  const pursue = async () => {
    setBusy("pursuing");
    try {
      await briefs.action(b.number, "pursuing");
      toast(`${b.company} marked as pursuing. It will not be re-pitched cold.`, "ok");
    } catch (err) {
      toast(err instanceof ApiError ? err.detail : "Could not record the action.", "error");
    } finally {
      setBusy(null);
    }
  };

  return (
    <div className="mx-auto max-w-3xl px-4 py-6 sm:px-6 sm:py-10">
      <div className="mb-4 flex flex-wrap items-center gap-x-3 gap-y-1">
        <span className="eyebrow">{data.is_today ? "Today" : "Latest signal"}</span>
        <span className="kicker">{fmtDate(b.date)}</span>
        <span className="kicker">{b.label}</span>
      </div>

      <article className="card overflow-hidden">
        <div className="h-1 w-full bg-gold" />
        <div className="p-5 sm:p-8">
          <div className="flex flex-wrap items-center gap-2">
            <TierBadge tier={b.tier} />
            <VerificationBadge badge={b.badge} />
            {b.track === 2 && <Tag tone="navy">Alumni Intelligence</Tag>}
            {b.historical && <Tag>Historical</Tag>}
          </div>

          <div className="mt-4 flex items-end justify-between gap-4">
            <div className="min-w-0">
              <h1 className="font-display text-4xl font-normal leading-[1.05] tracking-tight text-navy dark:text-ink sm:text-5xl">
                {b.company}
              </h1>
              {b.industry && <p className="mt-1.5 text-sm italic text-muted">{b.industry}</p>}
            </div>
            <div className="scorebox shrink-0 !min-w-[5.6rem] !px-3.5 !py-2.5">
              <div className="font-display text-4xl font-bold leading-none">{b.score ?? "—"}</div>
              <div className="mt-1 font-ui text-[0.55rem] uppercase tracking-[0.18em] text-gold">/ 100</div>
            </div>
          </div>

          <div className="mt-5 grid grid-cols-1 gap-2 sm:grid-cols-2">
            <div className="chip">
              <div className="chip-k">Series · Team</div>
              <div className="chip-v">
                {b.series || "—"}
                {b.team ? ` · ${b.team}` : ""}
              </div>
            </div>
            <div className="chip">
              <div className="chip-k">Decision-maker</div>
              <div className="chip-v">
                {b.person || "Not named"}
                {b.role && <span className="block font-normal text-muted">{b.role}</span>}
              </div>
            </div>
          </div>

          {b.take && (
            <p className="mt-6 font-display text-lg leading-relaxed text-ink">{plain(b.take)}</p>
          )}

          {data.highlights && data.highlights.length > 0 && (
            <section className="mt-6 border-t border-hair pt-5">
              <h2 className="h-rule border-b-0 !mb-2 !pb-0">Recent &amp; insightful</h2>
              <ul className="space-y-2">
                {data.highlights.map((h, i) => (
                  <li key={i} className="flex gap-3 text-[0.97rem] leading-relaxed">
                    <span className="mt-[0.62em] h-1.5 w-1.5 shrink-0 rounded-full bg-gold" aria-hidden />
                    <span>{h.text}</span>
                  </li>
                ))}
              </ul>
              <p className="kicker mt-3">Built from verified claims only</p>
            </section>
          )}

          <div className="mt-7 flex flex-wrap gap-2">
            <Link href={`/brief/${b.number}`} className="btn btn-primary">
              Open brief
            </Link>
            <button type="button" className="btn" onClick={() => router.push(`/brief/${b.number}#outreach`)}>
              Draft outreach
            </button>
            <button type="button" className="btn btn-gold" disabled={busy === "pursuing"} onClick={pursue}>
              {busy === "pursuing" ? "Saving…" : "Pursuing"}
            </button>
          </div>
        </div>
      </article>

      {data.run && (
        <p className="kicker mt-5 text-center">
          Run {fmtDate(data.run.date)} · {data.run.status.replace(/_/g, " ")}
          {data.run.others_not_chosen > 0 && ` · ${data.run.others_not_chosen} other candidates not chosen`}
        </p>
      )}
    </div>
  );
}

function Empty({ title, body }: { title: string; body: string }) {
  return (
    <div className="mx-auto max-w-xl px-6 py-20 text-center">
      <p className="eyebrow mb-3">Today</p>
      <h1 className="font-display text-3xl text-navy dark:text-ink">{title}</h1>
      <p className="mt-3 text-muted">{body}</p>
    </div>
  );
}
