import datetime
from datetime import date

import pytest

from regolith.dates import (month_to_str_int,
                            day_to_str_int,
                            find_gaps_overlaps,
                            get_dates, last_day,
                            is_current, get_due_date,
                            has_started, has_finished,
                            is_before, is_after,
                            is_between)

TEST_DATE = date(2019, 6, 15)
TEST_START_DATE = date(2019, 1, 1)
TEST_END_DATE = date(2019, 2, 5)


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


import datetime
from regolith.dates import date_to_float, month_to_int


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
        ('Jan', 1),
        (1, 1),
        ('February', 2)
    ],
)
def test_month_to_int(input, expected):
    assert month_to_int(input) == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        ([2019, 1, 15], 2019.0115),
        ([2019, 'May', 0], 2019.05),
        ([2019, 'February', 2], 2019.0202)
    ],
)
def test_date_to_float(input, expected):
    assert date_to_float(input[0], input[1], d=input[2]) == expected


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
        (({'year': 2020}, None), {'begin_date': datetime.date(2020, 1, 1),
                                  'end_date': datetime.date(2020, 12, 31)
                                  }
         ),
        (({'year': 2020, 'month': 9}, None), {'begin_date': datetime.date(2020, 9, 1),
                                              'end_date': datetime.date(2020, 9, 30)
                                              }
         ),
        (({}, None), {}
         ),
        (({'year': 'tbd', 'month': 9}, None),
         {}
         ),
        (({'year': 2019, 'month': 'tbd'}, None),
         {'begin_date': datetime.date(2019, 1, 1),
          'end_date': datetime.date(2019, 12, 31)
          }
         ),
        (({'year': 2020, 'month': 9}, None),
         {'begin_date': datetime.date(2020, 9, 1),
          'end_date': datetime.date(2020, 9, 30)
          }
         ),
        (({'year': 2020, 'month': 'Sep', 'day': 15}, None),
         {'begin_date': datetime.date(2020, 9, 15),
          'end_date': datetime.date(2020, 9, 15),
          'date': datetime.date(2020, 9, 15)
          }
         ),
        (({'begin_year': 2020}, None),
         {'begin_date': datetime.date(2020, 1, 1)
          }
         ),
        (({'begin_year': 2020, 'begin_month': 4}, None),
         {'begin_date': datetime.date(2020, 4, 1)
          }
         ),
        (({'begin_year': 2020, 'begin_month': 4, 'begin_day': 5}, None),
         {'begin_date': datetime.date(2020, 4, 5)
          }
         ),
        (({'begin_year': '2020', 'begin_month': '4', 'begin_day': '5'}, None),
         {'begin_date': datetime.date(2020, 4, 5)
          }
         ),
        (({'begin_year': 2019, 'end_year': 2020}, None),
         {'begin_date': datetime.date(2019, 1, 1),
          'end_date': datetime.date(2020, 12, 31)
          }
         ),
        (({'begin_year': 2019, 'end_year': 2020, 'end_month': 'Feb'}, None),
         {'begin_date': datetime.date(2019, 1, 1),
          'end_date': datetime.date(2020, 2, 29)
          }
         ),
        (({'begin_year': 2019, 'end_year': 2020, 'end_month': 'Feb', 'end_day': 10}, None),
         {'begin_date': datetime.date(2019, 1, 1),
          'end_date': datetime.date(2020, 2, 10)
          }
         ),
        (({'begin_date': '2020-05-09', 'begin_year': 2019, 'end_year': 2020, 'end_month': 'Feb',
           'end_day': 10}, None),
         {'begin_date': datetime.date(2020, 5, 9),
          'end_date': datetime.date(2020, 2, 10)
          }
         ),
        (({'end_date': '2020-5-20', 'begin_year': 2019, 'end_year': 2020, 'end_month': 'Feb',
           'end_day': 10}, None),
         {'begin_date': datetime.date(2019, 1, 1),
          'end_date': datetime.date(2020, 5, 20)
          }
         ),
        (({'date': '2020-5-20', 'begin_year': 2019, 'end_year': 2020,
           'end_month': 'Feb',
           'end_day': 10}, None),
         {'begin_date': datetime.date(2019, 1, 1),
          'end_date': datetime.date(2020, 2, 10),
          'date': datetime.date(2020, 5, 20)
          }
         ),
        (({'date': datetime.date(2020, 5, 20), 'begin_year': 2019, 'end_year': 2020,
           'end_month': 'Feb',
           'end_day': 10}, None),
         {'begin_date': datetime.date(2019, 1, 1),
          'end_date': datetime.date(2020, 2, 10),
          'date': datetime.date(2020, 5, 20)
          }
         ),
        (({'date': datetime.date(2020, 5, 20), 'begin_date': datetime.date(2015, 6, 8),
           'end_date': datetime.date(2025, 10, 4)}, None),
         {'begin_date': datetime.date(2015, 6, 8),
          'end_date': datetime.date(2025, 10, 4),
          'date': datetime.date(2020, 5, 20)
          }
         ),
        (({'submission_day': 10, 'submission_year': 2020,
           'submission_month': 'Feb'}, "submission"),
         {'begin_date': datetime.date(2020, 2, 10),
          'end_date': datetime.date(2020, 2, 10),
          'submission_date': datetime.date(2020, 2, 10),
          'date': datetime.date(2020, 2, 10)
          }
         ),
        (({'year': 2020, 'submission_year': 2019}, "submission"), {'begin_date': datetime.date(2019, 1, 1),
                                                                   'end_date': datetime.date(2019, 12, 31)
                                                                   }
         ),
    ],
)
def test_get_dates(input, expected):
    actual = get_dates(input[0], input[1])
    assert actual == expected


@pytest.mark.parametrize(
    "year,month,expected",
    [
        (2020, 2, 29),
        (2020, 'Feb', 29)
    ]
)
def test_last_day(year, month, expected):
    assert last_day(year, month) == expected


@pytest.mark.parametrize(
    "thing,expected",
    [
        ({"begin_date": '2020-01-01', "end_date": '2020-12-31'}, False),
        ({"begin_date": '2019-01-01', "end_date": '2020-12-31'}, True),
        ({"begin_date": '2019-01-01'}, True),
        ({"begin_year": 2018}, True),
        ({"begin_year": 2019}, True),
        ({"begin_year": 2020}, False),
        ({"begin_year": 2019, "begin_month": "Apr"}, True),
        ({"begin_year": 2019, "begin_month": "Jun"}, True),
        ({"begin_year": 2019, "begin_month": "Jul"}, False),
        ({"begin_year": 2019, "begin_month": "Jun", "begin_day": 14}, True),
        ({"begin_year": 2019, "begin_month": "Jun", "begin_day": 15}, True),
        ({"begin_year": 2019, "begin_month": "Jun", "begin_day": 16}, False),
        ({"year": 2018}, False),
        ({"year": 2019}, True),
        ({"year": 2020}, False),
        ({"year": 2019, "month": "Apr"}, False),
        ({"year": 2019, "month": "Jun"}, True),
        ({"year": 2019, "month": "Jul"}, False),
        ({"year": 2019, "month": "Jun", "day": 14}, False),
        ({"year": 2019, "month": "Jun", "day": 15}, True),
        ({"year": 2019, "month": "Jun", "day": 16}, False),
    ]
)
def test_is_current(thing, expected, now=TEST_DATE):
    assert is_current(thing, now=now) == expected


@pytest.mark.parametrize(
    "thing,expected",
    [
        ({"begin_date": '2020-01-01', "end_date": '2020-12-31'}, False),
        ({"begin_date": '2019-01-01', "end_date": '2020-12-31'}, True),
        ({"begin_date": '2019-01-01'}, True),
        ({"begin_year": 2018}, True),
        ({"begin_year": 2019}, True),
        ({"begin_year": 2020}, False),
        ({"begin_year": 2019, "begin_month": "Apr"}, True),
        ({"begin_year": 2019, "begin_month": "Jun"}, True),
        ({"begin_year": 2019, "begin_month": "Jul"}, False),
        ({"begin_year": 2019, "begin_month": "Jun", "begin_day": 14}, True),
        ({"begin_year": 2019, "begin_month": "Jun", "begin_day": 15}, True),
        ({"begin_year": 2019, "begin_month": "Jun", "begin_day": 16}, False),
        ({"year": 2018}, True),
        ({"year": 2019}, True),
        ({"year": 2020}, False),
        ({"year": 2019, "month": "Apr"}, True),
        ({"year": 2019, "month": "Jun"}, True),
        ({"year": 2019, "month": "Jul"}, False),
        ({"year": 2019, "month": "Jun", "day": 14}, True),
        ({"year": 2019, "month": "Jun", "day": 15}, True),
        ({"year": 2019, "month": "Jun", "day": 16}, False),
    ]
)
def test_has_started(thing, expected, now=TEST_DATE):
    assert has_started(thing, now=now) == expected


@pytest.mark.parametrize(
    "thing,expected",
    [
        ({"begin_date": '2020-01-01', "end_date": '2020-12-31'}, False),
        ({"begin_date": '2019-01-01', "end_date": '2019-06-15'}, False),
        ({"begin_date": '2019-01-01'}, False),
        ({"begin_year": 2018}, False),
        ({"begin_year": 2019}, False),
        ({"begin_year": 2020}, False),
        ({"begin_year": 2019, "begin_month": "Apr"}, False),
        ({"begin_year": 2019, "begin_month": "Jun"}, False),
        ({"begin_year": 2019, "begin_month": "Jul"}, False),
        ({"begin_year": 2019, "begin_month": "Jun", "begin_day": 14}, False),
        ({"begin_year": 2019, "begin_month": "Jun", "begin_day": 15}, False),
        ({"begin_year": 2019, "begin_month": "Jun", "begin_day": 16}, False),
        ({"year": 2018}, True),
        ({"year": 2019}, False),
        ({"year": 2020}, False),
        ({"year": 2019, "month": "Apr"}, True),
        ({"year": 2019, "month": "Jun"}, False),
        ({"year": 2019, "month": "Jul"}, False),
        ({"year": 2019, "month": "Jun", "day": 14}, True),
        ({"year": 2019, "month": "Jun", "day": 15}, False),
        ({"year": 2019, "month": "Jun", "day": 16}, False),
    ]
)
def test_has_finished(thing, expected, now=TEST_DATE):
    assert has_finished(thing, now=now) == expected


@pytest.mark.parametrize(
    "thing,expected",
    [
        ({"year": 2019, "month": "Jun", "day": 14}, True),
        ({"year": 2019, "month": "Jun", "day": 15}, False),
        ({"year": 2019, "month": "Jun", "day": 16}, False),
        ({"date": "2019-04-15"}, True),
        ({"date": "2019-08-10"}, False),
    ]
)
def test_is_before(thing, expected, now=TEST_DATE):
    assert is_before(thing, now=now) == expected


@pytest.mark.parametrize(
    "thing,expected",
    [
        ({"year": 2019, "month": "Jun", "day": 14}, False),
        ({"year": 2019, "month": "Jun", "day": 15}, False),
        ({"year": 2019, "month": "Jun", "day": 16}, True),
        ({"date": "2019-04-15"}, False),
        ({"date": "2019-08-10"}, True),
    ]
)
def test_is_after(thing, expected, now=TEST_DATE):
    assert is_after(thing, now=now) == expected


@pytest.mark.parametrize(
    "thing,expected",
    [
        ({"year": 2019, "month": "Jun", "day": 14}, False),
        ({"year": 2019, "month": "Jan", "day": 15}, True),
        ({"year": 2019, "month": "Jan", "day": 2}, True),
        ({"date": "2019-04-15"}, False),
        ({"date": "2019-02-03"}, True),
    ]
)
def test_is_between(thing, expected, start=TEST_START_DATE, end=TEST_END_DATE):
    assert is_between(thing, start=start, end=end) == expected
