import datetime
from datetime import date

import pytest

from regolith.dates import (month_to_str_int,
                            day_to_str_int,
                            find_gaps_overlaps,
                            get_dates, last_day, is_current, get_due_date)


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
        ('2020-05-01', datetime.date(2020, 5, 1)),
        (datetime.date(2020, 5, 1), datetime.date(2020, 5, 1)),
        (2020, True),
    ],
)
def test_get_due_date(input, expected):
    with pytest.raises(Exception):
        assert get_due_date(input) == expected

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
    "input,expected",
    [
        ({'year': 2020}, {'begin_date': datetime.date(2020, 1, 1),
                                'end_date': datetime.date(2020, 12, 31),
                                'date': None
                               }
         ),
        ({'year': 2020, 'month': 9},
         {'begin_date': datetime.date(2020, 9, 1),
          'end_date': datetime.date(2020, 9, 30),
          'date': None
          }
         ),
        ({'year': 2020, 'month': 'Sep', 'day': 15},
         {'begin_date': datetime.date(2020, 9, 15),
          'end_date': datetime.date(2020, 9, 15),
          'date': datetime.date(2020, 9, 15)
          }
         ),
        ({'begin_year': 2020},
         {'begin_date': datetime.date(2020, 1, 1),
          'end_date': None,
          'date': None
          }
         ),
        ({'begin_year': 2020, 'begin_month': 4},
         {'begin_date': datetime.date(2020, 4, 1),
          'end_date': None,
          'date': None
          }
         ),
        ({'begin_year': 2020, 'begin_month': 4, 'begin_day': 5},
         {'begin_date': datetime.date(2020, 4, 5),
          'end_date': None,
          'date': None
          }
         ),
        ({'begin_year': 2019, 'end_year': 2020},
         {'begin_date': datetime.date(2019, 1, 1),
          'end_date': datetime.date(2020, 12, 31),
          'date': None
          }
         ),
        ({'begin_year': 2019, 'end_year': 2020, 'end_month': 'Feb'},
         {'begin_date': datetime.date(2019, 1, 1),
          'end_date': datetime.date(2020, 2, 29),
          'date': None
          }
         ),
        ({'begin_year': 2019, 'end_year': 2020, 'end_month': 'Feb', 'end_day': 10},
         {'begin_date': datetime.date(2019, 1, 1),
          'end_date': datetime.date(2020, 2, 10),
          'date': None
          }
         ),
        ({'begin_date': '2020-05-09', 'begin_year': 2019, 'end_year': 2020, 'end_month': 'Feb',
          'end_day': 10},
         {'begin_date': datetime.date(2020, 5, 9),
          'end_date': datetime.date(2020, 2, 10),
          'date': None
          }
         ),
        ({'end_date': '2020-5-20', 'begin_year': 2019, 'end_year': 2020, 'end_month': 'Feb',
          'end_day': 10},
         {'begin_date': datetime.date(2019, 1, 1),
          'end_date': datetime.date(2020, 5, 20),
          'date': None
          }
         ),
        ({'date': '2020-5-20', 'begin_year': 2019, 'end_year': 2020,
          'end_month': 'Feb',
          'end_day': 10},
         {'begin_date': datetime.date(2019, 1, 1),
          'end_date': datetime.date(2020, 2, 10),
          'date': datetime.date(2020, 5, 20)
          }
         ),
    ],
)
def test_get_dates(input, expected):
    actual = get_dates(input)
    assert actual == expected


@pytest.mark.parametrize(
    "year,month,expected",
    [
        (2020, 2, 29),
        (2020, 'Feb', 29)
    ]
)
def test_last_day(year,month,expected):
    assert last_day(year,month) == expected

@pytest.mark.parametrize(
    "thing,date,expected",
    [
        ({'begin_day': 1, 'begin_month': 5, 'begin_year': 1950, 'end_day': 2, 'end_month': 5, 'end_year': 3000}, None, True),
        ({'begin_day': 1, 'begin_month': 5, 'begin_year': 3000, 'end_day': 2, 'end_month': 5, 'end_year': 3100}, None, False),
        ({'begin_day': 12, 'begin_month': 6, 'begin_year': 2025, 'end_day': 2, 'end_month': 5, 'end_year': 2030}, date(2026, 3, 3), True),
    ]
)
def test_is_current(thing, date, expected):
    assert is_current(thing, date) == expected