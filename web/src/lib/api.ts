/**
 * Typed fetch wrapper for the 1440 Intelligence API.
 *
 * In the browser every call is same-origin (`/api/...`, `/auth/...`) and reaches the API
 * through the rewrites in next.config.ts, so the httpOnly session cookie is first-party.
 * `NEXT_PUBLIC_API_BASE_URL` (default http://localhost:8000) is the rewrite target and
 * the absolute base used anywhere a relative URL cannot work (server side).
 */
import type {
  AlumniRow,
  BlocklistRow,
  BriefActionKind,
  BriefCard,
  BriefDetail,
  BriefList,
  BriefListFilters,
  CandidateReason,
  Highlight,
  Me,
  OpsConfig,
  OpsRun,
  OutreachDraft,
  PeopleCard,
  ProviderUsage,
  SponsorRow,
  TodayResponse,
} from "./types";

export const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"
).replace(/\/+$/, "");

export function apiUrl(path: string): string {
  if (typeof window === "undefined") return `${API_BASE_URL}${path}`;
  return path;
}

export class ApiError extends Error {
  status: number;
  detail: string;
  constructor(status: number, detail: string) {
    super(detail);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

const PUBLIC_PATHS = ["/signin", "/enrol"];

function onUnauthorised() {
  if (typeof window === "undefined") return;
  const here = window.location.pathname;
  if (PUBLIC_PATHS.some((p) => here.startsWith(p))) return;
  const next = encodeURIComponent(here + window.location.search);
  window.location.assign(`/signin?next=${next}`);
}

async function readDetail(res: Response): Promise<string> {
  const text = await res.text();
  if (!text) return res.statusText || `HTTP ${res.status}`;
  try {
    const j = JSON.parse(text);
    if (typeof j?.detail === "string") return j.detail;
    if (Array.isArray(j?.detail)) {
      return j.detail.map((d: { msg?: string }) => d.msg ?? JSON.stringify(d)).join("; ");
    }
    return text;
  } catch {
    return text;
  }
}

export async function api<T>(
  path: string,
  init: RequestInit & { json?: unknown; redirectOn401?: boolean } = {},
): Promise<T> {
  const { json, redirectOn401 = true, headers, ...rest } = init;
  const res = await fetch(apiUrl(path), {
    credentials: "include",
    ...rest,
    headers: {
      Accept: "application/json",
      ...(json !== undefined ? { "Content-Type": "application/json" } : {}),
      ...(headers ?? {}),
    },
    body: json !== undefined ? JSON.stringify(json) : rest.body,
  });
  if (res.status === 401) {
    if (redirectOn401) onUnauthorised();
    throw new ApiError(401, "sign in required");
  }
  if (!res.ok) throw new ApiError(res.status, await readDetail(res));
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

function qs(params: Record<string, string | number | boolean | undefined | null>): string {
  const u = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v === undefined || v === null || v === "") continue;
    u.set(k, String(v));
  }
  const s = u.toString();
  return s ? `?${s}` : "";
}

// ---- auth --------------------------------------------------------------------------

export const auth = {
  me: () => api<Me>("/auth/me", { redirectOn401: false }),
  logout: () => api<void>("/auth/logout", { method: "POST", redirectOn401: false }),
  magicLink: (email: string) =>
    api<void>("/auth/magic-link", { method: "POST", json: { email }, redirectOn401: false }),
  verifyMagicLink: (token: string) =>
    api<{ email: string; role: string; has_passkey: boolean; next: "/enrol" | "/" }>(
      `/auth/magic-link/verify?token=${encodeURIComponent(token)}`,
      { redirectOn401: false },
    ),
  passkeyLoginOptions: (email?: string) =>
    api<Record<string, unknown>>("/auth/passkey/login/options", {
      method: "POST",
      json: { email: email || null },
      redirectOn401: false,
    }),
  passkeyLoginVerify: (credential: unknown) =>
    api<{ email: string; role: string }>("/auth/passkey/login/verify", {
      method: "POST",
      json: { credential },
      redirectOn401: false,
    }),
  passkeyRegisterOptions: () =>
    api<Record<string, unknown>>("/auth/passkey/register/options", { method: "POST" }),
  passkeyRegisterVerify: (credential: unknown, device_name: string | null) =>
    api<{ ok: boolean }>("/auth/passkey/register/verify", {
      method: "POST",
      json: { credential, device_name },
    }),
};

// ---- briefs ------------------------------------------------------------------------

export const briefs = {
  today: () => api<TodayResponse>("/api/today"),
  list: (filters: BriefListFilters = {}, cursor?: string | null, limit = 30) =>
    api<BriefList>(
      `/api/briefs${qs({
        q: filters.q,
        series: filters.series,
        tier: filters.tier,
        track: filters.track,
        status: filters.status,
        from: filters.from,
        to: filters.to,
        include_blocked: filters.include_blocked ? true : undefined,
        cursor: cursor ?? undefined,
        limit,
      })}`,
    ),
  get: (number: number) => api<BriefDetail>(`/api/briefs/${number}`),
  pdfUrl: (number: number) => `/api/briefs/${number}/pdf`,
  highlights: (number: number) => api<Highlight[]>(`/api/briefs/${number}/highlights`),
  action: (number: number, action: BriefActionKind, note?: string) =>
    api<{ actions: BriefDetail["actions"] }>(`/api/briefs/${number}/actions`, {
      method: "POST",
      json: { action, note: note ?? null },
    }),
  people: (number: number) => api<PeopleCard>(`/api/briefs/${number}/people`),
  reverify: (number: number) =>
    api<PeopleCard>(`/api/briefs/${number}/people/reverify`, { method: "POST" }),
  lookupContact: (number: number) =>
    api<PeopleCard>(`/api/briefs/${number}/people/lookup`, { method: "POST" }),
  drafts: (number: number) => api<OutreachDraft[]>(`/api/briefs/${number}/outreach`),
  draft: (number: number) =>
    api<OutreachDraft>(`/api/briefs/${number}/outreach`, { method: "POST" }),
};

export const outreach = {
  outlookDraft: (draftId: number) =>
    api<OutreachDraft>(`/api/outreach/${draftId}/outlook-draft`, { method: "POST" }),
  contacted: (draftId: number) =>
    api<{ ok: boolean }>(`/api/outreach/${draftId}/contacted`, { method: "POST" }),
};

// ---- ops ---------------------------------------------------------------------------

export const ops = {
  runs: (limit = 30) => api<OpsRun[]>(`/api/ops/runs${qs({ limit })}`),
  candidates: (runId: number) => api<CandidateReason[]>(`/api/ops/runs/${runId}/candidates`),
  queue: () => api<BriefCard[]>("/api/ops/queue"),
  blocklist: () => api<BlocklistRow[]>("/api/ops/blocklist"),
  addBlocklist: (body: {
    company: string;
    status: string;
    reason?: string | null;
    cooling_until?: string | null;
    notes?: string | null;
  }) => api<BlocklistRow>("/api/ops/blocklist", { method: "POST", json: body }),
  deleteBlocklist: (id: number) => api<void>(`/api/ops/blocklist/${id}`, { method: "DELETE" }),
  alumni: () => api<AlumniRow[]>("/api/ops/alumni"),
  updateAlumni: (id: number, body: Partial<AlumniRow>) =>
    api<AlumniRow>(`/api/ops/alumni/${id}`, { method: "PUT", json: body }),
  sponsors: (params: { series?: string; team?: string; q?: string } = {}) =>
    api<SponsorRow[]>(`/api/ops/sponsors${qs(params)}`),
  updateSponsor: (id: number, body: Omit<SponsorRow, "id" | "verified_at">) =>
    api<SponsorRow>(`/api/ops/sponsors/${id}`, { method: "PUT", json: body }),
  providerUsage: () => api<ProviderUsage>("/api/ops/provider-usage"),
  config: () => api<OpsConfig>("/api/ops/config"),
};
