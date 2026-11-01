import pytest

from regolith.dates import date_to_float
from regolith.sorters import date_key, doc_date_key, doc_date_key_high, ene_date_key


# Test that sort keys give the same value for ISO and legacy dates, and fall back when dates are missing
@pytest.mark.parametrize(
    "sort_key, document, expected_float",
    [
        # C1: ene_date_key with 1. an ISO end_date, 2. the same end as legacy end_year and end_month,
        # expect the last day of that month
        pytest.param(ene_date_key, {"end_date": "2020-05-31"}, date_to_float(2020, 5, 31), id="ene-iso"),
        pytest.param(
            ene_date_key,
            {"begin_year": 2019, "end_year": 2020, "end_month": "May"},
            date_to_float(2020, 5, 31),
            id="ene-legacy",
        ),
        # C2: ene_date_key with a begin date but no end date, expect the far future so ongoing entries sort last
        pytest.param(ene_date_key, {"begin_date": "2019-01-01"}, date_to_float(4242, "dec"), id="ene-ongoing"),
        # C3: date_key with 1. an ISO end_date, 2. a legacy begin_year only, 3. an ISO point date,
        # expect the end date, then the begin date, then the point date
        pytest.param(
            date_key,
            {"begin_date": "2019-01-01", "end_date": "2020-05-31"},
            date_to_float(2020, 5, 31),
            id="date-key-iso-end",
        ),
        pytest.param(
            date_key,
            {"begin_year": 2019, "begin_month": "Mar"},
            date_to_float(2019, 3, 1),
            id="date-key-legacy-begin",
        ),
        pytest.param(date_key, {"date": "2021-07-04"}, date_to_float(2021, 7, 4), id="date-key-point"),
        # C4: doc_date_key with 1. an ISO date, 2. the same date as legacy year, month and day, expect that date
        pytest.param(doc_date_key, {"date": "2021-07-04"}, date_to_float(2021, 7, 4), id="doc-iso"),
        pytest.param(
            doc_date_key, {"year": 2021, "month": "Jul", "day": 4}, date_to_float(2021, 7, 4), id="doc-legacy"
        ),
        # C5: doc_date_key and doc_date_key_high with no dates, expect the start and end of 1970
        pytest.param(doc_date_key, {"name": "undated"}, date_to_float(1970, "jan"), id="doc-undated"),
        pytest.param(doc_date_key_high, {"name": "undated"}, date_to_float(1970, "dec"), id="doc-high-undated"),
    ],
)
def test_date_sort_keys(sort_key, document, expected_float):
    assert sort_key(document) == expected_float


# Test that sort keys leave the document they are given unchanged
def test_date_sort_keys_do_not_change_document():
    document = {"begin_year": 2019, "end_year": 2020}
    expected_document = dict(document)
    for sort_key in (date_key, doc_date_key, doc_date_key_high, ene_date_key):
        sort_key(document)
    assert document == expected_document


# Test that date_key refuses a document with no dates
def test_date_key_no_dates():
    with pytest.raises(KeyError, match="Could not find a date"):
        date_key({"name": "undated"})
