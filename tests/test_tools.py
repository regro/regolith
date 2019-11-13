import pytest

from regolith.tools import (filter_publications, fuzzy_retrieval,
                            number_suffix, latex_safe, is_before,
                            is_since, is_between, has_started, has_finished,
                            is_current, update_schemas)


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


def test_has_started():
    y1, y2 = 2000, 2900
    m1, m2 = 1, 12
    m4, m5 = "Jan", "Dec"
    d1, d2 = 1, 28
    assert has_started(y1) is True
    assert has_started(y2) is False
    assert has_started(y1, sm=m1) is True
    assert has_started(y2, sm=m2) is False
    assert has_started(y1, sm=m4) is True
    assert has_started(y2, sm=m5) is False
    assert has_started(y1, sm=m1, sd=d1) is True
    assert has_started(y2, sm=m2, sd=d2) is False


def test_has_finished():
    y1, y2 = 2000, 2900
    m1, m2 = 1, 12
    m4, m5 = "Jan", "Dec"
    d1, d2 = 1, 28
    assert has_finished(y1) is True
    assert has_finished(y2) is False
    assert has_finished(y1, em=m1) is True
    assert has_finished(y2, em=m2) is False
    assert has_finished(y1, em=m4) is True
    assert has_finished(y2, em=m5) is False
    assert has_finished(y1, em=m1, ed=d1) is True
    assert has_finished(y2, em=m2, ed=d2) is False


def test_is_current():
    y1, y2, y3 = 2000, 2010, 2900
    m1, m2 = 1, 12
    m4, m5 = "Jan", "Dec"
    d1, d2 = 1, 28
    assert is_current(y1, y2) is False
    assert is_current(y2, y3) is True
    assert is_current(y1, y2, sm=m1) is False
    assert is_current(y2, y3, sm=m2) is True
    assert is_current(y2, y3, sm=m4) is True
    assert is_current(y1, y2, sm=m5) is False
    assert is_current(y1, y2, sm=m1, sd=d1) is False
    assert is_current(y2, y3, sm=m2, sd=d2) is True
    assert is_current(y1, y2, sm=m1, sd=d1, em=m2) is False
    assert is_current(y2, y3, sm=m2, sd=d2, em=m5) is True
    assert is_current(y1, y2, sm=m1, sd=d1, em=m2, ed=d1) is False
    assert is_current(y2, y3, sm=m2, sd=d2, em=m5, ed=d2) is True


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


DEFAULT_SCHEMA = {
    "expenses": {
        "itemized_expenses": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "day": {
                        "description": "Expense day",
                        "required": True,
                        "type": "integer",
                    },
                },
            },
        },
    },
}

USER_SCHEMA0 = {
    "expenses": {
        "itemized_expenses": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "day": {
                        "required": False,
                    },
                },
            },
        },
    },
}

EXPECTED_SCHEMA0 = {
    "expenses": {
        "itemized_expenses": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "day": {
                        "description": "Expense day",
                        "required": False,
                        "type": "integer",
                    },
                },
            },
        },
    },
}

USER_SCHEMA1 = {
    "expenses": {
        "itemized_expenses": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "day": {
                        "type": "string",
                    },
                },
            },
        },
    },
}

EXPECTED_SCHEMA1 = {
    "expenses": {
        "itemized_expenses": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "day": {
                        "description": "Expense day",
                        "required": True,
                        "type": "string",
                    },
                },
            },
        },
    },
}

USER_SCHEMA2 = {
    "expenses": {
        "begin_day": {
            "description": "The first day of expense",
            "required": True,
            "type": "string",
        }
    },
}

EXPECTED_SCHEMA2 = {
    "expenses": {
        "itemized_expenses": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "day": {
                        "description": "Expense day",
                        "required": True,
                        "type": "integer",
                    },
                },
            },
        },
        "begin_day": {
            "description": "The first day of expense",
            "required": True,
            "type": "string",
        }
    },
}

USER_SCHEMA3 = {
    "expenses": {
        "itemized_expenses": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "day": {
                        "description": "The date on the receipt"
                    },
                },
            },
        },
    },
}

EXPECTED_SCHEMA3 = {
    "expenses": {
        "itemized_expenses": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "day": {
                        "description": "The date on the receipt",
                        "required": True,
                        "type": "integer",
                    },
                },
            },
        },
    },
}

USER_SCHEMA4 = {
    "expenses": {
        "itemized_expenses": {
            "schema": {
                "schema": {
                    "prepaid_expense": {
                        "description": "Expense paid by the direct billing",
                        "required": True,
                        "type": "float",
                    },
                },
            },
        },
    },
}

EXPECTED_SCHEMA4 = {
    "expenses": {
        "itemized_expenses": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "day": {
                        "description": "Expense day",
                        "required": True,
                        "type": "integer",
                    },
                    "prepaid_expense": {
                        "description": "Expense paid by the direct billing",
                        "required": True,
                        "type": "float",
                    },
                },
            },
        },
    },
}

USER_SCHEMA5 = {}

EXPECTED_SCHEMA5 = {
    "expenses": {
        "itemized_expenses": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "day": {
                        "description": "Expense day",
                        "required": True,
                        "type": "integer",
                    },
                },
            },
        },
    },
}

USER_SCHEMA6 = {
    "expenses": {}
}

EXPECTED_SCHEMA6 = {
    "expenses": {
        "itemized_expenses": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "day": {
                        "description": "Expense day",
                        "required": True,
                        "type": "integer",
                    },
                },
            },
        },
    },
}


@pytest.mark.parametrize(
    "default_schema, user_schema, expected_schema",
    [
        (DEFAULT_SCHEMA, USER_SCHEMA0, EXPECTED_SCHEMA0),
        (DEFAULT_SCHEMA, USER_SCHEMA1, EXPECTED_SCHEMA1),
        (DEFAULT_SCHEMA, USER_SCHEMA2, EXPECTED_SCHEMA2),
        (DEFAULT_SCHEMA, USER_SCHEMA3, EXPECTED_SCHEMA3),
        (DEFAULT_SCHEMA, USER_SCHEMA4, EXPECTED_SCHEMA4),
        (DEFAULT_SCHEMA, USER_SCHEMA5, EXPECTED_SCHEMA5),
        (DEFAULT_SCHEMA, USER_SCHEMA6, EXPECTED_SCHEMA6),
    ],
)
def test_update_schemas(default_schema, user_schema, expected_schema):
    updated_schema = update_schemas(default_schema, user_schema)
    assert updated_schema == expected_schema
