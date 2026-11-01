"""Tests for making, showing and reading back grant budgets."""

import datetime as dt

import pytest

from regolith.grant_budget import (
    budget_from_text,
    budget_notes,
    budget_to_text,
    editor_command,
    make_budget,
    yearly_periods,
)

D = dt.date


# Test splitting a grant into grant years that start on the anniversary of its begin date
@pytest.mark.parametrize(
    "begin_date, end_date, expected_periods",
    [
        # C1: a grant of exactly two years, expect two full years
        pytest.param(
            D(2026, 9, 1),
            D(2028, 8, 31),
            [(D(2026, 9, 1), D(2027, 8, 31)), (D(2027, 9, 1), D(2028, 8, 31))],
            id="whole-years",
        ),
        # C2: a grant ending part way through its second year, expect a short last year
        pytest.param(
            D(2026, 9, 1),
            D(2027, 12, 31),
            [(D(2026, 9, 1), D(2027, 8, 31)), (D(2027, 9, 1), D(2027, 12, 31))],
            id="short-last-year",
        ),
        # C3: a grant shorter than a year, expect one period covering it
        pytest.param(D(2026, 9, 1), D(2026, 12, 31), [(D(2026, 9, 1), D(2026, 12, 31))], id="under-a-year"),
    ],
)
def test_yearly_periods(begin_date, end_date, expected_periods):
    assert yearly_periods(begin_date, end_date) == expected_periods


# Test making a yearly budget from the grant amount or from an amount for each year
@pytest.mark.parametrize(
    "amount, annual_amounts, expected_amounts",
    [
        # C1: annual amounts, expect each year to have its own
        pytest.param(None, [100, 200], [100.0, 200.0], id="annual"),
        # C2: a total and a short second year, expect the total shared by length and adding up exactly
        pytest.param(1000, None, [800.0, 200.0], id="shared-by-length"),
        # C3: neither, expect periods with no amount
        pytest.param(None, None, [None, None], id="no-amounts"),
    ],
)
def test_make_budget(amount, annual_amounts, expected_amounts):
    budget = make_budget(D(2026, 9, 1), D(2027, 11, 30), amount=amount, annual_amounts=annual_amounts)
    assert [period.get("amount") for period in budget] == expected_amounts
    assert [period["begin_date"] for period in budget] == [D(2026, 9, 1), D(2027, 9, 1)]


# Test that the wrong number of annual amounts is refused with the number of years the grant has
def test_make_budget_wrong_number_of_amounts():
    with pytest.raises(ValueError, match="which is 2 budget years. Please give one amount for each year."):
        make_budget(D(2026, 9, 1), D(2028, 8, 31), annual_amounts=[1, 2, 3])


# Test that a budget written out for editing reads back unchanged
def test_budget_round_trip():
    budget = [
        {"begin_date": D(2026, 9, 1), "end_date": D(2027, 8, 31), "amount": 100.0, "student_months": 12.0},
        {"begin_date": D(2027, 9, 1), "end_date": D(2028, 8, 31), "amount": 200.5, "ss_months": 1.0},
    ]
    text = budget_to_text("g1", budget, (D(2026, 9, 1), D(2028, 8, 31)), 300.5)
    assert "# The grant runs from 2026-09-01 to 2028-08-31." in text
    assert budget_from_text(text) == (budget, [])


# Test that every problem in an edited budget is reported together, so they can be fixed in one go
@pytest.mark.parametrize(
    "text, expected_problems",
    [
        # C1: 1. a missing end date, 2. a date that is not a date, 3. an amount that is not a number and
        # 4. an unknown field, expect all four reported
        pytest.param(
            "- begin_date: 2026-09-01\n  amount: lots\n  overhead: 3\n"
            "- begin_date: 2027-13-01\n  end_date: 2028-08-31\n",
            [
                "Period 1 has no end_date.",
                "Period 1 has the amount lots, which is not a number.",
                "Period 1 has overhead, which a budget period cannot hold. The fields allowed are begin_date, "
                "end_date, amount, student_months, postdoc_months, ss_months.",
                "Period 2 has the begin_date 2027-13-01, which is not a YYYY-MM-DD date.",
            ],
            id="field-problems",
        ),
        # C2: a period ending before it begins, and the next overlapping it, expect both reported
        pytest.param(
            "- begin_date: 2027-09-01\n  end_date: 2027-08-31\n- begin_date: 2027-08-01\n  end_date: 2028-08-31\n",
            [
                "Period 1 begins on 2027-09-01, after it ends on 2027-08-31.",
                "Period 2 begins on 2027-08-01, before period 1 ends on 2027-08-31. The periods must be in order "
                "and must not overlap.",
            ],
            id="date-order",
        ),
        # C3: something that is not a list of periods, expect a message saying what it should be
        pytest.param(
            "begin_date: 2026-09-01\n",
            ["The budget must be a list of periods, each starting with '- begin_date:'."],
            id="not-a-list",
        ),
        # C4: text that is not YAML, expect a message saying it could not be read
        pytest.param("- begin_date: [2026\n", ["The budget could not be read as YAML"], id="not-yaml"),
    ],
)
def test_budget_from_text_problems(text, expected_problems):
    _, problems = budget_from_text(text)
    assert len(problems) == len(expected_problems)
    for problem, expected_problem in zip(problems, expected_problems):
        assert problem.startswith(expected_problem)


# Test the differences between a good budget and its grant that are worth a look
@pytest.mark.parametrize(
    "grant_amount, grant_dates, expected_notes",
    [
        # C1: a budget matching its grant, expect no notes
        pytest.param(300.0, (D(2026, 9, 1), D(2028, 8, 31)), [], id="matching"),
        # C2: 1. a different amount and 2. a later end date, expect both noted
        pytest.param(
            400.0,
            (D(2026, 9, 1), D(2028, 12, 31)),
            [
                "The periods add up to 300.00, but the grant amount is 400.00.",
                "The last period ends on 2028-08-31, not on the grant's 2028-12-31.",
            ],
            id="different",
        ),
    ],
)
def test_budget_notes(grant_amount, grant_dates, expected_notes):
    budget = make_budget(D(2026, 9, 1), D(2028, 8, 31), annual_amounts=[100, 200])
    assert budget_notes(budget, grant_dates, grant_amount) == expected_notes


# Test choosing the text editor from the environment
@pytest.mark.parametrize(
    "environment, expected_command",
    [
        # C1: VISUAL and EDITOR both set, expect VISUAL
        pytest.param({"VISUAL": "code --wait", "EDITOR": "vim"}, ["code", "--wait"], id="visual"),
        # C2: only EDITOR set, expect EDITOR
        pytest.param({"EDITOR": "vim"}, ["vim"], id="editor"),
    ],
)
def test_editor_command(environment, expected_command, monkeypatch):
    for name in ("VISUAL", "EDITOR"):
        monkeypatch.delenv(name, raising=False)
    for name, value in environment.items():
        monkeypatch.setenv(name, value)
    assert editor_command() == expected_command
