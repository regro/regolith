from datetime import date

import pytest

from regolith.dates import (month_to_str_int,
                            day_to_str_int,
                            find_gaps_overlaps)


@pytest.mark.parametrize(
    "input,expected",
    [
        (1, "01"),
        (10, "10"),
        ("Oct", "10"),
        ("Jan", "01"),
    ],
)
def test_month_to_str(input, expected):
    assert month_to_str_int(input) == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        (1, "01"),
        (10, "10"),
    ],
)
def test_day_to_str(input, expected):
    assert day_to_str_int(input) == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        ([(date(2020, 1, 1), date(2020, 1, 31)),
         (date(2020, 2, 1), date(2020, 2, 5))], True),
        ([(date(2020, 1, 1), date(2020, 1, 31)),
         (date(2020, 2, 2), date(2020, 2, 5))], False),
        ([(date(2020, 1, 1), date(2020, 1, 31)),
         (date(2020, 1, 31), date(2020, 2, 5))], False),
        ([(date(2020, 1, 1), date(2020, 1, 31)),
         (date(2020, 2, 1), date(2020, 2, 5)),
         (date(2020, 2, 6), date(2020, 2, 7))], True),
        ([(date(2020, 1, 1), date(2020, 1, 31)),
         (date(2020, 2, 1), date(2020, 2, 5)),
         (date(2020, 2, 7), date(2020, 2, 7))], False)
    ],
)
def test_find_gaps_overlaps(input, expected):
    actual = find_gaps_overlaps(input)
    assert actual == expected
