from datetime import date

import pytest

from regolith.dates import (month_to_str_int,
                            day_to_str_int,
                            find_gaps_overlaps,
                            get_dates)


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
    "input,flag,expected",
    [
        ([(date(2020, 1, 1), date(2020, 1, 31)),
         (date(2020, 2, 1), date(2020, 2, 5))], False, True),
        ([(date(2020, 2, 1), date(2020, 2, 5)),
         (date(2020, 1, 1), date(2020, 1, 31))], False, True),
        ([(date(2020, 1, 1), date(2020, 1, 31)),
         (date(2020, 2, 2), date(2020, 2, 5))], False, False),
        ([(date(2020, 1, 1), date(2020, 1, 31)),
         (date(2020, 1, 31), date(2020, 2, 5))], False, False),
        ([(date(2020, 1, 1), date(2020, 1, 31)),
         (date(2020, 1, 31), date(2020, 2, 5))], True, True),
        ([(date(2020, 1, 1), date(2020, 1, 31)),
         (date(2020, 2, 1), date(2020, 2, 5)),
         (date(2020, 2, 6), date(2020, 2, 7))], False, True),
        ([(date(2020, 1, 1), date(2020, 1, 31)),
         (date(2020, 2, 1), date(2020, 2, 5)),
         (date(2020, 2, 7), date(2020, 2, 7))], False, False)
    ],
)
def test_find_gaps_overlaps(input, flag, expected):
    actual = find_gaps_overlaps(input, overlaps_ok=flag)
    assert actual == expected

@pytest.mark.parametrize(
    "input,flag,expected",
    [({'year': 2020}, True, {'begin_day': 1, 'begin_month': 1, 'begin_year': 2020,
                 'end_day': None, 'end_month': 12,
                 'end_year': None, 'day': 1, 'month': 1,
                 'year': 2020})
#        ({"begin_year": 2019, "end_year": 2020}),
    ],
)
def test_get_dates(input, flag, expected):
    actual = get_dates(input,valid_date=flag)
    print(actual)
    assert False