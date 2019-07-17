import pytest

from regolith.tools import (filter_publications, fuzzy_retrieval,
                            number_suffix, latex_safe, is_before,
                            is_since, is_between)


def test_author_publications():
    citations = [{"author": ["CJ", "SJLB"]}, {"editor": "SJLB"}]
    filter_publications(citations, {"SJLB"})


def test_is_since():
    y1, y2, y3 = 2000, 2010, 2020
    m1, m2, m3 = 1, 6, 12
    m4, m5, m6 = "Jan", "Jun", "Dec"
    d1, d2, d3 = 1, 15, 28
    assert is_since(y2, y1) is True
    assert is_since(y1, y1) is True
    assert is_since(y1, y2) is False
    assert is_since(y1, y1, m=m2, sm=m1) is True
    assert is_since(y1, y1, m=m3, sm=m3) is True
    assert is_since(y1, y1, m=m1, sm=m2) is False
    assert is_since(y1, y1, m=m5, sm=m4) is True
    assert is_since(y1, y1, m=m4, sm=m4) is True
    assert is_since(y1, y1, m=m4, sm=m5) is False
    assert is_since(y1, y1, m=m5, sm=m1) is True
    assert is_since(y1, y1, m=m2, sm=m4) is True
    assert is_since(y1, y1, m=m1, sm=m5) is False
    assert is_since(y1, y1, m=m1, sm=m1, d=d2, sd=d1) is True
    assert is_since(y1, y1, m=m1, sm=m1, d=d1, sd=d1) is True
    assert is_since(y1, y1, m=m1, sm=m1, d=d1, sd=d2) is False
    assert is_since(y1, y1, m=m1) is True
    assert is_since(y1, y1, m=m2) is True
    assert is_since(y1, y1, sm=m2) is False


def test_is_before():
    y1, y2, y3 = 2000, 2010, 2020
    m1, m2, m3 = 1, 6, 12
    m4, m5, m6 = "Jan", "Jun", "Dec"
    d1, d2, d3 = 1, 15, 28
    assert is_before(y2, y1) is False
    assert is_before(y1, y1) is True
    assert is_before(y1, y2) is True
    assert is_before(y1, y1, m=m2, bm=m1) is False
    assert is_before(y1, y1, m=m3, bm=m3) is True
    assert is_before(y1, y1, m=m1, bm=m2) is True
    assert is_before(y1, y1, m=m5, bm=m4) is False
    assert is_before(y1, y1, m=m4, bm=m4) is True
    assert is_before(y1, y1, m=m4, bm=m5) is True
    assert is_before(y1, y1, m=m5, bm=m1) is False
    assert is_before(y1, y1, m=m2, bm=m5) is True
    assert is_before(y1, y1, m=m1, bm=m5) is True
    assert is_before(y1, y1, m=m1, bm=m1, d=d2, bd=d1) is False
    assert is_before(y1, y1, m=m1, bm=m1, d=d1, bd=d1) is True
    assert is_before(y1, y1, m=m1, bm=m1, d=d1, bd=d2) is True
    assert is_before(y1, y1, m=m1) is True
    assert is_before(y1, y1, m=m3) is True
    assert is_before(y1, y1, bm=m2) is False

def test_is_between():
    y1, y2, y3 = 2000, 2010, 2020
    assert is_between(y2, y1, y3) is True
    assert is_between(y1, y1, y1) is True
    assert is_between(y1, y2, y3) is False
    assert is_between(y1, y3, y2) is False

def test_fuzzy_retrieval():
    person = {
        "_id": "scopatz",
        "aka": [
            "Scopatz",
            "Scopatz, A",
            "Scopatz, A.",
            "Scopatz, A M",
            "Anthony Michael Scopatz",
        ],
        "name": "Anthony Scopatz",
    }
    assert (
            fuzzy_retrieval([person], ["aka", "name", "_id"],
                            "scopatz") == person
    )
    assert (
            fuzzy_retrieval([person], ["aka", "name", "_id"],
                            "scopatz, a") is None
    )
    assert (
            fuzzy_retrieval(
                [person],
                ["aka", "name", "_id"],
                "scopatz, a",
                case_sensitive=False,
            )
            == person
    )


@pytest.mark.parametrize(
    "input,expected",
    [
        (0, "th"),
        (1, "st"),
        (2, "nd"),
        (3, "rd"),
        (4, "th"),
        (10, "th"),
        (13, "th"),
        (33, "rd"),
        (None, ""),
        ("0", ""),
    ],
)
def test_number_suffix(input, expected):
    assert number_suffix(input) == expected


@pytest.mark.parametrize(
    "input,expected,kwargs",
    [
        ('$hi', r'\$hi', {}),
        (r'Website: https://github.com/CJ-Wright/'
         r'Masters_Thesis/raw/master/thesis.pdf hi',
         r'Website: \url{https://github.com/CJ-Wright/'
         r'Masters_Thesis/raw/master/thesis.pdf} hi', {}),
        (r'Website: https://github.com/CJ-Wright/'
         r'Masters_Thesis/raw/master/thesis.pdf hi',
         r'Website: \href{https://github.com/CJ-Wright/'
         r'Masters_Thesis/raw/master/thesis.pdf} hi', {'wrapper': 'href'}),
        (r'Website: https://github.com/CJ-Wright/'
         r'Masters_Thesis/raw/master/thesis.pdf hi',
         r'Website: https://github.com/CJ-Wright/'
         r'Masters\_Thesis/raw/master/thesis.pdf hi', {'url_check': False})
    ],
)
def test_latex_safe(input, expected, kwargs):
    output = latex_safe(input, **kwargs)
    assert output == expected
