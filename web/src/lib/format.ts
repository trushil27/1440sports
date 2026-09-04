import type { ClaimStatus, Tier, VerificationBadge } from "./types";

const LONDON = "Europe/London";

export function fmtDate(iso: string | null | undefined, opts?: Intl.DateTimeFormatOptions) {
  if (!iso) return "";
  const d = iso.length === 10 ? new Date(`${iso}T12:00:00Z`) : new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString("en-GB", {
    day: "numeric",
    month: "long",
    year: "numeric",
    timeZone: LONDON,
    ...opts,
  });
}

export function fmtDateShort(iso: string | null | undefined) {
  return fmtDate(iso, { day: "numeric", month: "short", year: undefined });
}

export function fmtDateTime(iso: string | null | undefined) {
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    timeZone: LONDON,
  });
}

export function monthKey(iso: string): string {
  return iso.slice(0, 7);
}

export function monthLabel(key: string): string {
  const [y, m] = key.split("-").map(Number);
  return new Date(Date.UTC(y, m - 1, 15)).toLocaleDateString("en-GB", {
    month: "long",
    year: "numeric",
    timeZone: "UTC",
  });
}

export function todayLondon(): string {
  return new Date().toLocaleDateString("en-GB", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
    timeZone: LONDON,
  });
}

export function tierClass(tier: Tier | string | null | undefined): string {
  switch ((tier ?? "").toUpperCase()) {
    case "HOT TOP TIER":
      return "pill pill-navy";
    case "HOT":
      return "pill pill-ok";
    case "WARM":
      return "pill pill-warn";
    case "VERIFY":
      return "pill pill-muted";
    default:
      return "pill pill-muted";
  }
}

export function badgeClass(badge: VerificationBadge | string | null | undefined): string {
  switch (badge) {
    case "Verified":
      return "pill pill-ok";
    case "Review":
      return "pill pill-warn";
    case "Blocked":
      return "pill pill-bad";
    default:
      return "pill pill-muted";
  }
}

export function claimClass(status: ClaimStatus | string): string {
  switch (status) {
    case "verified":
      return "pill pill-ok";
    case "contradicted":
      return "pill pill-bad";
    default:
      return "pill pill-warn";
  }
}

export function claimLabel(status: ClaimStatus | string): string {
  switch (status) {
    case "verified":
      return "Verified";
    case "contradicted":
      return "Contradicted";
    default:
      return "Unverified";
  }
}

export function auditLabel(status: string): string {
  switch (status) {
    case "pass":
      return "Passed";
    case "pass_after_retry":
      return "Passed after retry";
    case "failed":
      return "Failed";
    default:
      return "Pending";
  }
}

export function auditClass(status: string): string {
  switch (status) {
    case "pass":
    case "pass_after_retry":
      return "pill pill-ok";
    case "failed":
      return "pill pill-bad";
    default:
      return "pill pill-muted";
  }
}

/** Strip the writer's inline `<font>` markup for plain-text contexts. */
export function plain(text: string | null | undefined): string {
  return (text ?? "").replace(/<[^>]+>/g, "").replace(/&nbsp;/g, " ").trim();
}

export function hostname(url: string | null | undefined): string {
  if (!url) return "";
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
}

export function decisionLabel(decision: string): string {
  return decision.replace(/_/g, " ");
}
