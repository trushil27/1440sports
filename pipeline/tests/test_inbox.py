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
        {"subject": "1440 Routine Signals — 7 Sep 2026", "receivedDateTime": "2026-09-07T09:17:00Z",
         "body": {"content": ROUTINE_BODY}},
        {"subject": "1440 Intelligence Brief — Keyfactor — 15 Jul 2026",
         "receivedDateTime": "2026-09-07T08:00:00Z", "body": {"content": "<html>…</html>"}},
        {"subject": "1440 Intelligence Brief — Nexeon — 6 Sep 2026",  # already seen above
         "receivedDateTime": "2026-09-07T07:00:00Z", "body": {"content": "<html>…</html>"}},
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


def test_an_unreadable_mailbox_is_a_missing_source_not_a_failed_run():
    class Boom:
        sender, refresh_token, http = "d@x.test", "rt", None

        def token(self):
            raise RuntimeError("Mail.Read not consented")

    signals, note = inbox.collect(None, None, Boom())
    assert signals == [] and "unavailable" in note["status"]
    signals, note = inbox.collect(None, None, object())
    assert signals == [] and "no mailbox" in note["status"]
