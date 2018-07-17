import pytest

from regolith.tools import filter_publications
from regolith.tools import fuzzy_retrieval, number_suffix


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
