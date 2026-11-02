"""Tests for planning and checking appointments."""

import datetime as dt

import pytest

from regolith.appointments import (
    appointment_alerts,
    appointments_from_text,
    appointments_to_text,
    gap_appointments,
    is_outside,
    new_appointment_id,
    quarter_periods,
)

D = dt.date
TODAY = D(2026, 11, 1)
STUDENT = {
    "_id": "stu",
    "name": "A Student",
    "employment": [
        {
            "position": "graduate research assistant",
            "group": "bg",
            "begin_date": "2025-09-01",
            "end_date": "2027-09-30",
        },
        {
            "position": "undergraduate research assistant",
            "group": "bg",
            "begin_date": "2020-01-01",
            "end_date": "2030-01-01",
        },
    ],
}
FALL_HALF_OUTSIDE = [
    {
        "_id": "f26",
        "begin_date": D(2026, 10, 1),
        "end_date": D(2026, 12, 31),
        "type": "gra",
        "loading": 0.5,
        "outside_funding": "NSF GRFP",
    },
    {
        "_id": "f26-2",
        "begin_date": D(2026, 10, 1),
        "end_date": D(2026, 12, 31),
        "type": "gra",
        "loading": 0.5,
        "grant": "g1",
    },
]
GRANT = {
    "_id": "g1",
    "alias": "grant1",
    "begin_date": "2025-01-01",
    "end_date": "2027-03-31",
    "budget": [{"begin_date": "2025-01-01", "end_date": "2027-03-31", "student_months": 2}],
}


# Test splitting a stretch of time into appointment quarters, with the summer from July to September
@pytest.mark.parametrize(
    "begin_date, end_date, expected_periods",
    [
        # C1: whole quarters across a new year, expect each quarter with its id
        pytest.param(
            D(2026, 10, 1),
            D(2027, 9, 30),
            [
                (D(2026, 10, 1), D(2026, 12, 31), "f26"),
                (D(2027, 1, 1), D(2027, 3, 31), "w27"),
                (D(2027, 4, 1), D(2027, 6, 30), "s27"),
                (D(2027, 7, 1), D(2027, 9, 30), "ss27"),
            ],
            id="whole-quarters",
        ),
        # C2: dates part way through quarters, expect the first and last quarters cut to them
        pytest.param(
            D(2026, 11, 15),
            D(2027, 2, 10),
            [(D(2026, 11, 15), D(2026, 12, 31), "f26"), (D(2027, 1, 1), D(2027, 2, 10), "w27")],
            id="part-quarters",
        ),
    ],
)
def test_quarter_periods(begin_date, end_date, expected_periods):
    assert quarter_periods(begin_date, end_date) == expected_periods


# Test recognising appointments paid by outside funding
@pytest.mark.parametrize(
    "appointment, expected_outside",
    [
        # C1: outside_funding given, expect outside
        pytest.param({"outside_funding": "NSF GRFP"}, True, id="outside-funding"),
        # C2: a grant that once stood for outside funding, expect outside
        pytest.param({"grant": "ta"}, True, id="legacy-grant"),
        # C3: a real grant, expect not outside
        pytest.param({"grant": "dmref15"}, False, id="grant"),
    ],
)
def test_is_outside(appointment, expected_outside):
    assert is_outside(appointment) == expected_outside


# Test filling the gaps in a person's funding, quarter by quarter, until their funded position ends
@pytest.mark.parametrize(
    "appointments, expected_gaps",
    [
        # C1: the fall fully appointed, half on outside funding, expect the winter and spring filled as gra
        # and the summer as ss, all on future_grant
        pytest.param(
            FALL_HALF_OUTSIDE,
            [
                (D(2027, 1, 1), D(2027, 3, 31), "gra", 1.0),
                (D(2027, 4, 1), D(2027, 6, 30), "gra", 1.0),
                (D(2027, 7, 1), D(2027, 9, 30), "ss", 1.0),
            ],
            id="after-fall",
        ),
        # C2: only half of the fall appointed, expect the other half of the fall filled too
        pytest.param(
            FALL_HALF_OUTSIDE[:1],
            [
                (D(2026, 11, 1), D(2026, 12, 31), "gra", 0.5),
                (D(2027, 1, 1), D(2027, 3, 31), "gra", 1.0),
                (D(2027, 4, 1), D(2027, 6, 30), "gra", 1.0),
                (D(2027, 7, 1), D(2027, 9, 30), "ss", 1.0),
            ],
            id="half-fall",
        ),
    ],
)
def test_gap_appointments(appointments, expected_gaps):
    gaps = gap_appointments(STUDENT, appointments, "bg", TODAY)
    assert [(g["begin_date"], g["end_date"], g["type"], g["loading"]) for g in gaps] == expected_gaps
    assert {(g["grant"], g["status"]) for g in gaps} == {("future_grant", "proposed")}


# Test that a plan stops at its horizon when a position ends later, such as at a placeholder date
@pytest.mark.parametrize(
    "until, expected_last_day",
    [
        # C1: no horizon given, expect the plan to stop five years from today
        pytest.param(None, D(2031, 10, 31), id="default"),
        # C2: a horizon given, expect the plan to stop there
        pytest.param(D(2027, 6, 30), D(2027, 6, 30), id="until"),
    ],
)
def test_gap_appointments_horizon(until, expected_last_day):
    person = {
        "_id": "p",
        "employment": [
            {
                "position": "graduate research assistant",
                "group": "bg",
                "begin_date": "2026-01-01",
                "end_date": "2100-12-31",
            }
        ],
    }
    gaps = gap_appointments(person, [], "bg", TODAY, until)
    assert max(gap["end_date"] for gap in gaps) == expected_last_day
    alerts = appointment_alerts(person, [], [], [], "bg", TODAY, until)
    assert alerts == [f"There is a gap in the appointments from 2026-11-01 to {expected_last_day}."]


# Test giving a new appointment an id from the quarter it begins in
@pytest.mark.parametrize(
    "begin_date, taken_ids, expected_id",
    [
        # C1: a free quarter id, expect it
        pytest.param("2027-07-01", set(), "ss27", id="free"),
        # C2: the quarter id taken twice, expect the next number
        pytest.param("2027-01-15", {"w27", "w27-2"}, "w27-3", id="taken"),
    ],
)
def test_new_appointment_id(begin_date, taken_ids, expected_id):
    assert new_appointment_id({"begin_date": begin_date}, taken_ids) == expected_id


# Test that appointments written out for editing read back as they were, with status defaulting to proposed
def test_appointments_round_trip():
    appointments = [
        {**FALL_HALF_OUTSIDE[0], "status": "appointed", "notes": ["renewed: yes"]},
        {"begin_date": D(2027, 1, 1), "end_date": D(2027, 3, 31), "type": "gra", "loading": 1.0, "grant": "g1"},
    ]
    text = appointments_to_text(STUDENT, appointments, D(2027, 9, 30), ["an alert"])
    assert "# ALERT: an alert" in text
    expected_appointments = [appointments[0], {**appointments[1], "status": "proposed"}]
    assert appointments_from_text(text) == (expected_appointments, [])


# Test that every problem in edited appointments is reported together, so they can be fixed in one go
@pytest.mark.parametrize(
    "text, expected_problems",
    [
        # C1: 1. a bad date, 2. a bad type, 3. a loading over 1, 4. nothing paying and 5. an unknown field,
        # expect all five reported
        pytest.param(
            "- begin_date: 2027-13-01\n  end_date: 2027-03-31\n  type: xx\n  loading: 2\n  rate: 3\n",
            [
                "Entry 1 has the begin_date 2027-13-01, which is not a YYYY-MM-DD date.",
                "Entry 1 has the type xx. It must be one of gra, ss, pd, ug.",
                "Entry 1 has the loading 2. It must be above 0 and at most 1.",
                "Entry 1 says nothing about what pays for it.",
                "Entry 1 has rate, which an appointment cannot hold.",
            ],
            id="field-problems",
        ),
        # C2: 1. both a grant and outside funding, 2. dates the wrong way round and 3. a repeated id, expect
        # all three reported
        pytest.param(
            "- _id: a\n  begin_date: 2027-03-31\n  end_date: 2027-01-01\n  type: gra\n  loading: 1\n"
            "  grant: g1\n  outside_funding: TA\n"
            "- _id: a\n  begin_date: 2027-04-01\n  end_date: 2027-06-30\n  type: gra\n  loading: 1\n  grant: g1\n",
            [
                "Entry 1 (a) has both a grant and outside_funding.",
                "Entry 1 (a) begins on 2027-03-31, after it ends on 2027-01-01.",
                "Entry 2 (a) has the same _id as an earlier entry.",
            ],
            id="entry-problems",
        ),
    ],
)
def test_appointments_from_text_problems(text, expected_problems):
    _, problems = appointments_from_text(text)
    assert len(problems) == len(expected_problems)
    for problem, expected_problem in zip(problems, expected_problems):
        assert problem.startswith(expected_problem)


# Test the alerts about a person's appointments from today on
@pytest.mark.parametrize(
    "appointments, expected_alerts",
    [
        # C1: a fall half on outside funding and half on a grant that has the money, then nothing, expect
        # only the gap reported
        pytest.param(
            FALL_HALF_OUTSIDE,
            ["There is a gap in the appointments from 2027-01-01 to 2027-09-30."],
            id="gap",
        ),
        # C2: the winter and spring on the grant, which ends in March and has too little money, and a summer
        # not yet funded, expect the grant ending, the money running out and the unfunded summer reported
        pytest.param(
            FALL_HALF_OUTSIDE
            + [
                {
                    "_id": "w27",
                    "begin_date": D(2027, 1, 1),
                    "end_date": D(2027, 6, 30),
                    "type": "gra",
                    "loading": 1.0,
                    "grant": "GRANT1",
                },
                {
                    "_id": "ss27",
                    "begin_date": D(2027, 7, 1),
                    "end_date": D(2027, 9, 30),
                    "type": "ss",
                    "loading": 1.0,
                    "grant": "future_grant",
                },
            ],
            [
                "w27 (2027-01-01 to 2027-06-30) runs past the end of the grant GRANT1 on 2027-03-31.",
                "The grant GRANT1 runs out of student months on 2027-01-",
                "ss27 (2027-07-01 to 2027-09-30) is not yet funded.",
            ],
            id="grant-problems",
        ),
        # C3: two full-time appointments at once, one on a grant with two months of students, expect more than
        # full time and the money running out reported
        pytest.param(
            [{**FALL_HALF_OUTSIDE[0], "loading": 1.0}, {**FALL_HALF_OUTSIDE[1], "loading": 1.0}],
            [
                "The grant g1 runs out of student months on 2026-12-06, during f26-2",
                "There is a gap in the appointments from 2027-01-01 to 2027-09-30.",
                "The appointments add up to more than full time from 2026-11-01 to 2026-12-31.",
            ],
            id="over-full-time",
        ),
    ],
)
def test_appointment_alerts(appointments, expected_alerts):
    alerts = appointment_alerts(STUDENT, appointments, [GRANT], appointments, "bg", TODAY)
    assert len(alerts) == len(expected_alerts)
    for alert, expected_alert in zip(alerts, expected_alerts):
        assert alert.startswith(expected_alert)


# Test that a funded position with no end date is reported, since the gaps until it ends cannot be found
def test_appointment_alerts_no_end_date():
    person = {
        "_id": "pd",
        "employment": [{"position": "Post-Doctoral Scholar", "group": "bg", "begin_date": "2026-01-01"}],
    }
    alerts = appointment_alerts(person, [], [], [], "bg", TODAY)
    assert alerts == [
        "The post-doctoral scholar position has no end date in employment, so gaps cannot be found. "
        "Please add the date they are expected to graduate or leave."
    ]
