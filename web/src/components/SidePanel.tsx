"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { forwardRef, useCallback, useEffect, useImperativeHandle, useMemo, useRef, useState } from "react";
import { ApiError, briefs } from "@/lib/api";
import { fmtDateShort, monthKey, monthLabel } from "@/lib/format";
import type { BriefCard, BriefListFilters } from "@/lib/types";
import { VerificationBadge } from "./Badges";

export interface SidePanelHandle {
  focusSearch: () => void;
}

interface Props {
  open: boolean;
  onClose: () => void;
}

const EMPTY: BriefListFilters = {};

export const SidePanel = forwardRef<SidePanelHandle, Props>(function SidePanel({ open, onClose }, ref) {
  const pathname = usePathname();
  const activeNumber = useMemo(() => {
    const m = pathname.match(/^\/brief\/(\d+)/);
    return m ? Number(m[1]) : null;
  }, [pathname]);

  const [q, setQ] = useState("");
  const [filters, setFilters] = useState<BriefListFilters>(EMPTY);
  const [showFilters, setShowFilters] = useState(false);
  const [items, setItems] = useState<BriefCard[]>([]);
  const [cursor, setCursor] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const searchRef = useRef<HTMLInputElement>(null);
  const sentinelRef = useRef<HTMLDivElement>(null);
  const reqSeq = useRef(0);

  useImperativeHandle(ref, () => ({
    focusSearch: () => searchRef.current?.focus(),
  }));

  const effective = useMemo<BriefListFilters>(() => ({ ...filters, q: q.trim() || undefined }), [filters, q]);

  const load = useCallback(
    async (reset: boolean) => {
      const seq = ++reqSeq.current;
      setLoading(true);
      setError(null);
      try {
        const page = await briefs.list(effective, reset ? null : cursor);
        if (seq !== reqSeq.current) return;
        setItems((xs) => (reset ? page.items : [...xs, ...page.items]));
        setCursor(page.next_cursor);
      } catch (err) {
        if (seq !== reqSeq.current) return;
        setError(err instanceof ApiError ? err.detail : "Could not load the history.");
      } finally {
        if (seq === reqSeq.current) setLoading(false);
      }
    },
    [effective, cursor],
  );

  // Debounced reload when the query or filters change.
  useEffect(() => {
    const t = window.setTimeout(() => void load(true), 250);
    return () => window.clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [effective]);

  // Infinite scroll.
  useEffect(() => {
    const el = sentinelRef.current;
    if (!el || !cursor) return;
    const io = new IntersectionObserver((entries) => {
      if (entries.some((e) => e.isIntersecting) && !loading) void load(false);
    });
    io.observe(el);
    return () => io.disconnect();
  }, [cursor, loading, load]);

  const groups = useMemo(() => {
    const map = new Map<string, BriefCard[]>();
    for (const b of items) {
      const k = monthKey(b.date);
      if (!map.has(k)) map.set(k, []);
      map.get(k)!.push(b);
    }
    return [...map.entries()];
  }, [items]);

  const set = (patch: Partial<BriefListFilters>) => setFilters((f) => ({ ...f, ...patch }));
  const activeFilterCount = Object.values(filters).filter((v) => v !== undefined && v !== "").length;

  return (
    <>
      {open && <div className="fixed inset-0 z-40 bg-navy/50 md:hidden" onClick={onClose} aria-hidden />}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-[86vw] max-w-sm flex-col border-r border-hair bg-paper transition-transform duration-200 md:static md:z-auto md:w-80 md:translate-x-0 md:transition-none lg:w-[22rem] ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
        aria-label="History"
      >
        <div className="border-b border-hair p-3 md:sticky md:top-14">
          <div className="flex items-center gap-2">
            <div className="relative flex-1">
              <input
                ref={searchRef}
                type="search"
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder="Company, person, team…"
                className="field pl-9"
                aria-label="Search briefs"
              />
              <svg className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
                <circle cx="11" cy="11" r="7" />
                <path d="M20 20l-3.5-3.5" />
              </svg>
            </div>
            <button
              type="button"
              onClick={() => setShowFilters((v) => !v)}
              className={`btn px-3 ${showFilters || activeFilterCount ? "border-gold" : ""}`}
              aria-expanded={showFilters}
              aria-label="Filters"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
                <path d="M4 6h16M7 12h10M10 18h4" />
              </svg>
              {activeFilterCount > 0 && <span className="text-xs">{activeFilterCount}</span>}
            </button>
            <button type="button" onClick={onClose} className="btn px-3 md:hidden" aria-label="Close history">
              ✕
            </button>
          </div>

          {showFilters && (
            <div className="mt-3 grid grid-cols-2 gap-2 font-ui text-xs">
              <label className="col-span-1">
                <span className="kicker block mb-1">From</span>
                <input type="date" className="field" value={filters.from ?? ""} onChange={(e) => set({ from: e.target.value || undefined })} />
              </label>
              <label className="col-span-1">
                <span className="kicker block mb-1">To</span>
                <input type="date" className="field" value={filters.to ?? ""} onChange={(e) => set({ to: e.target.value || undefined })} />
              </label>
              <label>
                <span className="kicker block mb-1">Tier</span>
                <select className="field" value={filters.tier ?? ""} onChange={(e) => set({ tier: e.target.value || undefined })}>
                  <option value="">Any</option>
                  <option>HOT TOP TIER</option>
                  <option>HOT</option>
                  <option>WARM</option>
                  <option>VERIFY</option>
                </select>
              </label>
              <label>
                <span className="kicker block mb-1">Series</span>
                <select className="field" value={filters.series ?? ""} onChange={(e) => set({ series: e.target.value || undefined })}>
                  <option value="">Any</option>
                  <option value="F1">Formula 1</option>
                  <option value="FE">Formula E</option>
                </select>
              </label>
              <label>
                <span className="kicker block mb-1">Track</span>
                <select
                  className="field"
                  value={filters.track ?? ""}
                  onChange={(e) => set({ track: e.target.value ? (Number(e.target.value) as 1 | 2) : undefined })}
                >
                  <option value="">Any</option>
                  <option value="1">Track 1 · Signals</option>
                  <option value="2">Track 2 · Alumni</option>
                </select>
              </label>
              <label>
                <span className="kicker block mb-1">Verification</span>
                <select
                  className="field"
                  value={filters.status ?? (filters.include_blocked ? "blocked" : "")}
                  onChange={(e) => {
                    const v = e.target.value;
                    if (v === "blocked") set({ status: "blocked", include_blocked: true });
                    else set({ status: (v || undefined) as BriefListFilters["status"], include_blocked: undefined });
                  }}
                >
                  <option value="">Any</option>
                  <option value="verified">Verified</option>
                  <option value="needs_review">Review</option>
                  <option value="blocked">Blocked</option>
                </select>
              </label>
              {activeFilterCount > 0 && (
                <button type="button" className="btn col-span-2" onClick={() => setFilters(EMPTY)}>
                  Clear filters
                </button>
              )}
            </div>
          )}
        </div>

        <div className="flex-1 overflow-y-auto overscroll-contain">
          {groups.map(([key, rows]) => (
            <section key={key}>
              <h3 className="kicker sticky top-0 z-10 bg-paper/95 px-4 pb-1 pt-4 backdrop-blur">{monthLabel(key)}</h3>
              <ul>
                {rows.map((b) => {
                  const active = b.number === activeNumber;
                  return (
                    <li key={`${b.number}-${b.date}`}>
                      <Link
                        href={`/brief/${b.number}`}
                        onClick={onClose}
                        className={`flex items-center gap-3 border-l-2 px-4 py-2.5 transition-colors hover:bg-panel ${
                          active ? "border-gold bg-panel" : "border-transparent"
                        }`}
                      >
                        <div className="w-12 shrink-0 font-ui text-[0.68rem] uppercase tracking-wider text-muted">
                          {fmtDateShort(b.date)}
                        </div>
                        <div className="min-w-0 flex-1">
                          <div className="truncate text-[0.95rem] leading-tight text-ink">{b.company}</div>
                          <div className="mt-0.5 flex items-center gap-1.5">
                            <VerificationBadge badge={b.badge} />
                            {b.track === 2 && <span className="pill pill-navy">Alumni</span>}
                            {b.historical && <span className="pill pill-muted">Historical</span>}
                          </div>
                        </div>
                        <div className="shrink-0 font-ui text-base font-bold text-navy dark:text-gold">
                          {b.score ?? "—"}
                        </div>
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </section>
          ))}

          {!loading && !error && items.length === 0 && (
            <p className="px-4 py-8 text-center text-sm text-muted">
              {q || activeFilterCount ? "No briefs match this search." : "No briefs stored yet."}
            </p>
          )}
          {error && <p className="px-4 py-6 text-center text-sm text-bad">{error}</p>}
          {loading && <p className="kicker px-4 py-4 text-center">Loading…</p>}
          <div ref={sentinelRef} className="h-6" />
        </div>
      </aside>
    </>
  );
});
