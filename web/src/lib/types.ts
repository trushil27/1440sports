/** JSON shapes, mirrored from api/intel_api/serializers.py and the route modules. */

export type VerificationStatus = "pending" | "verified" | "needs_review" | "blocked";
export type VerificationBadge = "Verified" | "Review" | "Blocked" | "Pending";
export type ClaimStatus = "verified" | "unverified" | "contradicted";
export type AuditStatus = "pending" | "pass" | "pass_after_retry" | "failed";
export type Tier = "HOT TOP TIER" | "HOT" | "WARM" | "VERIFY" | "PLANT" | "DISCARD";
export type BriefActionKind = "pursuing" | "snoozed" | "killed" | "contacted";

export interface BriefCard {
  number: number;
  label: string;
  date: string; // ISO date
  company: string;
  score: number | null;
  tier: Tier | string | null;
  series: string | null;
  team: string | null;
  person: string | null;
  role: string | null;
  take: string | null;
  verification: VerificationStatus;
  badge: VerificationBadge;
  audit: AuditStatus;
  track: 1 | 2;
  track_label: "Alumni Intelligence" | "";
  historical: boolean;
  has_pdf: boolean;
  md_eligible: boolean;
  industry: string | null;
}

export interface ClaimRow {
  id: number;
  text: string;
  section: string;
  type: string;
  load_bearing: boolean;
  cited_source_url: string | null;
  status: ClaimStatus;
  method: string | null;
  evidence_url: string | null;
  excerpt: string | null;
  notes: string | null;
  checked_at: string | null;
  model: string | null;
}

export interface VerificationPanelData {
  status: VerificationStatus;
  badge: VerificationBadge;
  summary: string;
  load_bearing_total: number;
  load_bearing_verified: number;
  claims: ClaimRow[];
}

export interface ScoreCell {
  label: string;
  num: number;
  denom: string;
  note: string;
}

export interface ActionRow {
  id: number;
  action: BriefActionKind;
  by: string;
  at: string;
  note: string | null;
}

export interface ProofPoint {
  value: string;
  fact: string;
  source_url: string | null;
  verified: boolean;
  claim_id: number | null;
}

export interface GridRow {
  team: string;
  recommended: boolean;
  status: "prime" | "open" | "crowded" | "conflict";
  label: string;
  detail: string;
}

export interface Risk {
  label: string;
  detail: string;
  counter: string;
}

/** The writer + pipeline fields the renderer uses (pipeline/intel/brief_data.py). */
export interface BriefData {
  brief_number?: string;
  track_label?: string;
  company?: string;
  industry_meta?: string;
  hq?: string | null;
  ticker?: string | null;
  deck?: string;
  score?: number;
  timing_label?: string;
  series_label?: string;
  team_label?: string;
  horizon_label?: string;
  hot_top_tier?: boolean;
  confidence_level?: string;
  the_case_p1?: string;
  the_case_p2?: string;
  why_now_callout?: string;
  why_team_label?: string;
  why_team_para?: string;
  value_section?: boolean;
  value_section_label?: string;
  value_mode?: "A" | "B" | "C" | null;
  value_content?: string;
  deal_arch_para?: string;
  decision_maker_name?: string;
  decision_maker_role?: string;
  decision_maker_bio?: string;
  opening_angle_intro?: string;
  opening_angle_quote?: string;
  score_cells?: ScoreCell[];
  risks?: Risk[];
  bottom_line?: string;
  signals?: string[];
  proof_points?: ProofPoint[];
  all_proof_points_verified?: boolean;
  gridfit?: GridRow[];
  gridfit_note?: string;
  sources?: string[];
  decision_maker_verified?: boolean;
  historical_label?: string;
  [key: string]: unknown;
}

export interface BriefDetail extends BriefCard {
  brief_data: BriefData | null;
  mode: string | null;
  page_count: number | null;
  pdf_url: string | null;
  page_url: string | null;
  verification_panel: VerificationPanelData;
  score_composition: {
    cells: ScoreCell[];
    breakdown: Record<string, unknown> | null;
    gate_results: Record<string, unknown> | null;
    alumni_boost: number | null;
  };
  audit_result: {
    status: AuditStatus;
    attempts: number | null;
    violations: unknown[];
  };
  candidate: {
    id: number;
    decision: string;
    reason: string | null;
    trigger: string | null;
    trigger_date: string | null;
    source_url: string | null;
    resurfaced: boolean;
  };
  actions: ActionRow[];
}

export interface Highlight {
  text: string;
  claim_ids: number[] | null;
  generated_at?: string;
}

export interface TodayResponse {
  brief: BriefCard | null;
  highlights?: Highlight[];
  run?: { id: number; date: string; status: string; others_not_chosen: number };
  is_today?: boolean;
  message?: string;
  last_run?: { date: string; status: string } | null;
}

export interface BriefList {
  items: BriefCard[];
  next_cursor: string | null;
}

export interface BriefListFilters {
  q?: string;
  series?: string;
  tier?: string;
  track?: 1 | 2;
  status?: VerificationStatus;
  from?: string;
  to?: string;
  include_blocked?: boolean;
}

export interface PeopleCard {
  name: string | null;
  title: string | null;
  company: string;
  bio: string | null;
  role: {
    claim_id: number | null;
    status: ClaimStatus;
    verified_on: string | null;
    source: string | null;
    excerpt: string | null;
    drifted: boolean;
  };
  contact: {
    linkedin_url: string | null;
    email: string | null;
    phone: string | null;
    provider: string | null;
    retrieved_at: string | null;
    opted_out: boolean;
    consent_basis: string | null;
  } | null;
  contact_provider: string;
  alumni: { name: string; tier: string; prior_deal: string | null; boost: number | null } | null;
  co_decision_makers: unknown[];
  outreach_enabled: boolean;
  warning: string | null;
}

export interface OutreachDraft {
  id: number;
  brief_number: number | null;
  subject: string;
  body: string;
  created_at: string;
  outlook_draft_id: string | null;
  claim_ids?: number[];
}

export interface Me {
  email: string;
  role: "operator" | "md";
  display_name: string;
  passkeys: number;
}

// ---- ops -----------------------------------------------------------------------------

export interface OpsRun {
  id: number;
  date: string;
  attempt: number;
  status: string;
  mode: string;
  started_at: string | null;
  finished_at: string | null;
  models: Record<string, string> | null;
  candidates: number;
  summary: string | null;
  error: string | null;
}

export interface CandidateReason {
  rank: number | null;
  company: string;
  score: number | null;
  decision: string;
  reason: string | null;
}

export interface BlocklistRow {
  id: number;
  company: string;
  company_norm: string;
  status: "active" | "closed_lost" | "cooling";
  reason: string | null;
  added_at: string;
  cooling_until: string | null;
  added_by: string | null;
  notes: string | null;
}

export interface AlumniRow {
  id: number;
  name: string;
  previous_role: string | null;
  previous_company: string | null;
  deal_involvement: string | null;
  current_role: string | null;
  current_company: string | null;
  move_date: string | null;
  tier: "strict" | "medium";
  boost_applied: number | null;
  final_score: number | null;
  complications: string | null;
  outreach_status: string | null;
  active: boolean;
  notes: string | null;
}

export interface SponsorRow {
  id: number;
  series: "F1" | "FE";
  level: string;
  team: string | null;
  brand: string;
  category: string | null;
  status: "active" | "joined" | "departed" | "unverified";
  season: string | null;
  notes: string | null;
  source: string | null;
  verified_at: string | null;
}

export interface ProviderUsage {
  providers: { provider: string; records: number; last_retrieved: string | null }[];
  note: string;
}

export interface OpsConfig {
  execution_mode: string;
  models: { scan: string; writer: string; verify: string };
  md_threshold: number;
  freshness_days_track1: number;
  freshness_days_alumni: number;
  dedup_window_days: number;
  max_verification_attempts: number;
  timezone: string;
  anthropic_key_configured: boolean;
  graph_configured: boolean;
  md_email_configured: boolean;
}
