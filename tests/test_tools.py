import pytest

from regolith.tools import (filter_publications, fuzzy_retrieval,
                            number_suffix, latex_safe)


def test_author_publications():
    citations = [{"author": ["CJ", "SJLB"]}, {"editor": "SJLB"}]
    filter_publications(citations, {"SJLB"})


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
        fuzzy_retrieval([person], ["aka", "name", "_id"], "scopatz") == person
    )
    assert (
        fuzzy_retrieval([person], ["aka", "name", "_id"], "scopatz, a") is None
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
    "input,expected",
    [
        ('$hi', r'\$hi'),
        (r'Website: https://github.com/CJ-Wright/'
         r'Masters_Thesis/raw/master/thesis.pdf hi',
         r'Website: \url{https://github.com/CJ-Wright/'
         r'Masters_Thesis/raw/master/thesis.pdf} hi')
    ],
)
def test_latex_safe(input, expected):
    output = latex_safe(input)
    assert output == expected
