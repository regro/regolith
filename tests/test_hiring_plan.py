"""Tests for working out how many students and postdocs the grants can
support."""

import datetime as dt
import json
import os

import pytest

from regolith.fsclient import dump_yaml
from regolith.hiring_plan import (
    evaluate_plans,
    expected_new_funding,
    grant_supplies,
    hire_needs,
    is_federal,
    month_starts,
    monthly_loading,
    simulate,
)
from regolith.main import main

D = dt.date


def supply(grant_id, end_date, balance, extended_end=None, additions=None):
    return {
        "_id": grant_id,
        "alias": grant_id,
        "end_date": end_date,
        "extended_end": extended_end or end_date,
        "balance": balance,
        "additions": additions or {},
    }


# Test recognising funders whose grants normally get a no-cost extension
@pytest.mark.parametrize(
    "funder, expected_federal",
    [
        # C1: a federal agency and its division, expect federal
        pytest.param("NSF-DMR", True, id="nsf-division"),
        # C2: a federal agency spelled out, expect federal
        pytest.param("Department of Energy", True, id="spelled-out"),
        # C3: a university, expect not federal
        pytest.param("Columbia University", False, id="university"),
        # C4: a word that begins like an agency, expect not federal
        pytest.param("DOEsomething Foundation", False, id="lookalike"),
    ],
)
def test_is_federal(funder, expected_federal):
    assert is_federal({"funder": funder}) == expected_federal


# Test the months of support needed in each month, including part months
def test_monthly_loading():
    needs = monthly_loading(D(2027, 1, 16), D(2027, 3, 31), 0.5)
    assert {month: round(value, 3) for month, value in needs.items()} == {
        D(2027, 1, 1): round(16 * 0.5 / 30.5, 3),
        D(2027, 2, 1): round(28 * 0.5 / 30.5, 3),
        D(2027, 3, 1): round(31 * 0.5 / 30.5, 3),
    }


# Test that a student staying 4.5 years needs 54 months of support from the month they start
def test_hire_needs():
    needs = hire_needs(2, D(2027, 10, 1), 4.5)
    assert min(needs) == D(2027, 10, 1) and max(needs) == D(2032, 3, 1)
    assert round(sum(needs.values())) == 2 * 54


# Test paying the months needed from the grants
@pytest.mark.parametrize(
    "supplies, pinned, expected_paid, expected_unpaid, expected_extension, expected_lost",
    [
        # C1: two grants with money and one person a month, expect the grant ending first paid from first, and
        # the other's money left over lost when it ends
        pytest.param(
            [supply("late", D(2027, 4, 30), 3.0), supply("early", D(2027, 2, 28), 1.0)],
            {},
            {"early": 1.0, "late": 3.0},
            0.0,
            {},
            {"early": 0.0, "late": 0.0},
            id="soonest-first",
        ),
        # C2: an appointment on the later grant, expect it paid from that grant, leaving less for the others
        pytest.param(
            [supply("late", D(2027, 4, 30), 3.0), supply("early", D(2027, 2, 28), 1.0)],
            {"late": {D(2027, 1, 1): 1.0}},
            {"early": 1.0, "late": 3.0},
            1.0,
            {},
            {"early": 0.0, "late": 0.0},
            id="pinned",
        ),
        # C3: a grant whose extension year is needed, expect its money spent in the extension and counted
        pytest.param(
            [supply("ext", D(2027, 2, 28), 4.0, extended_end=D(2028, 2, 29))],
            {},
            {"ext": 4.0},
            0.0,
            {"ext": 2.0},
            {},
            id="extension",
        ),
    ],
)
def test_simulate(supplies, pinned, expected_paid, expected_unpaid, expected_extension, expected_lost):
    months = month_starts(D(2027, 1, 1), D(2027, 4, 30))
    result = simulate(supplies, pinned, {month: 1.0 for month in months}, months)
    assert {grant_id: round(sum(paid.values()), 6) for grant_id, paid in result["paid"].items()} == expected_paid
    assert round(sum(result["unpaid"].values()), 6) == expected_unpaid
    assert {grant_id: round(value, 6) for grant_id, value in result["extension"].items()} == expected_extension
    assert {grant_id: round(value, 6) for grant_id, value in result["lost"].items()} == expected_lost


# Test that a grant's months left at the start of the plan, and those its later periods add, are found
def test_grant_supplies():
    grant = {
        "_id": "g1",
        "funder": "NSF",
        "begin_date": "2026-01-01",
        "end_date": "2027-12-31",
        "budget": [
            {"begin_date": "2026-01-01", "end_date": "2026-12-31", "student_months": 12},
            {"begin_date": "2027-01-01", "end_date": "2027-12-31", "postdoc_months": 6, "ss_months": 2},
        ],
    }
    appointments = [
        {"grant": "g1", "type": "gra", "loading": 1.0, "begin_date": "2026-01-01", "end_date": "2026-06-30"}
    ]
    supplies, unreadable = grant_supplies([grant], appointments, D(2026, 12, 1))
    assert unreadable == []
    assert round(supplies[0]["balance"], 1) == round(12 - 181 / 30.5, 1)
    assert supplies[0]["additions"] == {D(2027, 1, 1): 8.0}
    assert supplies[0]["extended_end"] == D(2028, 12, 31)


# Test the new funding expected each month
def test_expected_new_funding():
    months = month_starts(D(2027, 1, 1), D(2027, 12, 31))
    proposal = {"status": "pending", "amount": 100000, "begin_date": "2027-07-01", "end_date": "2027-12-31"}
    declined = {**proposal, "status": "declined"}
    expected = expected_new_funding([proposal, declined], 0.5, 1 / 10000, months, flat_per_year=12)
    assert round(expected[D(2027, 1, 1)], 6) == 1.0
    assert round(sum(expected.values()), 6) == 12 + 5.0


# Test that the suggested plan is the most hires the expected new funding keeps up with, month by month
def test_evaluate_plans():
    months = month_starts(D(2027, 1, 1), D(2028, 12, 31))
    supplies = [supply("g1", D(2028, 12, 31), 12.0)]
    hires = {
        "students": {"most": 2, "start": D(2027, 1, 1), "years": 2},
        "postdocs": {"most": 1, "start": D(2027, 1, 1), "years": 1},
    }
    expected = {month: 0.5 for month in months}
    plans = evaluate_plans(supplies, {}, {}, months, expected, hires)
    suggested = plans[0]
    assert (suggested["students"], suggested["postdocs"]) == (1, 0)
    assert suggested["covered"] and suggested["lost"] == 0
    # Two students use the grant's 12 months by June 2027, and then need 2 months a month against the 0.5 a
    # month expected since January, so by September 6 months are unpaid against 4.5 expected
    too_many = next(plan for plan in plans if (plan["students"], plan["postdocs"]) == (2, 0))
    assert not too_many["covered"] and too_many["first_short"] == D(2027, 9, 1)


@pytest.fixture
def hiring_db(tmp_path):
    cwd = os.getcwd()
    rc = {
        "groupname": "The Group",
        "databases": [
            {
                "name": "test",
                "url": str(tmp_path),
                "public": False,
                "path": "db",
                "local": True,
                "backend": "filesystem",
            }
        ],
    }
    (tmp_path / "regolithrc.json").write_text(json.dumps(rc))
    (tmp_path / "db").mkdir()
    collections = {
        "groups": {"grp": {"_id": "grp", "name": "Group", "aka": ["The Group"]}},
        "grants": {
            "g1": {
                "_id": "g1",
                "alias": "big",
                "funder": "NSF",
                "amount": 500000.0,
                "begin_date": "2026-01-01",
                "end_date": "2030-12-31",
                "budget": [{"begin_date": "2026-01-01", "end_date": "2030-12-31", "student_months": 120}],
            },
        },
        "proposals": {},
        "people": {
            "stu": {
                "_id": "stu",
                "name": "A Student",
                "employment": [
                    {
                        "position": "graduate research assistant",
                        "group": "grp",
                        "begin_date": "2025-09-01",
                        "end_date": "2028-08-31",
                    }
                ],
            },
        },
    }
    for name, documents in collections.items():
        dump_yaml(str(tmp_path / "db" / f"{name}.yaml"), documents)
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(cwd)


# Test the hiring plan for a group with one grant and one current student
def test_l_hiringplan(hiring_db, capsys):
    main(["helper", "l_hiringplan", "--date", "2026-11-01", "--students-most", "2", "--postdocs-most", "1"])
    output = capsys.readouterr().out
    assert "new students start 2027-10-01 for 4.5 years; new postdocs start 2027-03-01 for 2 years" in output
    assert "assumed to get a one-year no-cost extension: big" in output
    assert "Suggested plan:" in output
    assert "big" in output.split("months paid each year:")[1]
