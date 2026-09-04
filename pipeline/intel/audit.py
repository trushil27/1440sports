"""The 13-rule brief audit (spec/production_roadmap.md §2.1.8 — "Audit Brief" node).

Audits the writer's ``WrittenBrief`` for structure and brand compliance. Every check
runs on plain text — the spec's inline ``<font>`` markup is stripped first via
``brief_data.strip_markup`` — and the rule list is ported exactly as the roadmap
lists it: twelve high-severity rules plus rule 13 (phrase overlap) at medium.

Routing: a brief with no high-severity violation routes ``pass``; anything else
routes ``retry`` (the orchestrator owns the single retry and the operator-review
fallback — not this module). Medium violations are warnings and never block.

Word-count ceilings come from spec/n8n_v21_prompts.md NODE 2 (WORD COUNT MAXIMUMS),
the track-label and date formats from its TRACK LABEL / DATE HANDLING blocks, and the
deck / THE CASE p2 vacancy prohibition from the deck rule + Section Content Boundaries.
"""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field
from typing import Literal

from intel.brief_data import WrittenBrief, strip_markup, word_count

Severity = Literal["high", "medium"]

# (number, code, severity, description) — in roadmap order. Do not add rules.
RULES: tuple[tuple[int, str, Severity, str], ...] = (
    (1, "deal_duration", "high", "Deal architecture states a duration of at least THREE YEARS"),
    (2, "opening_quote", "high", 'Opening quote contains "25 minutes" and ends with "?"'),
    (3, "opening_intro_declarative", "high", "Opening intro is declarative (no question mark)"),
    (4, "footer_date", "high", "footer_date matches the run date as 'D MMM YYYY' uppercase"),
    (5, "industry_meta_no_date", "high", "industry_meta carries no trailing date"),
    (
        6,
        "team_vacancy_proximity",
        "high",
        "Deck and THE CASE p2 never name the team within 100 chars of a vacancy clause",
    ),
    (7, "word_counts", "high", "Every section is within its word-count ceiling"),
    (8, "confidence_not_low", "high", "confidence_level is not LOW"),
    (9, "track_label", "high", "track_label is exactly '' or ' · ALUMNI INTELLIGENCE'"),
    (10, "risk_count", "high", "Exactly 2 risks with the value section, exactly 3 without"),
    (
        11,
        "page2_char_budget",
        "high",
        "Page-2 plain-text budget: 2500 chars with value section, 2300 without",
    ),
    (
        12,
        "value_section_required",
        "high",
        "Value section renders (label + content) when score >= 70",
    ),
    (
        13,
        "phrase_overlap",
        "medium",
        "No 5+ word substantive phrase shared by THE CASE p2 and WHY [TEAM]",
    ),
)
_RULE_BY_CODE = {code: (num, sev) for num, code, sev, _ in RULES}

MIN_DEAL_YEARS = 3
ALUMNI_TRACK_LABEL = " · ALUMNI INTELLIGENCE"
VACANCY_PROXIMITY_CHARS = 100
PAGE2_BUDGET_WITH_VALUE = 2500
PAGE2_BUDGET_WITHOUT_VALUE = 2300
VALUE_SECTION_MIN_SCORE = 70
OVERLAP_MIN_WORDS = 5
OVERLAP_MIN_SUBSTANTIVE = 2

# NODE 2 WORD COUNT MAXIMUMS (hard ceilings).
WORD_CEILINGS: dict[str, int] = {
    "deck": 50,
    "the_case_p1": 95,
    "the_case_p2": 75,
    "why_now_callout": 55,
    "why_team_para": 85,
    "value_content": 70,
    "deal_arch_para": 70,
    "decision_maker_bio": 50,
    "opening_angle_intro": 18,
    "opening_angle_quote": 45,
}
RISK_WORD_CEILING = 32  # detail + counter combined
SCORE_NOTE_WORD_CEILING = 8

_MONTHS = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")
_MONTH_RE = (
    r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)"
    r"(?:uary|ruary|ch|il|e|y|ust|tember|ober|ember)?\.?"
)
_TRAILING_DATE_PATTERNS = (
    re.compile(r"\d{4}-\d{2}-\d{2}\s*$"),  # ISO, also covers "· YYYY-MM-DD"
    re.compile(rf"\b\d{{1,2}}\s+{_MONTH_RE}\s+\d{{4}}\s*$", re.I),  # D MMM YYYY
    re.compile(rf"\b{_MONTH_RE}\s+\d{{4}}\s*$", re.I),  # month-year
)

_WORD_NUMBERS = {
    w: i + 1
    for i, w in enumerate(
        ("one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten")
    )
}
_YEARS_RE = re.compile(
    r"\b(one|two|three|four|five|six|seven|eight|nine|ten|\d+)[\s-]*(?:year|yr)s?\b", re.I
)
_MONTHS_RE = re.compile(r"\b(\d+)[\s-]*months?\b", re.I)

_VACANCY_PATTERNS = tuple(
    re.compile(p, re.I)
    for p in (
        r"no .{0,40}(?:partner|sponsor)",
        r"slot .{0,20}(?:open|empty|vacant)",
        r"open (?:slot|lane|category|at)",
        r"vacan",
        r"has no",
        r"whitespace",
        r"uncontested",
        r"unoccupied",
        r"is open",
    )
)

_TRAILING_QUOTES = "\"'”’»“‘"
_TOKEN_RE = re.compile(r"[a-z0-9]+(?:'[a-z]+)?")
STOPWORDS = frozenset(
    """
    a an the and or but nor so yet of in on at to for from by with as into onto over
    under than then that this these those there here it its is are was were be been
    being am do does did has have had not no yes if when where which who whom whose
    what while up down out off about above below between through during before after
    all any both each few more most other some such only own same too very can will
    just also very s t
    """.split()
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

    @property
    def passed(self) -> bool:
        return not any(v.severity == "high" for v in self.violations)

    @property
    def route(self) -> Literal["pass", "retry"]:
        return "pass" if self.passed else "retry"

    @property
    def warnings(self) -> list[Violation]:
        return [v for v in self.violations if v.severity == "medium"]

    def rules_fired(self) -> set[int]:
        return {v.rule for v in self.violations}


def _v(code: str, message: str, field_name: str | None = None) -> Violation:
    num, sev = _RULE_BY_CODE[code]
    return Violation(rule=num, code=code, severity=sev, message=message, field=field_name)


# --------------------------------------------------------------------------- rules


def _rule_deal_duration(b: WrittenBrief) -> list[Violation]:
    text = strip_markup(b.deal_arch_para)
    years: list[int] = []
    for m in _YEARS_RE.finditer(text):
        raw = m.group(1).lower()
        years.append(_WORD_NUMBERS.get(raw) or int(raw))
    for m in _MONTHS_RE.finditer(text):
        years.append(int(m.group(1)) // 12)
    if not years:
        return [_v("deal_duration", "deal_arch_para names no deal duration", "deal_arch_para")]
    if max(years) < MIN_DEAL_YEARS:
        return [
            _v(
                "deal_duration",
                f"deal_arch_para states a {max(years)}-year term; minimum is THREE YEARS",
                "deal_arch_para",
            )
        ]
    return []


def _rule_opening_quote(b: WrittenBrief) -> list[Violation]:
    text = strip_markup(b.opening_angle_quote)
    out: list[Violation] = []
    if "25 minutes" not in text:
        out.append(
            _v("opening_quote", 'opening_angle_quote lacks "25 minutes"', "opening_angle_quote")
        )
    if not text.rstrip().rstrip(_TRAILING_QUOTES).rstrip().endswith("?"):
        out.append(
            _v("opening_quote", 'opening_angle_quote does not end with "?"', "opening_angle_quote")
        )
    return out


def _rule_opening_intro(b: WrittenBrief) -> list[Violation]:
    if "?" in strip_markup(b.opening_angle_intro):
        return [
            _v(
                "opening_intro_declarative",
                "opening_angle_intro must be declarative (contains '?')",
                "opening_angle_intro",
            )
        ]
    return []


def expected_footer_date(run_date: dt.date) -> str:
    """'D MMM YYYY' uppercase, no leading zero — e.g. '21 MAY 2026'."""
    return f"{run_date.day} {_MONTHS[run_date.month - 1]} {run_date.year}"


def _rule_footer_date(b: WrittenBrief, run_date: dt.date) -> list[Violation]:
    want = expected_footer_date(run_date)
    if strip_markup(b.footer_date) != want:
        return [
            _v("footer_date", f"footer_date is {b.footer_date!r}; expected {want!r}", "footer_date")
        ]
    return []


def _rule_industry_meta(b: WrittenBrief) -> list[Violation]:
    tail = strip_markup(b.industry_meta)[-20:]
    if any(p.search(tail) for p in _TRAILING_DATE_PATTERNS):
        return [_v("industry_meta_no_date", "industry_meta ends with a date", "industry_meta")]
    return []


def team_name_variants(team_label: str) -> list[str]:
    """Full label plus its first and last words when they are 4+ letters."""
    label = strip_markup(team_label)
    words = [w for w in re.findall(r"[A-Za-z][A-Za-z'-]*", label)]
    variants = [label] if label else []
    for w in words[:1] + words[-1:]:
        if len(w) >= 4 and w.lower() != label.lower():
            variants.append(w)
    return list(dict.fromkeys(v for v in variants if v))


def _spans_near(a: tuple[int, int], b: tuple[int, int], limit: int) -> bool:
    if a[0] > b[1]:
        return a[0] - b[1] <= limit
    if b[0] > a[1]:
        return b[0] - a[1] <= limit
    return True  # overlapping


def find_vacancy_proximity(
    text: str, team_label: str, limit: int = VACANCY_PROXIMITY_CHARS
) -> str | None:
    """Return the offending vacancy phrase if the team is named within ``limit`` chars of it."""
    plain = strip_markup(text)
    team_spans: list[tuple[int, int]] = []
    for variant in team_name_variants(team_label):
        for m in re.finditer(rf"(?<![A-Za-z]){re.escape(variant)}(?![A-Za-z])", plain, re.I):
            team_spans.append(m.span())
    if not team_spans:
        return None
    for pat in _VACANCY_PATTERNS:
        for m in pat.finditer(plain):
            if any(_spans_near(m.span(), ts, limit) for ts in team_spans):
                return m.group(0)
    return None


def _rule_team_vacancy(b: WrittenBrief) -> list[Violation]:
    out: list[Violation] = []
    for name in ("deck", "the_case_p2"):
        hit = find_vacancy_proximity(getattr(b, name), b.team_label)
        if hit:
            out.append(
                _v(
                    "team_vacancy_proximity",
                    f"{name} names {b.team_label!r} within {VACANCY_PROXIMITY_CHARS} chars "
                    f"of vacancy clause {hit!r}",
                    name,
                )
            )
    return out


def _rule_word_counts(b: WrittenBrief) -> list[Violation]:
    out: list[Violation] = []

    def check(name: str, text: str, ceiling: int) -> None:
        n = word_count(text)
        if n > ceiling:
            out.append(_v("word_counts", f"{name} is {n} words; ceiling {ceiling}", name))

    for name, ceiling in WORD_CEILINGS.items():
        if name == "value_content" and not b.value_section:
            continue
        text = b.why_now_text if name == "why_now_callout" else getattr(b, name)
        check(name, text, ceiling)
    for i, r in enumerate(b.risks, 1):
        check(f"risks[{i}]", f"{r.detail} {r.counter}", RISK_WORD_CEILING)
    for i, c in enumerate(b.score_cells, 1):
        check(f"score_cells[{i}] ({c.label})", c.note, SCORE_NOTE_WORD_CEILING)
    return out


def _rule_confidence(b: WrittenBrief) -> list[Violation]:
    if strip_markup(b.confidence_level).upper() == "LOW":
        return [_v("confidence_not_low", "confidence_level is LOW", "confidence_level")]
    return []


def _rule_track_label(b: WrittenBrief) -> list[Violation]:
    if b.track_label not in ("", ALUMNI_TRACK_LABEL):
        return [
            _v(
                "track_label",
                f"track_label is {b.track_label!r}; must be '' or {ALUMNI_TRACK_LABEL!r}",
                "track_label",
            )
        ]
    return []


def _rule_risk_count(b: WrittenBrief) -> list[Violation]:
    want = 2 if b.value_section else 3
    if len(b.risks) != want:
        return [
            _v(
                "risk_count",
                f"{len(b.risks)} risks; expected exactly {want} "
                f"({'with' if b.value_section else 'without'} value section)",
                "risks",
            )
        ]
    return []


def page2_chars(b: WrittenBrief) -> int:
    parts = [
        b.why_team_para,
        b.value_content if b.value_section else "",
        b.deal_arch_para,
        b.decision_maker_bio,
        b.opening_angle_intro,
        b.opening_angle_quote,
        *(c.note for c in b.score_cells),
        *(f"{r.detail} {r.counter}" for r in b.risks),
    ]
    return sum(len(strip_markup(p)) for p in parts)


def _rule_page2_budget(b: WrittenBrief) -> list[Violation]:
    budget = PAGE2_BUDGET_WITH_VALUE if b.value_section else PAGE2_BUDGET_WITHOUT_VALUE
    n = page2_chars(b)
    if n > budget:
        return [_v("page2_char_budget", f"page-2 sections total {n} chars; budget {budget}")]
    return []


def _rule_value_section(b: WrittenBrief) -> list[Violation]:
    if b.score < VALUE_SECTION_MIN_SCORE:
        return []
    problems = []
    if not b.value_section:
        problems.append("value_section is false")
    if not strip_markup(b.value_content):
        problems.append("value_content is empty")
    if not strip_markup(b.value_section_label):
        problems.append("value_section_label is empty")
    if problems:
        return [
            _v(
                "value_section_required",
                f"score {b.score} >= {VALUE_SECTION_MIN_SCORE} but " + "; ".join(problems),
                "value_section",
            )
        ]
    return []


def _tokens(text: str) -> list[str]:
    return _TOKEN_RE.findall(strip_markup(text).lower())


def shared_phrases(a: str, b: str, n: int = OVERLAP_MIN_WORDS) -> list[str]:
    """Maximal runs of ``n``+ consecutive words shared by ``a`` and ``b`` with 2+ non-stopwords."""
    ta, tb = _tokens(a), _tokens(b)
    grams_b = {tuple(tb[i : i + n]) for i in range(len(tb) - n + 1)}
    runs: list[str] = []
    i = 0
    while i <= len(ta) - n:
        if tuple(ta[i : i + n]) in grams_b:
            j = i + n
            while j < len(ta) and tuple(ta[j - n + 1 : j + 1]) in grams_b:
                j += 1
            run = ta[i:j]
            if sum(w not in STOPWORDS for w in run) >= OVERLAP_MIN_SUBSTANTIVE:
                runs.append(" ".join(run))
            i = j
        else:
            i += 1
    return runs


def _rule_phrase_overlap(b: WrittenBrief) -> list[Violation]:
    return [
        _v(
            "phrase_overlap",
            f"the_case_p2 and why_team_para share the phrase {run!r}",
            "why_team_para",
        )
        for run in shared_phrases(b.the_case_p2, b.why_team_para)
    ]


# --------------------------------------------------------------------------- API


def audit_brief(brief: WrittenBrief, run_date: dt.date) -> AuditResult:
    violations: list[Violation] = []
    violations += _rule_deal_duration(brief)
    violations += _rule_opening_quote(brief)
    violations += _rule_opening_intro(brief)
    violations += _rule_footer_date(brief, run_date)
    violations += _rule_industry_meta(brief)
    violations += _rule_team_vacancy(brief)
    violations += _rule_word_counts(brief)
    violations += _rule_confidence(brief)
    violations += _rule_track_label(brief)
    violations += _rule_risk_count(brief)
    violations += _rule_page2_budget(brief)
    violations += _rule_value_section(brief)
    violations += _rule_phrase_overlap(brief)
    return AuditResult(violations=violations)


def violations_feedback(result: AuditResult) -> str:
    """Numbered plain-text list of violations, for the writer's retry message."""
    if not result.violations:
        return "No audit violations."
    lines = []
    for i, v in enumerate(result.violations, 1):
        where = f" [{v.field}]" if v.field else ""
        lines.append(f"{i}. Rule {v.rule} ({v.code}, {v.severity}){where}: {v.message}")
    return "\n".join(lines)
