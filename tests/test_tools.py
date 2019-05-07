import pytest

from regolith.tools import (filter_publications, fuzzy_retrieval,
                            number_suffix, latex_safe, merge_collections)


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
def test_merge_collections(input, expected, kwargs):
    a = {
        "proposal": "just in a",
        "value": "value in a"
    }
    b = {
        "results": "just in b",
        "value": "value in b"
    }
    c = {}
    output = merge_collections(a, b)
    assert output == {"proposal": "just in a",
        "value": "value in b", "results": "just in b"}
    output = merge_collections(a, c)
    assert output == {"proposal": "just in a",
        "value": "value in a"}
