"""intel.inbox — the desk's other two sources feed the same 06:00 pick.

Until 7 Sep 2026 the daily brief came from the pipeline's own scanner alone; the Claude
routine's mail and n8n's went to a human and nothing read them. The operator's question was
the right one: "I thought we have 3 sources to see in one app."
"""

from __future__ import annotations

import datetime as dt
import json

from intel import inbox

RECEIVED = dt.datetime(2026, 9, 7, 9, 17, tzinfo=dt.UTC)

ROUTINE_BODY = (
    "<SIGNALS>\n"
    + json.dumps(
        [
            {
                "company": "Nexeon",
                "series": "FE",
                "team": "Jaguar TCS Racing",
                "trigger": "£100m round anchored by the UK National Wealth Fund",
                "trigger_date": "2026-09-01",
                "source_url": "https://www.nationalwealthfund.org.uk/news/nexeon",
                "person": "Dr. Scott Brown",
                "role": "Chief Executive Officer",
                "score": 80,
            },
            {"company": "Gridsight", "trigger": "$26m Series B", "score": 59},
        ]
    )
    + "</SIGNALS>\n\nDesk — today's run, weighted to Formula E."
)


def test_the_routine_block_becomes_leads_and_prose_is_left_alone():
    leads = inbox.parse_routine_email(ROUTINE_BODY, RECEIVED)
    assert [x.company for x in leads] == ["Nexeon", "Gridsight"]
    nexeon = leads[0]
    assert nexeon.source == "routine" and nexeon.series == "FE" and nexeon.score == 80
    assert nexeon.trigger_date == "2026-09-01" and nexeon.is_candidate
    # no source URL: a name to research, not a candidate — nothing is invented to fill it
    assert leads[1].is_candidate is False


def test_a_mail_without_a_block_or_with_broken_json_yields_nothing():
    assert inbox.parse_routine_email("Three prospects clear the bar today.") == []
    assert inbox.parse_routine_email("<SIGNALS>[{not json}]</SIGNALS>") == []


def test_the_n8n_subject_names_the_company_and_nothing_more_is_claimed():
    lead = inbox.parse_n8n_email("1440 Intelligence Brief — Keyfactor — 15 Jul 2026", RECEIVED)
    assert lead and lead.company == "Keyfactor" and lead.source == "n8n"
    assert lead.trigger is None and lead.is_candidate is False
    assert inbox.parse_n8n_email("Re: lunch") is None


def test_both_sources_are_read_from_one_mailbox_and_deduplicated():
    messages = [
        {
            "subject": "1440 Routine Signals — 7 Sep 2026",
            "receivedDateTime": "2026-09-07T09:17:00Z",
            "body": {"content": ROUTINE_BODY},
        },
        {
            "subject": "1440 Intelligence Brief — Keyfactor — 15 Jul 2026",
            "receivedDateTime": "2026-09-07T08:00:00Z",
            "body": {"content": "<html>…</html>"},
        },
        {
            "subject": "1440 Intelligence Brief — Nexeon — 6 Sep 2026",  # already seen above
            "receivedDateTime": "2026-09-07T07:00:00Z",
            "body": {"content": "<html>…</html>"},
        },
        {"subject": "Lunch?", "receivedDateTime": "2026-09-07T06:00:00Z", "body": {"content": "x"}},
    ]
    leads = inbox.leads_from_messages(messages)
    assert [(x.company, x.source) for x in leads] == [
        ("Nexeon", "routine"),
        ("Gridsight", "routine"),
        ("Keyfactor", "n8n"),
    ]


def test_only_candidate_shaped_leads_enter_the_pool_and_the_desk_rescores_them():
    signals = inbox.as_signals(inbox.parse_routine_email(ROUTINE_BODY, RECEIVED))
    assert [s.company for s in signals] == ["Nexeon"]
    s = signals[0]
    assert s.source_url == "https://www.nationalwealthfund.org.uk/news/nexeon"
    assert s.signal_date == "2026-09-01" and s.person == "Dr. Scott Brown" and s.track == 1


def test_the_inbox_note_says_what_was_read_and_why_nothing_was_new(monkeypatch):
    """8 Sep 2026: "0 routine + 0 n8n" and no way to tell whether the mailbox was empty, the
    routine's mail was missing, or every lead was already known. Now each step is counted."""

    class Mailer:
        sender, refresh_token, http = "d@x.test", "rt", None

        def token(self):
            return "t"

    messages = [
        {
            "subject": "1440 Routine Signals — 7 Sep 2026",
            "receivedDateTime": "2026-09-07T09:17:00Z",
            "body": {"content": ROUTINE_BODY},
        },
        {"subject": "Lunch?", "receivedDateTime": "2026-09-07T06:00:00Z", "body": {"content": "x"}},
    ]
    monkeypatch.setattr(inbox.GraphInbox, "read", lambda self, since, limit=40: messages)
    monkeypatch.setattr(inbox, "known_companies", lambda session: {"nexeon"})
    signals, note = inbox.collect(None, None, Mailer())
    assert note["status"] == "read" and note["mails_read"] == 2 and note["routine_mails"] == 1
    assert note["offered"] == ["Nexeon (routine)", "Gridsight (routine)"]
    assert note["already_known"] == ["Nexeon"]
    assert [s.company for s in signals] == []  # Gridsight has no source URL: research, not pool
    assert note["to_research"] == ["Gridsight"]


def test_an_unreadable_mailbox_is_a_missing_source_not_a_failed_run():
    class Boom:
        sender, refresh_token, http = "d@x.test", "rt", None

        def token(self):
            raise RuntimeError("Mail.Read not consented")

    signals, note = inbox.collect(None, None, Boom())
    assert signals == [] and "unavailable" in note["status"]
    signals, note = inbox.collect(None, None, object())
    assert signals == [] and "no mailbox" in note["status"]


def test_the_routine_mail_is_html_by_the_time_it_is_read():
    """Run 192 (7 Sep 2026) read the mailbox correctly and found nothing: the mail client had
    dropped the <SIGNALS> tag, wrapped the array in <p> and encoded & as &amp;."""
    body = (
        "<div><p>\n[\n  {&quot;company&quot;: &quot;Gridsight&quot;, "
        "&quot;role&quot;: &quot;Co-founder &amp; CEO&quot;, "
        "&quot;trigger&quot;: &quot;$26m Series B&quot;, "
        "&quot;source_url&quot;: &quot;https://esgtoday.com/gridsight&quot;, "
        "&quot;score&quot;: 59}\n]</p><p>Desk — today's run.</p></div>"
    )
    leads = inbox.parse_routine_email(body, RECEIVED)
    assert [x.company for x in leads] == ["Gridsight"]
    assert leads[0].role == "Co-founder & CEO" and leads[0].is_candidate


def test_escaped_signals_tags_still_delimit_the_block():
    body = '&lt;SIGNALS&gt;[{"company": "Acme", "score": 70}]&lt;/SIGNALS&gt;<br>prose'
    assert [x.company for x in inbox.parse_routine_email(body)] == ["Acme"]


def test_prose_that_merely_mentions_brackets_is_not_a_signal():
    assert inbox.parse_routine_email("<p>We looked at [1] and [2] and found nothing.</p>") == []


def test_a_thin_lead_is_scored_by_the_desk_s_own_scanner_before_the_gate():
    """8 Sep 2026: EnerVenue and Eos Energy came from the routine, reached the pool and fell
    at the gate with "no score_breakdown from scanner". A lead is not a scored record."""
    from intel.config import Settings
    from intel.parse import ScannedSignal

    thin = inbox.as_signals(inbox.parse_routine_email(ROUTINE_BODY, RECEIVED))  # Nexeon only
    assert thin and thin[0].score_breakdown is None
    calls = []

    def fake_scan(company, today, settings=None, hint=None):
        calls.append((company, hint))
        return [
            ScannedSignal.model_validate(
                {
                    "company": "Nexeon",
                    "score": 74,
                    "signal_date": "2026-09-01",
                    "source_url": "https://x.test",
                    "trigger_reason": "£100m round",
                    "score_breakdown": {
                        "timing": 15,
                        "capacity": 15,
                        "brand_fit": 15,
                        "urgency": 14,
                        "ops_fit": 15,
                    },
                }
            )
        ]

    out, note = inbox.enrich(thin, dt.date(2026, 9, 8), Settings(), scan_fn=fake_scan)
    assert note["scanned"] == ["Nexeon"] and out[0].score_breakdown is not None
    assert calls[0][0] == "Nexeon" and "National Wealth Fund" in calls[0][1]


def test_a_failed_or_mismatched_scan_keeps_the_thin_lead_and_the_cap_holds():
    from intel.config import Settings
    from intel.parse import ScannedSignal

    a = ScannedSignal.model_validate(
        {"company": "A", "score": 70, "source_url": "https://a", "trigger_reason": "x"}
    )
    b = ScannedSignal.model_validate(
        {"company": "B", "score": 70, "source_url": "https://b", "trigger_reason": "y"}
    )
    c = ScannedSignal.model_validate(
        {"company": "C", "score": 70, "source_url": "https://c", "trigger_reason": "z"}
    )

    def scan(company, today, settings=None, hint=None):
        if company == "A":
            raise RuntimeError("boom")
        return [
            ScannedSignal.model_validate(
                {
                    "company": "Someone Else",
                    "score": 80,
                    "score_breakdown": {
                        "timing": 16,
                        "capacity": 16,
                        "brand_fit": 16,
                        "urgency": 16,
                        "ops_fit": 16,
                    },
                }
            )
        ]

    out, note = inbox.enrich(
        [a, b, c], dt.date(2026, 9, 8), Settings(inbox_scan_max=2), scan_fn=scan
    )
    assert [s.company for s in out] == ["A", "B", "C"]  # nothing lost, nothing swapped in
    assert note["kept_thin"] == ["A: RuntimeError", "B: no matching scored record"]
    assert note["scanned"] == []
    out, note = inbox.enrich([a], dt.date(2026, 9, 8), Settings(inbox_scan_max=0), scan_fn=scan)
    assert out == [a] and note == {"scanned": [], "kept_thin": []}
