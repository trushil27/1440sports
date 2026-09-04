"""The 13-rule brief audit — a rule-for-rule port of the production n8n ``Audit Brief``
Code node, **Phase 2.1.8d** (``spec/n8n_workflow_production_2026-09-04.json``).

Every check mirrors the JS exactly: the same violation codes, the same severities
(``critical`` / ``medium``), the same regexes (translated verbatim; JS ``\\w``/``\\b`` are
ASCII, so the rule-6 and rule-13 patterns compile with ``re.ASCII``), the same text
helpers (``wc`` strips tags only; ``plainText`` also removes ``&entity;`` tokens) and the
same route decision. Where this port knowingly departs from the JS it says so inline:

* Rule 4 compares against the orchestrator's ``run_date`` rather than ``new Date()`` UTC
  (the pipeline runs at 06:00 Europe/London, when the two coincide; the date is an input
  so tests are deterministic).
* Rule 6 escapes the team label before building the ``(UC|Cap|raw)`` alternation; the JS
  interpolates it raw (a label containing regex metacharacters would be a wildcard).
* Rule 11 counts ``label + detail + counter`` of a risk. The JS sums ``r[0] + ' ' + r[1]``
  — for the production two-element risk ``[label, text]`` that is the entire risk; the
  June-format :class:`~intel.brief_data.Risk` carries a third (counter) element that is
  rendered on the page, so it is included. With an empty ``detail`` the arithmetic is the
  JS's exactly.
* ``operational_fit_section`` / ``operational_fit_content`` (the pre-2.1.8 field names the
  JS still accepts as fallbacks) do not exist on :class:`~intel.brief_data.WrittenBrief`;
  ``value_section`` / ``value_content`` are used alone.

Routing (``_audit_route`` in the JS): no critical violation → ``pass``; otherwise
``retry`` while ``retry_count < 1``, else ``manual_review``. ``previous_violations`` is
carried through untouched — it never influences the route (JS parity). Medium violations
never block. The orchestrator owns the retry loop; see :func:`audit_brief`.
"""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field
from typing import Literal

from intel.brief_data import WrittenBrief

Severity = Literal["critical", "medium"]
Route = Literal["pass", "retry", "manual_review"]

# (number, name, headline severity, description) — the 13 rules in production order.
# Rule 6 also emits two medium sub-codes (count claims) and rule 10 is critical only when
# the value section renders; see CODES for the exact per-code severities.
RULES: tuple[tuple[int, str, Severity, str], ...] = (
    (
        1,
        "deal_duration",
        "critical",
        "deal_arch_para never says TWO YEARS and carries a bold "
        "<font>THREE|FOUR|FIVE YEARS</font> marker",
    ),
    (
        2,
        "opening_quote",
        "critical",
        'opening_angle_quote contains "25 minutes", ends "?" '
        '(optionally followed by &rdquo; / " / curly quote) and does not use 25 minutes as a '
        "metaphor",
    ),
    (3, "opening_intro_declarative", "critical", "opening_angle_intro does not end with '?'"),
    (4, "footer_date", "medium", "footer_date equals the run date as 'D MMM YYYY' uppercase"),
    (5, "industry_meta_no_date", "medium", "industry_meta has no trailing ISO date"),
    (
        6,
        "team_vacancy",
        "critical",
        "the_case_p2 and deck carry no team-vacancy / why-team "
        "pattern (A/B/C/E critical, D medium)",
    ),
    (7, "word_counts", "medium", "Every section within its word ceiling (+5 words grace)"),
    (8, "confidence_not_low", "critical", "confidence_level is not LOW"),
    (9, "track_label", "medium", "track_label is exactly '' or ' · ALUMNI INTELLIGENCE'"),
    (
        10,
        "risk_count",
        "critical",
        "Exactly 2 risks with the value section (critical), exactly 3 without (medium)",
    ),
    (
        11,
        "page2_char_budget",
        "critical",
        "Page-2 plain-text budget: 2300 chars with the value section, 2100 without",
    ),
    (
        12,
        "value_section_required",
        "critical",
        "Value section on when score >= 70; value_content non-empty whenever the section is on",
    ),
    (
        13,
        "phrase_overlap",
        "medium",
        "No 5-word phrase with 3+ content words shared by the_case_p2 and why_team_para",
    ),
)

# Every violation code the production JS can emit → (rule number, severity).
CODES: dict[str, tuple[int, Severity]] = {
    "min_3_year_deal": (1, "critical"),
    "missing_duration_marker": (1, "critical"),
    "opening_quote_ending": (2, "critical"),
    "opening_quote_metaphor": (2, "critical"),
    "opening_intro_question": (3, "critical"),
    "footer_date_mismatch": (4, "medium"),
    "industry_meta_date_suffix": (5, "medium"),
    "why_team_claim_in_case_p2_a": (6, "critical"),
    "why_team_claim_in_case_p2_b": (6, "critical"),
    "why_team_claim_in_case_p2_c": (6, "critical"),
    "count_claim_in_case_p2": (6, "medium"),
    "team_has_no_in_case_p2": (6, "critical"),
    "team_vacancy_in_deck_a": (6, "critical"),
    "team_vacancy_in_deck_e": (6, "critical"),
    "team_vacancy_in_deck_b": (6, "critical"),
    "team_vacancy_in_deck_c": (6, "critical"),
    "count_claim_in_deck": (6, "medium"),
    "low_confidence": (8, "critical"),
    "bad_track_label": (9, "medium"),
    "risk_count": (10, "critical"),  # medium when value_section is false — see _rule_risk_count
    "page2_overflow_risk": (11, "critical"),
    "value_section_missing": (12, "critical"),
    "value_content_empty": (12, "critical"),
    "p2_why_team_phrase_overlap": (13, "medium"),
}

# Rule 7 — the JS `ceilings` object, verbatim. Fields absent/empty on the brief are skipped.
WORD_CEILINGS: dict[str, int] = {
    "deck": 50,
    "the_case_p1": 95,
    "the_case_p2": 75,
    "why_now_callout": 55,
    "why_team_para": 85,
    "value_content": 75,
    "operational_fit_content": 75,
    "deal_arch_para": 70,
    "decision_maker_bio": 50,
    "opening_angle_intro": 18,
    "opening_angle_quote": 45,
}
WORD_CEILING_GRACE = 5  # `if (n > ceilings[key] + 5)`
for _key in WORD_CEILINGS:
    CODES[f"wc_{_key}"] = (7, "medium")

ALUMNI_TRACK_LABEL = " · ALUMNI INTELLIGENCE"
VACANCY_PROXIMITY_CHARS = 100
PAGE2_BUDGET_WITH_VALUE = 2300  # v2.1.8d: 2500 → 2300
PAGE2_BUDGET_WITHOUT_VALUE = 2100  # v2.1.8d: 2300 → 2100
VALUE_SECTION_MIN_SCORE = 70
OVERLAP_NGRAM = 5
OVERLAP_MIN_CONTENT_TOKENS = 3
OVERLAP_TEAM_TOKENS_EXCLUDE = 2

_MONTHS = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")

# --- text helpers (JS `wc` and `plainText`) -------------------------------------------------
_TAG = re.compile(r"<[^>]+>")
_ENTITY = re.compile(r"&[a-z]+;", re.IGNORECASE)
_WS = re.compile(r"\s+")


def js_word_count(s: str | None) -> int:
    """JS ``wc``: tags → space, split on whitespace, count non-empty tokens (entities kept)."""
    return len(_TAG.sub(" ", s or "").split())


def plain_text(s: str | None) -> str:
    """JS ``plainText``: tags → space, ``&entity;`` → space, whitespace collapsed, trimmed."""
    return _WS.sub(" ", _ENTITY.sub(" ", _TAG.sub(" ", s or ""))).strip()


# --- rule regexes ---------------------------------------------------------------------------
_TWO_YEARS = re.compile(r"\bTWO\s+YEARS?\b", re.IGNORECASE)
_DURATION_MARKER = re.compile(r"<font[^>]*>\s*(THREE|FOUR|FIVE) YEARS\s*</font>", re.IGNORECASE)

_QUOTE_ENDING = re.compile(r'\?\s*(&rdquo;|"|[“”]|$)')
_TWENTY_FIVE = re.compile(r"\b25 minutes\b", re.IGNORECASE)
_QUOTE_TAIL = re.compile(r'25 minutes\?\s*(&rdquo;|"|[“”]|$).*$')
_METAPHOR = re.compile(
    r"\b(the|those|these|spending|sitting out|wasting)\s+"
    r"(fastest|hardest|toughest|best|most|same|next|last|whole|entire)?\s*25 minutes\b",
    re.IGNORECASE,
)
_INTRO_QUESTION = re.compile(r"\?\s*$")
_INDUSTRY_DATE_SUFFIX = re.compile(r"[·\-\s]\s*\d{4}-\d{2}-\d{2}\s*$")

# Rule 6 — `vacancyReSrc`, verbatim. Deliberately has no bare "is open" / "slot is open"
# (preserves the Datadog reference construction).
VACANCY_RE_SRC = (
    r"(\b(?:has|carries|holds|hosts)\s+no\s+\w+"
    r"|\b(?:no\s+active|no\s+documented|no\s+title-level|no\s+headline|no\s+current)\s+\w+\s+partner"
    r"|\bcategory\s+(?:is|sits|remains)\s+(?:vacant|available|open|uncontested|empty|unfilled|unclaimed)"
    r"|\bdestination\s+where\s+\w+\s+(?:sits|is)\s+(?:vacant|open|available|unclaimed)"
    r"|\bwhere\s+the\s+\w+(?:\s+\w+){0,4}\s+category\s+is\s+(?:vacant|available|open|uncontested|unclaimed)"
    r"|\b(?:still\s+seeking|yet\s+to\s+(?:sign|land|ink|secure))\b"
    r"|\bcurrently\s+lacks\b"
    r"|\bremains\s+without\b"
    r"|\bis\s+unclaimed\b)"
)
_JS_FLAGS = re.IGNORECASE | re.ASCII  # JS regexes without the u flag: ASCII \w and \b
VACANCY_RE = re.compile(VACANCY_RE_SRC, _JS_FLAGS)
_COUNT_CLAIM_RE = re.compile(
    r"\b(two|three|four|several|multiple)\s+\w+\s+teams?\s+(carry|have|hold)\s+no\b", _JS_FLAGS
)

_NGRAM_PUNCT = re.compile(r"[^\w\s]", re.ASCII)
STOPWORDS = frozenset(
    "a an the and or but of in on at to for with by is are was were from as it its that "
    "this these those be has have".split()
)


@dataclass
class Violation:
    rule: int
    code: str
    severity: Severity
    message: str
    field: str | None = None


@dataclass
class AuditResult:
    violations: list[Violation] = field(default_factory=list)
    retry_count: int = 0
    previous_violations: list = field(default_factory=list)  # pass-through only (JS parity)

    @property
    def critical(self) -> list[Violation]:
        return [v for v in self.violations if v.severity == "critical"]

    @property
    def warnings(self) -> list[Violation]:
        return [v for v in self.violations if v.severity == "medium"]

    @property
    def passed(self) -> bool:
        return not self.critical

    @property
    def route(self) -> Route:
        """JS ``_audit_route``: pass / retry (first failure) / manual_review (failed again).

        The orchestrator maps it as: ``pass`` → render + send path; ``retry`` → feed
        :func:`violations_feedback` back to the writer once (``retry_count`` becomes 1);
        ``manual_review`` → ``AuditStatus.failed``, operator alert, never MD-eligible.
        ``run_daily.produce_brief`` currently calls :func:`audit_brief` without
        ``retry_count`` on both attempts, so it sees ``retry`` twice and applies the same
        outcome by attempt count; passing ``retry_count=attempt - 1`` would make the
        second result read ``manual_review`` directly.
        """
        if self.passed:
            return "pass"
        return "retry" if self.retry_count < 1 else "manual_review"

    def rules_fired(self) -> set[int]:
        return {v.rule for v in self.violations}

    def codes(self) -> set[str]:
        return {v.code for v in self.violations}

    def as_json(self, run_at: dt.datetime | None = None) -> dict:
        """The JS ``_audit`` object."""
        return {
            "passed": self.passed,
            "critical_count": len(self.critical),
            "medium_count": len(self.warnings),
            "violations": [
                {"rule": v.code, "severity": v.severity, "detail": v.message}
                for v in self.violations
            ],
            "retry_count": self.retry_count,
            "run_at": (run_at or dt.datetime.now(dt.UTC)).isoformat(),
        }

    def log_rows(self, brief: WrittenBrief, run_date: dt.date) -> list[dict]:
        """The JS ``_audit_log_rows`` (Audit Log sheet rows): one summary row, then one
        ``violation`` row per violation. NB the summary detail is "No violations." whenever
        no *critical* violation exists, even if medium ones do (JS parity)."""
        company = brief.company or brief.footer_company or "unknown"
        number = brief.brief_number or "???"
        critical, medium = self.critical, self.warnings
        if self.passed:
            rule, severity, detail = "audit_passed", "info", "No violations."
        else:
            rule = (
                "audit_failed_manual_review"
                if self.route == "manual_review"
                else "audit_failed_retrying"
            )
            severity = "critical" if critical else "medium"
            detail = f"{len(critical)} critical, {len(medium)} medium (retry={self.retry_count})"
        base = {"run_date": run_date.isoformat(), "brief_number": number, "company": company}
        rows = [
            {**base, "row_type": "summary", "rule": rule, "severity": severity, "detail": detail}
        ]
        rows += [
            {
                **base,
                "row_type": "violation",
                "rule": v.code,
                "severity": v.severity,
                "detail": v.message,
            }
            for v in self.violations
        ]
        return rows


def _v(code: str, detail: str, field_name: str | None = None, severity: Severity | None = None):
    num, sev = CODES[code]
    return Violation(
        rule=num, code=code, severity=severity or sev, message=detail, field=field_name
    )


# --------------------------------------------------------------------------- rules


def _rule1_deal_duration(b: WrittenBrief) -> list[Violation]:
    para = b.deal_arch_para or ""
    out = []
    if _TWO_YEARS.search(plain_text(para)):
        out.append(_v("min_3_year_deal", "deal_arch_para proposes TWO YEARS", "deal_arch_para"))
    if not _DURATION_MARKER.search(para):
        out.append(
            _v(
                "missing_duration_marker",
                "deal_arch_para missing bold THREE/FOUR/FIVE YEARS marker",
                "deal_arch_para",
            )
        )
    return out


def quote_without_ask(quote: str) -> str:
    """The quote with everything from ``25 minutes?`` onward removed (the JS ``quoteNoEnd``)."""
    return _QUOTE_TAIL.sub("", quote)


def _rule2_opening_quote(b: WrittenBrief) -> list[Violation]:
    quote = (b.opening_angle_quote or "").strip()
    out = []
    if not _QUOTE_ENDING.search(quote) or not _TWENTY_FIVE.search(quote):
        out.append(
            _v(
                "opening_quote_ending",
                'opening_angle_quote must contain "25 minutes" and end with "?"',
                "opening_angle_quote",
            )
        )
    if _METAPHOR.search(quote_without_ask(quote)):
        out.append(
            _v("opening_quote_metaphor", "25 minutes used as metaphor", "opening_angle_quote")
        )
    return out


def _rule3_opening_intro(b: WrittenBrief) -> list[Violation]:
    intro = (b.opening_angle_intro or "").strip()
    if _INTRO_QUESTION.search(intro):
        return [
            _v(
                "opening_intro_question",
                'opening_angle_intro ends with "?" — must be declarative',
                "opening_angle_intro",
            )
        ]
    return []


def expected_footer_date(run_date: dt.date) -> str:
    """'D MMM YYYY' uppercase, no leading zero — e.g. '21 MAY 2026'."""
    return f"{run_date.day} {_MONTHS[run_date.month - 1]} {run_date.year}"


def _rule4_footer_date(b: WrittenBrief, run_date: dt.date) -> list[Violation]:
    want = expected_footer_date(run_date)
    if (b.footer_date or "").upper().strip() != want:
        return [
            _v("footer_date_mismatch", f"footer_date '{b.footer_date}' != today", "footer_date")
        ]
    return []


def _rule5_industry_meta(b: WrittenBrief) -> list[Violation]:
    if _INDUSTRY_DATE_SUFFIX.search(b.industry_meta or ""):
        return [_v("industry_meta_date_suffix", "industry_meta has trailing date", "industry_meta")]
    return []


def team_pattern(team_label: str) -> str:
    """The JS ``teamPattern``: ``(UPPER|Capitalised Words|raw)`` for the trimmed label."""
    raw = (team_label or "").strip()
    cap = " ".join(w[:1].upper() + w[1:].lower() for w in raw.split())
    return "(" + "|".join(re.escape(x) for x in (raw.upper(), cap, raw)) + ")"


def team_regex(team_label: str) -> re.Pattern[str]:
    return re.compile(r"\b" + team_pattern(team_label) + r"\b", _JS_FLAGS)


def team_vacancy_distance(text: str, team_label: str) -> int | None:
    """Minimum start-index distance between any team mention and any vacancy clause
    (the JS ``teamPlusVacancyWithin`` measure); None when either is absent."""
    t = [m.start() for m in team_regex(team_label).finditer(text)]
    v = [m.start() for m in VACANCY_RE.finditer(text)]
    if not t or not v:
        return None
    return min(abs(a - b) for a in t for b in v)


def team_vacancy_within(text: str, team_label: str, limit: int = VACANCY_PROXIMITY_CHARS) -> bool:
    d = team_vacancy_distance(text, team_label)
    return d is not None and d <= limit


def _rule6_team_vacancy(b: WrittenBrief) -> list[Violation]:
    team_raw = (b.team_label or "").strip()
    if not team_raw:
        return []
    p2 = plain_text(b.the_case_p2)
    deck = plain_text(b.deck)
    tp = team_pattern(team_raw)
    re_a = re.compile(
        r"\b"
        + tp
        + r"\s+is\s+(the\s+only|where\b|one\s+of\s+the\s+only|the\s+destination\s+where)",
        _JS_FLAGS,
    )
    re_c = re.compile(
        r"\b(only|lone|sole)\s+[A-Z]{1,3}\s*\w*\s+team[^.]{0,80}\b" + tp + r"\b", _JS_FLAGS
    )
    re_e = re.compile(r"\b" + tp + r"\s+(has|carries|holds|hosts)\s+no\b", _JS_FLAGS)
    out = []
    # p2 — order A, B, C, D, E as in the JS
    if re_a.search(p2):
        out.append(
            _v(
                "why_team_claim_in_case_p2_a",
                "the_case_p2 has '[Team] is the only/where/destination' pattern",
                "the_case_p2",
            )
        )
    if team_vacancy_within(p2, team_raw):
        out.append(
            _v(
                "why_team_claim_in_case_p2_b",
                "the_case_p2 names team within 100 chars of a vacancy clause",
                "the_case_p2",
            )
        )
    if re_c.search(p2):
        out.append(
            _v(
                "why_team_claim_in_case_p2_c",
                "the_case_p2 has 'only [N]-team' framing naming recommended team",
                "the_case_p2",
            )
        )
    if _COUNT_CLAIM_RE.search(p2):
        out.append(
            _v("count_claim_in_case_p2", "the_case_p2 makes counted-teams claim", "the_case_p2")
        )
    if re_e.search(p2):
        out.append(
            _v(
                "team_has_no_in_case_p2",
                "the_case_p2 has '[Team] has/carries no X' pattern",
                "the_case_p2",
            )
        )
    # deck — order A, E, B, C, D as in the JS (C and D added to the deck in v2.1.8d)
    if re_a.search(deck):
        out.append(
            _v(
                "team_vacancy_in_deck_a",
                "deck has '[Team] is the only/where/destination' — must be company-side only",
                "deck",
            )
        )
    if re_e.search(deck):
        out.append(
            _v(
                "team_vacancy_in_deck_e",
                "deck has '[Team] HAS NO X' pattern — must be company-side only",
                "deck",
            )
        )
    if team_vacancy_within(deck, team_raw):
        out.append(
            _v(
                "team_vacancy_in_deck_b",
                "deck names team within 100 chars of a vacancy clause — must be company-side only",
                "deck",
            )
        )
    if re_c.search(deck):
        out.append(
            _v(
                "team_vacancy_in_deck_c",
                "deck has 'only [N]-team' framing — must be company-side only",
                "deck",
            )
        )
    if _COUNT_CLAIM_RE.search(deck):
        out.append(
            _v(
                "count_claim_in_deck",
                "deck makes counted-teams claim — must be company-side only",
                "deck",
            )
        )
    return out


def _rule7_word_counts(b: WrittenBrief) -> list[Violation]:
    out = []
    for key, ceiling in WORD_CEILINGS.items():
        value = getattr(b, key, None)
        if not value:
            continue
        n = js_word_count(value)
        if n > ceiling + WORD_CEILING_GRACE:
            out.append(_v(f"wc_{key}", f"{key}: {n} words > {ceiling}", key))
    return out


def _rule8_confidence(b: WrittenBrief) -> list[Violation]:
    if (b.confidence_level or "").upper() == "LOW":
        return [_v("low_confidence", "confidence_level is LOW", "confidence_level")]
    return []


def _rule9_track_label(b: WrittenBrief) -> list[Violation]:
    tl = b.track_label
    if tl is not None and tl != "" and tl != ALUMNI_TRACK_LABEL:
        return [_v("bad_track_label", f"track_label '{tl}' invalid", "track_label")]
    return []


def _value_on(b: WrittenBrief) -> bool:
    return bool(b.value_section)


def _rule10_risk_count(b: WrittenBrief) -> list[Violation]:
    value_on = _value_on(b)
    expected = 2 if value_on else 3
    if len(b.risks) != expected:
        return [
            _v(
                "risk_count",
                f"risks={len(b.risks)}, expected {expected}",
                "risks",
                severity="critical" if value_on else "medium",
            )
        ]
    return []


def page2_chars(b: WrittenBrief) -> int:
    """The JS ``total``: six page-2 prose fields + every risk, plain-text lengths summed.
    ``value_content`` counts whether or not the section is switched on (JS parity)."""
    sections = [
        b.why_team_para,
        b.value_content,
        b.deal_arch_para,
        b.decision_maker_bio,
        b.opening_angle_intro,
        b.opening_angle_quote,
    ]
    b_chars = sum(len(plain_text(s)) for s in sections)
    r_chars = sum(len(plain_text(f"{r.label} {r.detail} {r.counter}")) for r in b.risks)
    return b_chars + r_chars


def _rule11_page2_budget(b: WrittenBrief) -> list[Violation]:
    budget = PAGE2_BUDGET_WITH_VALUE if _value_on(b) else PAGE2_BUDGET_WITHOUT_VALUE
    total = page2_chars(b)
    if total > budget:
        return [_v("page2_overflow_risk", f"page-2 char budget exceeded: {total} > {budget}")]
    return []


def _rule12_value_section(b: WrittenBrief) -> list[Violation]:
    value_on = _value_on(b)
    score = int(b.score or 0)
    out = []
    if score >= VALUE_SECTION_MIN_SCORE and not value_on:
        out.append(
            _v(
                "value_section_missing",
                f"value_section is false but score {score} >= 70 — must render VALUE TO [TEAM]",
                "value_section",
            )
        )
    if value_on and not plain_text(b.value_content):
        out.append(
            _v(
                "value_content_empty",
                "value_section is true but value_content is empty",
                "value_content",
            )
        )
    return out


def ngrams(text: str, n: int = OVERLAP_NGRAM) -> list[str]:
    words = _NGRAM_PUNCT.sub(" ", (text or "").lower()).split()
    return [" ".join(words[i : i + n]) for i in range(len(words) - n + 1)]


def shared_phrases(p2: str, why_team: str, team_label: str = "") -> list[str]:
    """5-grams of ``p2`` (plain text) also present in ``why_team``, first occurrence order,
    with 3+ non-stopword tokens and fewer than 2 tokens from the team label."""
    wt_set = set(ngrams(plain_text(why_team)))
    team_words = (team_label or "").strip().lower().split()
    seen: set[str] = set()
    out: list[str] = []
    for phrase in ngrams(plain_text(p2)):
        if phrase not in wt_set or phrase in seen:
            continue
        seen.add(phrase)
        tokens = phrase.split(" ")
        if sum(t not in STOPWORDS for t in tokens) < OVERLAP_MIN_CONTENT_TOKENS:
            continue
        if team_words and sum(t in team_words for t in tokens) >= OVERLAP_TEAM_TOKENS_EXCLUDE:
            continue
        out.append(phrase)
    return out


def _rule13_phrase_overlap(b: WrittenBrief) -> list[Violation]:
    shared = shared_phrases(b.the_case_p2, b.why_team_para, (b.team_label or "").strip())
    if not shared:
        return []
    more = f" (+{len(shared) - 1} more)" if len(shared) > 1 else ""
    return [
        _v(
            "p2_why_team_phrase_overlap",
            f'5+ word phrase shared: "{shared[0]}"{more}',
            "why_team_para",
        )
    ]


# --------------------------------------------------------------------------- API


def audit_brief(
    brief: WrittenBrief,
    run_date: dt.date,
    retry_count: int = 0,
    previous_violations: list | None = None,
) -> AuditResult:
    """Run the 13 rules in production order and decide the route.

    ``retry_count`` is the JS ``retry_count`` (0 on the first draft, 1 on the corrected
    draft the writer produced from :func:`violations_feedback`); it decides ``retry`` vs
    ``manual_review``. ``previous_violations`` is stored on the result but has no effect on
    the outcome, exactly as in the JS.
    """
    violations: list[Violation] = []
    violations += _rule1_deal_duration(brief)
    violations += _rule2_opening_quote(brief)
    violations += _rule3_opening_intro(brief)
    violations += _rule4_footer_date(brief, run_date)
    violations += _rule5_industry_meta(brief)
    violations += _rule6_team_vacancy(brief)
    violations += _rule7_word_counts(brief)
    violations += _rule8_confidence(brief)
    violations += _rule9_track_label(brief)
    violations += _rule10_risk_count(brief)
    violations += _rule11_page2_budget(brief)
    violations += _rule12_value_section(brief)
    violations += _rule13_phrase_overlap(brief)
    return AuditResult(violations, int(retry_count or 0), list(previous_violations or []))


def violations_feedback(result: AuditResult) -> str:
    """The violation lines the production ``Retry Prep`` node feeds back to the writer:
    ``- [SEVERITY] code: detail``, one per line (empty when there are none). ``brief.py``
    wraps them in the RETRY MODE block the writer prompt expects."""
    return "\n".join(f"- [{v.severity.upper()}] {v.code}: {v.message}" for v in result.violations)
