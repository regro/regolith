import copy
import datetime as dt

import habanero
import pytest
import requests_mock

from regolith.runcontrol import DEFAULT_RC
from regolith.tools import (
    awards_grants_honors,
    collect_appts,
    collection_str,
    compound_dict,
    compound_list,
    create_repo,
    date_to_rfc822,
    dereference_institution,
    filter_employment_for_advisees,
    filter_presentations,
    filter_publications,
    fragment_retrieval,
    fuzzy_retrieval,
    get_appointments,
    get_formatted_crossref_reference,
    get_id_from_name,
    get_person_contact,
    get_tags,
    get_target_repo_info,
    get_target_token,
    get_uuid,
    grant_burn,
    group,
    group_member_employment_start_end,
    group_member_ids,
    is_fully_appointed,
    key_value_pair_filter,
    latex_safe,
    merge_collections_all,
    merge_collections_intersect,
    merge_collections_superior,
    month_and_year,
    number_suffix,
    remove_duplicate_docs,
    search_collection,
    update_schemas,
    validate_meeting,
    filter_software
)

PEOPLE_COLL = [
    {
        "_id": "m1",
        "name": "member1",
        "education": [
            {"group": "bg", "institution": "columbiau", "degree": "PhD", "department": "apam", "begin_year": 2016}
        ],
        "employment": [
            {
                "begin_year": 2020,
                "begin_month": 1,
                "organization": "columbiau",
                "position": "Undergraduate Researcher",
                "advisor": "sbillinge",
                "status": "undergrad",
            }
        ],
        "funding": [{"name": "Omega Laser User's Group Travel Award", "value": 1100, "year": 2013}],
        "service": [
            {
                "name": "International Steering Committee",
                "role": "chair",
                "type": "profession",
                "year": 2020,
                "month": 3,
                "notes": ["something"],
            }
        ],
    },
    {
        "_id": "nm1",
        "name": "non-member1",
        "education": [{"institution": "columbiau", "degree": "PhD", "department": "apam", "begin_year": 2016}],
        "employment": [
            {
                "begin_year": 2020,
                "begin_month": 1,
                "organization": "columbiau",
                "position": "Undergraduate Researcher",
                "advisor": "sbillinge",
                "status": "undergrad",
            }
        ],
    },
    {
        "_id": "m2",
        "name": "member2",
        "education": [{"institution": "columbiau", "degree": "PhD", "department": "apam", "begin_year": 2016}],
        "employment": [
            {
                "begin_year": 2020,
                "begin_month": 1,
                "group": "bg",
                "organization": "columbiau",
                "position": "Undergraduate Researcher",
                "advisor": "sbillinge",
                "status": "undergrad",
            }
        ],
    },
]

CONTACTS_COLL = [{"_id": "c1", "name": "contact1", "institution": "columbiau"}]


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            ["m1", PEOPLE_COLL, CONTACTS_COLL],
            {
                "_id": "m1",
                "funding": [{"name": "Omega Laser User's Group Travel Award", "value": 1100, "year": 2013}],
                "name": "member1",
                "service": [
                    {
                        "month": 3,
                        "name": "International Steering Committee",
                        "notes": ["something"],
                        "role": "chair",
                        "type": "profession",
                        "year": 2020,
                    }
                ],
                "education": [
                    {
                        "group": "bg",
                        "institution": "columbiau",
                        "degree": "PhD",
                        "department": "apam",
                        "begin_year": 2016,
                    }
                ],
                "employment": [
                    {
                        "begin_year": 2020,
                        "begin_month": 1,
                        "organization": "columbiau",
                        "position": "Undergraduate Researcher",
                        "advisor": "sbillinge",
                        "status": "undergrad",
                    }
                ],
            },
        ),
        (["c1", PEOPLE_COLL, CONTACTS_COLL], {"_id": "c1", "name": "contact1", "institution": "columbiau"}),
        (["bad1", PEOPLE_COLL, CONTACTS_COLL], None),
    ],
)
def test_get_person_contact(input, expected):
    actual = get_person_contact(input[0], input[1], input[2])
    assert actual == expected


CITATIONS = [
    {
        "_id": "paper",
        "author": ["m1", "cleese"],
        "ackno": "thanks",
        "grant": "fwp, dmref",
        "month": "apr",
        "year": "2021",
    },
    {"_id": "paper2", "author": ["m1", "palin"], "ackno": "thanks", "grant": "fwp2", "year": "2020"},
    {
        "_id": "paper3",
        "author": ["m1", "jones"],
        "ackno": "thanks",
        "grant": "fwp2",
        "month": "jun",
        "year": "2020",
    },
]


@pytest.mark.parametrize(
    "args, kwargs, expected",
    [
        (
            [CITATIONS, set(["m1"])],
            {},
            [
                {
                    "_id": "paper3",
                    "author": ["\\textbf{m1}", "jones"],
                    "ackno": "thanks",
                    "grant": "fwp2",
                    "month": "jun",
                    "year": "2020",
                },
                {
                    "_id": "paper2",
                    "author": ["\\textbf{m1}", "palin"],
                    "ackno": "thanks",
                    "grant": "fwp2",
                    "year": "2020",
                },
                {
                    "_id": "paper",
                    "ackno": "thanks",
                    "author": ["\\textbf{m1}", "cleese"],
                    "grant": "fwp, dmref",
                    "month": "apr",
                    "year": "2021",
                },
            ],
        ),
        (
            [CITATIONS, set(["m1"])],
            {"bold": False, "ackno": True},
            [
                {
                    "_id": "paper3",
                    "author": ["m1", "jones"],
                    "ackno": "thanks",
                    "grant": "fwp2",
                    "month": "jun",
                    "note": "\\newline\\newline\\noindent Acknowledgement:\\newline\\noindent thanks"
                    "\\newline\\newline\\noindent ",
                    "year": "2020",
                },
                {
                    "_id": "paper2",
                    "author": ["m1", "palin"],
                    "ackno": "thanks",
                    "grant": "fwp2",
                    "note": "\\newline\\newline\\noindent Acknowledgement:\\newline\\noindent thanks"
                    "\\newline\\newline\\noindent ",
                    "year": "2020",
                },
                {
                    "_id": "paper",
                    "ackno": "thanks",
                    "author": ["m1", "cleese"],
                    "grant": "fwp, dmref",
                    "month": "apr",
                    "note": "\\newline\\newline\\noindent Acknowledgement:\\newline\\noindent thanks"
                    "\\newline\\newline\\noindent ",
                    "year": "2021",
                },
            ],
        ),
        (
            [CITATIONS, set(["m1"])],
            {"bold": False},
            [
                {
                    "_id": "paper3",
                    "author": ["m1", "jones"],
                    "ackno": "thanks",
                    "grant": "fwp2",
                    "month": "jun",
                    "year": "2020",
                },
                {"_id": "paper2", "author": ["m1", "palin"], "ackno": "thanks", "grant": "fwp2", "year": "2020"},
                {
                    "_id": "paper",
                    "ackno": "thanks",
                    "author": ["m1", "cleese"],
                    "grant": "fwp, dmref",
                    "month": "apr",
                    "year": "2021",
                },
            ],
        ),
        (
            [CITATIONS, set(["m1"])],
            {"bold": False, "grants": "fwp2"},
            [
                {
                    "_id": "paper3",
                    "author": ["m1", "jones"],
                    "ackno": "thanks",
                    "grant": "fwp2",
                    "month": "jun",
                    "year": "2020",
                },
                {"_id": "paper2", "author": ["m1", "palin"], "ackno": "thanks", "grant": "fwp2", "year": "2020"},
            ],
        ),
        (
            [CITATIONS, set(["m1"])],
            {"bold": False, "grants": ["fwp2", "dmref"]},
            [
                {
                    "_id": "paper3",
                    "author": ["m1", "jones"],
                    "ackno": "thanks",
                    "grant": "fwp2",
                    "month": "jun",
                    "year": "2020",
                },
                {"_id": "paper2", "author": ["m1", "palin"], "ackno": "thanks", "grant": "fwp2", "year": "2020"},
                {
                    "_id": "paper",
                    "ackno": "thanks",
                    "author": ["m1", "cleese"],
                    "grant": "fwp, dmref",
                    "month": "apr",
                    "year": "2021",
                },
            ],
        ),
        (
            [CITATIONS, set(["m1"])],
            {"bold": False, "since": dt.date(2021, 1, 1)},
            [
                {
                    "_id": "paper",
                    "ackno": "thanks",
                    "author": ["m1", "cleese"],
                    "grant": "fwp, dmref",
                    "month": "apr",
                    "year": "2021",
                }
            ],
        ),
        (
            [CITATIONS, set(["m1"])],
            {"bold": False, "since": dt.date(2020, 5, 1), "before": dt.date(2021, 1, 1)},
            [
                {
                    "_id": "paper3",
                    "author": ["m1", "jones"],
                    "ackno": "thanks",
                    "grant": "fwp2",
                    "month": "jun",
                    "year": "2020",
                },
                {"_id": "paper2", "author": ["m1", "palin"], "ackno": "thanks", "grant": "fwp2", "year": "2020"},
            ],
        ),
    ],
)
def test_filter_publications(args, kwargs, expected):
    actual = filter_publications(*args, **kwargs)
    assert actual == expected


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
    assert fuzzy_retrieval([person], ["aka", "name", "_id"], "scopatz") == person
    assert fuzzy_retrieval([person], ["aka", "name", "_id"], "scopatz, a") is None
    assert (
        fuzzy_retrieval(
            [person],
            ["aka", "name", "_id"],
            "scopatz, a",
            case_sensitive=False,
        )
        == person
    )


def test_get_formatted_crossref_reference(monkeypatch):
    def mockreturn(*args, **kwargs):
        mock_article = {
            "message": {
                "author": [{"given": "SJL", "family": "Billinge"}],
                "short-container-title": ["J. Great Results"],
                "volume": 10,
                "title": ["Whamo"],
                "page": "231-233",
                "issued": {"date-parts": [[1971, 8, 20]]},
            }
        }
        return mock_article

    monkeypatch.setattr(habanero.Crossref, "works", mockreturn)
    expected = ("Whamo, SJL Billinge, J. Great Results, v. 10, pp. 231-233, (1971).", dt.date(1971, 8, 20))
    actual = get_formatted_crossref_reference("test")
    assert actual == expected


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
        (
            (
                [
                    {
                        "_id": "proposal1",
                        "title": "European swallow",
                        "author": "king arthur",
                    }
                ],
                [{"_id": "grant1", "linked_to": "proposal1", "amount": "100 mph"}],
            ),
            [
                {
                    "_id": "grant1",
                    "title": "European swallow",
                    "author": "king arthur",
                    "linked_to": "proposal1",
                    "amount": "100 mph",
                }
            ],
        ),
        (
            (
                [
                    {
                        "_id": "proposal1",
                        "title": "European swallow",
                        "author": "king arthur",
                    },
                    {
                        "_id": "proposal2",
                        "title": "African swallow",
                        "author": "king arthur",
                    },
                ],
                [{"_id": "grant1", "linked_to": "proposal1", "amount": "100 mph"}],
            ),
            [
                {
                    "_id": "proposal2",
                    "title": "African swallow",
                    "author": "king arthur",
                },
                {
                    "_id": "grant1",
                    "title": "European swallow",
                    "author": "king arthur",
                    "linked_to": "proposal1",
                    "amount": "100 mph",
                },
            ],
        ),
        (
            (
                [
                    {
                        "_id": "proposal1",
                        "title": "European swallow",
                        "author": "king arthur",
                        "amount": "50 mph",
                    },
                    {
                        "_id": "proposal2",
                        "title": "African swallow",
                        "author": "king arthur",
                    },
                ],
                [{"_id": "grant1", "linked_to": "proposal1", "amount": "100 mph"}],
            ),
            [
                {
                    "_id": "proposal2",
                    "title": "African swallow",
                    "author": "king arthur",
                },
                {
                    "_id": "grant1",
                    "title": "European swallow",
                    "author": "king arthur",
                    "linked_to": "proposal1",
                    "amount": "100 mph",
                },
            ],
        ),
        (
            (
                [
                    {
                        "_id": "proposal1",
                        "title": "European swallow",
                        "author": "king arthur",
                        "amount": "50 mph",
                    },
                    {
                        "_id": "proposal2",
                        "title": "African swallow",
                        "author": "king arthur",
                    },
                ],
                [
                    {"_id": "grant1", "linked_to": "proposal1", "amount": "100 mph"},
                    {
                        "_id": "grant2",
                        "title": "African swallow",
                        "author": "king arthur",
                    },
                ],
            ),
            [
                {
                    "_id": "proposal2",
                    "title": "African swallow",
                    "author": "king arthur",
                },
                {
                    "_id": "grant1",
                    "title": "European swallow",
                    "author": "king arthur",
                    "linked_to": "proposal1",
                    "amount": "100 mph",
                },
                {
                    "_id": "grant2",
                    "title": "African swallow",
                    "author": "king arthur",
                },
            ],
        ),
        (
            (
                [
                    {
                        "_id": "proposal1",
                        "title": "European swallow",
                        "author": "king arthur",
                        "amount": "50 mph",
                    },
                    {
                        "_id": "proposal2",
                        "title": "African swallow",
                        "author": "king arthur",
                    },
                ],
                [
                    {"_id": "grant1", "linked_to": "proposal1", "amount": "100 mph"},
                    {
                        "_id": "grant2",
                        "title": "African swallow",
                        "author": "king arthur",
                        "linked_to": "proposal2",
                    },
                ],
            ),
            [
                {
                    "_id": "grant1",
                    "title": "European swallow",
                    "author": "king arthur",
                    "linked_to": "proposal1",
                    "amount": "100 mph",
                },
                {
                    "_id": "grant2",
                    "title": "African swallow",
                    "author": "king arthur",
                    "linked_to": "proposal2",
                },
            ],
        ),
        (
            (
                [
                    {
                        "_id": "proposal1",
                        "title": "European swallow",
                        "author": "king arthur",
                        "amount": "50 mph",
                    },
                ],
                [
                    {"_id": "grant1", "linked_to": "proposal1", "amount": "100 mph"},
                    {
                        "_id": "grant2",
                        "title": "African swallow",
                        "author": "king arthur",
                    },
                ],
            ),
            [
                {
                    "_id": "grant1",
                    "title": "European swallow",
                    "author": "king arthur",
                    "linked_to": "proposal1",
                    "amount": "100 mph",
                },
                {
                    "_id": "grant2",
                    "title": "African swallow",
                    "author": "king arthur",
                },
            ],
        ),
    ],
)
def test_merge_collections_all(input, expected):
    a = input[0]
    b = input[1]
    target_id = "linked_to"
    assert merge_collections_all(a, b, target_id) == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        (
            (
                [
                    {
                        "_id": "proposal1",
                        "title": "European swallow",
                        "author": "king arthur",
                    }
                ],
                [{"_id": "grant1", "linked_to": "proposal1", "amount": "100 mph"}],
            ),
            [
                {
                    "_id": "grant1",
                    "title": "European swallow",
                    "author": "king arthur",
                    "linked_to": "proposal1",
                    "amount": "100 mph",
                }
            ],
        ),
        (
            (
                [
                    {
                        "_id": "proposal1",
                        "title": "European swallow",
                        "author": "king arthur",
                    },
                    {
                        "_id": "proposal2",
                        "title": "African swallow",
                        "author": "king arthur",
                    },
                ],
                [{"_id": "grant1", "linked_to": "proposal1", "amount": "100 mph"}],
            ),
            [
                {
                    "_id": "grant1",
                    "title": "European swallow",
                    "author": "king arthur",
                    "linked_to": "proposal1",
                    "amount": "100 mph",
                },
            ],
        ),
        (
            (
                [
                    {
                        "_id": "proposal1",
                        "title": "European swallow",
                        "author": "king arthur",
                        "amount": "50 mph",
                    },
                    {
                        "_id": "proposal2",
                        "title": "African swallow",
                        "author": "king arthur",
                    },
                ],
                [{"_id": "grant1", "linked_to": "proposal1", "amount": "100 mph"}],
            ),
            [
                {
                    "_id": "grant1",
                    "title": "European swallow",
                    "author": "king arthur",
                    "linked_to": "proposal1",
                    "amount": "100 mph",
                },
            ],
        ),
        (
            (
                [
                    {
                        "_id": "proposal1",
                        "title": "European swallow",
                        "author": "king arthur",
                        "amount": "50 mph",
                    },
                    {
                        "_id": "proposal2",
                        "title": "African swallow",
                        "author": "king arthur",
                    },
                ],
                [
                    {"_id": "grant1", "linked_to": "proposal1", "amount": "100 mph"},
                    {
                        "_id": "grant2",
                        "title": "African swallow",
                        "author": "king arthur",
                    },
                ],
            ),
            [
                {
                    "_id": "grant1",
                    "title": "European swallow",
                    "author": "king arthur",
                    "linked_to": "proposal1",
                    "amount": "100 mph",
                },
                {
                    "_id": "grant2",
                    "title": "African swallow",
                    "author": "king arthur",
                },
            ],
        ),
        (
            (
                [
                    {
                        "_id": "proposal1",
                        "title": "European swallow",
                        "author": "king arthur",
                        "amount": "50 mph",
                    },
                    {
                        "_id": "proposal2",
                        "title": "African swallow",
                        "author": "king arthur",
                    },
                ],
                [
                    {"_id": "grant1", "linked_to": "proposal1", "amount": "100 mph"},
                    {
                        "_id": "grant2",
                        "title": "African swallow",
                        "author": "king arthur",
                        "linked_to": "proposal2",
                    },
                ],
            ),
            [
                {
                    "_id": "grant1",
                    "title": "European swallow",
                    "author": "king arthur",
                    "linked_to": "proposal1",
                    "amount": "100 mph",
                },
                {
                    "_id": "grant2",
                    "title": "African swallow",
                    "author": "king arthur",
                    "linked_to": "proposal2",
                },
            ],
        ),
        (
            (
                [
                    {
                        "_id": "proposal1",
                        "title": "European swallow",
                        "author": "king arthur",
                        "amount": "50 mph",
                    },
                ],
                [
                    {"_id": "grant1", "linked_to": "proposal1", "amount": "100 mph"},
                    {
                        "_id": "grant2",
                        "title": "African swallow",
                        "author": "king arthur",
                    },
                ],
            ),
            [
                {
                    "_id": "grant1",
                    "title": "European swallow",
                    "author": "king arthur",
                    "linked_to": "proposal1",
                    "amount": "100 mph",
                },
                {
                    "_id": "grant2",
                    "title": "African swallow",
                    "author": "king arthur",
                },
            ],
        ),
    ],
)
def test_merge_collections_superior(input, expected):
    a = input[0]
    b = input[1]
    target_id = "linked_to"
    assert merge_collections_superior(a, b, target_id) == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        (
            (
                [
                    {
                        "_id": "proposal1",
                        "title": "European swallow",
                        "author": "king arthur",
                    }
                ],
                [{"_id": "grant1", "linked_to": "proposal1", "amount": "100 mph"}],
            ),
            [
                {
                    "_id": "grant1",
                    "title": "European swallow",
                    "author": "king arthur",
                    "linked_to": "proposal1",
                    "amount": "100 mph",
                }
            ],
        ),
        (
            (
                [
                    {
                        "_id": "proposal1",
                        "title": "European swallow",
                        "author": "king arthur",
                    },
                    {
                        "_id": "proposal2",
                        "title": "African swallow",
                        "author": "king arthur",
                    },
                ],
                [{"_id": "grant1", "linked_to": "proposal1", "amount": "100 mph"}],
            ),
            [
                {
                    "_id": "grant1",
                    "title": "European swallow",
                    "author": "king arthur",
                    "linked_to": "proposal1",
                    "amount": "100 mph",
                },
            ],
        ),
        (
            (
                [
                    {
                        "_id": "proposal1",
                        "title": "European swallow",
                        "author": "king arthur",
                        "amount": "50 mph",
                    },
                    {
                        "_id": "proposal2",
                        "title": "African swallow",
                        "author": "king arthur",
                    },
                ],
                [{"_id": "grant1", "linked_to": "proposal1", "amount": "100 mph"}],
            ),
            [
                {
                    "_id": "grant1",
                    "title": "European swallow",
                    "author": "king arthur",
                    "linked_to": "proposal1",
                    "amount": "100 mph",
                },
            ],
        ),
        (
            (
                [
                    {
                        "_id": "proposal1",
                        "title": "European swallow",
                        "author": "king arthur",
                        "amount": "50 mph",
                    },
                    {
                        "_id": "proposal2",
                        "title": "African swallow",
                        "author": "king arthur",
                    },
                ],
                [
                    {"_id": "grant1", "linked_to": "proposal1", "amount": "100 mph"},
                ],
            ),
            [
                {
                    "_id": "grant1",
                    "title": "European swallow",
                    "author": "king arthur",
                    "linked_to": "proposal1",
                    "amount": "100 mph",
                },
            ],
        ),
        (
            (
                [
                    {
                        "_id": "proposal1",
                        "title": "European swallow",
                        "author": "king arthur",
                        "amount": "50 mph",
                    },
                    {
                        "_id": "proposal2",
                        "title": "African swallow",
                        "author": "king arthur",
                    },
                ],
                [
                    {"_id": "grant1", "linked_to": "proposal1", "amount": "100 mph"},
                    {
                        "_id": "grant2",
                        "title": "African swallow",
                        "author": "king arthur",
                        "linked_to": "proposal2",
                    },
                ],
            ),
            [
                {
                    "_id": "grant1",
                    "title": "European swallow",
                    "author": "king arthur",
                    "linked_to": "proposal1",
                    "amount": "100 mph",
                },
                {
                    "_id": "grant2",
                    "title": "African swallow",
                    "author": "king arthur",
                    "linked_to": "proposal2",
                },
            ],
        ),
        (
            (
                [
                    {
                        "_id": "proposal1",
                        "title": "European swallow",
                        "author": "king arthur",
                        "amount": "50 mph",
                    },
                ],
                [
                    {"_id": "grant1", "linked_to": "proposal1", "amount": "100 mph"},
                    {
                        "_id": "grant2",
                        "title": "African swallow",
                        "author": "king arthur",
                    },
                ],
            ),
            [
                {
                    "_id": "grant1",
                    "title": "European swallow",
                    "author": "king arthur",
                    "linked_to": "proposal1",
                    "amount": "100 mph",
                },
            ],
        ),
    ],
)
def test_merge_intersection(input, expected):
    a = input[0]
    b = input[1]
    target_id = "linked_to"
    assert merge_collections_intersect(a, b, target_id) == expected


@pytest.mark.parametrize(
    "input,expected,kwargs",
    [
        ("$hi", r"\$hi", {}),
        (
            r"Website: https://github.com/CJ-Wright/" r"Masters_Thesis/raw/master/thesis.pdf hi",
            r"Website: \url{https://github.com/CJ-Wright/" r"Masters_Thesis/raw/master/thesis.pdf} hi",
            {},
        ),
        (
            r"Website: https://github.com/CJ-Wright/" r"Masters_Thesis/raw/master/thesis.pdf hi",
            r"Website: \href{https://github.com/CJ-Wright/" r"Masters_Thesis/raw/master/thesis.pdf} hi",
            {"wrapper": "href"},
        ),
        (
            r"Website: https://github.com/CJ-Wright/" r"Masters_Thesis/raw/master/thesis.pdf hi",
            r"Website: https://github.com/CJ-Wright/" r"Masters\_Thesis/raw/master/thesis.pdf hi",
            {"url_check": False},
        ),
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
        },
    },
}

USER_SCHEMA3 = {
    "expenses": {
        "itemized_expenses": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "day": {"description": "The date on the receipt"},
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

USER_SCHEMA6 = {"expenses": {}}

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


def test_group():
    doc0 = {"k0": "v00", "k1": "v01"}
    doc1 = {"k0": "v10", "k1": "v11"}
    doc2 = {"k1": "v21"}
    doc3 = {"k0": "v00", "k1": "v31"}
    db = (doc for doc in (doc0, doc1, doc2, doc3))
    by = "k0"
    expect = {"v00": [doc0, doc3], "v10": [doc1]}
    assert group(db, by) == expect


ppl_coll = [
    {
        "_id": "m1",
        "name": "member1",
        "education": [
            {"group": "bg", "institution": "columbiau", "degree": "PhD", "department": "apam", "begin_year": 2016}
        ],
        "employment": [
            {
                "begin_year": 2020,
                "begin_month": 1,
                "organization": "columbiau",
                "position": "Undergraduate Researcher",
                "advisor": "sbillinge",
                "status": "undergrad",
            }
        ],
    },
    {
        "_id": "nm1",
        "name": "non-member1",
        "education": [{"institution": "columbiau", "degree": "PhD", "department": "apam", "begin_year": 2016}],
        "employment": [
            {
                "begin_year": 2020,
                "begin_month": 1,
                "organization": "columbiau",
                "position": "Undergraduate Researcher",
                "advisor": "sbillinge",
                "status": "undergrad",
            }
        ],
    },
    {
        "_id": "m2",
        "name": "member2",
        "education": [{"institution": "columbiau", "degree": "PhD", "department": "apam", "begin_year": 2016}],
        "employment": [
            {
                "begin_year": 2020,
                "begin_month": 1,
                "group": "bg",
                "organization": "columbiau",
                "position": "Undergraduate Researcher",
                "advisor": "sbillinge",
                "status": "undergrad",
            }
        ],
    },
]


@pytest.mark.parametrize(
    "input,expected",
    [
        (ppl_coll, set(["m1", "m2"])),
    ],
)
def test_group_member_ids(input, expected):
    actual = group_member_ids(input, "bg")
    assert actual == expected


d1 = {
    "name": "John",
    "experience": [{"company": "Google", "role": "product manager"}, {"company": "Amazon", "role": "QA"}],
    "school": {"name": "Columbia", "location": "NYC", "year": "senior"},
}
d2 = {
    "name": "Sarah",
    "experience": [{"company": "Verizon", "role": "sales"}, {"company": "AT&T", "role": "software engineer"}],
    "school": {"name": "Columbia", "location": "NYC", "year": "junior"},
    "hobbies": ["swimming", "hiking"],
    "info": {"stats": {"code": "a76", "location": "California"}, "software": "CAD"},
}
d3 = {
    "_id": "abc",
    "name": "Example Lab",
    "Members": [
        {
            "Name": "Lisa",
            "Experience": [
                {"company": "Google", "location": {"state": "CA", "zip code": "94043"}},
                {"company": "Amazon", "location": {"state": "VA", "zip code": "20189"}},
            ],
        },
        {
            "Name": "Stephen",
            "Experience": [{"company": "Goldman Sachs", "location": {"state": "NY", "zip code": "10282"}}],
        },
    ],
}


@pytest.mark.parametrize(
    "input,expected",
    [
        (d1, ["John", "Google", "product manager", "Amazon", "QA", "Columbia", "NYC", "senior"]),
        (
            d2,
            [
                "Sarah",
                "Verizon",
                "sales",
                "AT&T",
                "software engineer",
                "Columbia",
                "NYC",
                "junior",
                "swimming",
                "hiking",
                "a76",
                "California",
                "CAD",
            ],
        ),
        (
            d3,
            [
                "abc",
                "Example Lab",
                "Lisa",
                "Google",
                "CA",
                "94043",
                "Amazon",
                "VA",
                "20189",
                "Stephen",
                "Goldman Sachs",
                "NY",
                "10282",
            ],
        ),
    ],
)
def test_compound_dict(input, expected):
    assert compound_dict(input, []) == expected


l1 = ["hello", {"name": "Fred", "status": "active"}, {"name": "Derf", "status": "inactive"}, "bye"]
l2 = [
    ["a", "b", "c"],
    {"name": "Anthony", "Status": "active"},
    [{"product": "phone"}, {"product": "laptop"}],
    "end",
]


@pytest.mark.parametrize(
    "input,expected",
    [
        (l1, ["hello", "Fred", "active", "Derf", "inactive", "bye"]),
        (l2, ["a", "b", "c", "Anthony", "active", "phone", "laptop", "end"]),
    ],
)
def test_compound_list(input, expected):
    assert compound_list(input, []) == expected


p1 = {
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
p2 = {
    "_id": "abc",
    "aka": [
        "A. BC",
        "BC, A",
        "Anthony BC",
    ],
    "name": "Anthony Bill Chris",
}
p3 = {
    "_id": "Leonan",
    "name": "Leonan Garea",
    "company": {"name": "Amazon", "role": "Product Manager"},
    "projects": [
        {"title": "GUI Application", "description": "Make a GUI for the group"},
    ],
}
p4 = {
    "_id": "cba",
    "name": "Jackie",
    "company": {},
    "projects": [
        {"title": "PDF Maker", "description": "New PDF function"},
        {"title": "Write Paper", "description": "Draft the new paper"},
    ],
}
p5 = {
    "_id": "ghi",
    "name": "Carl",
    "experience": [
        {
            "name": "Google",
            "roles": [
                {"position": "software engineer", "location": {"state": "CA", "zip code": "92551"}},
                {"position": "manager", "location": {"state": "VA", "zip code": "20189"}},
            ],
        },
        {
            "name": "Goldman Sachs",
            "Experience": [{"position": "junior associate", "location": {"state": "NY", "zip code": "10282"}}],
        },
    ],
}


@pytest.mark.parametrize(
    "input, expected",
    [
        (([p1, p2], ["aka", "name", "_id"], "Anth", False), [p1, p2]),
        (([p1, p2], ["aka", "name", "_id"], "scopatz, a", True), []),
        (([p1, p2], ["aka", "name", "_id"], "scopatz, a", False), [p1]),
        (([p1, p2], ["aka", "name", "_id"], "ill", False), [p2]),
        (([p3], ["company"], "Amazon", False), [p3]),
        (([p3, p4], ["projects"], "PDF", False), [p4]),
        (([p5], ["experience"], "20189", False), [p5]),
        (([p5], ["experience"], "hello", False), []),
    ],
)
def test_fragment_retrieval(input, expected):
    assert fragment_retrieval(input[0], input[1], input[2], case_sensitive=input[3]) == expected


@pytest.mark.parametrize(
    "input, expected",
    [
        ((None, None), "present"),
        ((None, 2002), "2002"),
        ((5, 2002), "May 2002"),
    ],
)
def test_month_and_year(input, expected):
    assert month_and_year(input[0], input[1]) == expected


@pytest.mark.parametrize(
    "appts,start,end,expected",
    [
        (
            {
                "name": "Kurt Godel",
                "_id": "kgodel",
                "appointments": {
                    "A": {
                        "begin_year": 2017,
                        "begin_month": 6,
                        "begin_day": 1,
                        "end_year": 2017,
                        "end_month": 6,
                        "end_day": 30,
                        "grant": "grant1",
                        "loading": 1.0,
                        "type": "pd",
                    }
                },
            },
            "2017-06-01",
            "2017-07-01",
            False,
        ),
        (
            {
                "name": "MC Escher",
                "_id": "mcescher",
                "appointments": {
                    "A": {
                        "begin_date": "2017-06-01",
                        "end_date": "2017-06-30",
                        "grant": "grant1",
                        "loading": 0.5,
                        "type": "pd",
                    },
                    "B": {
                        "begin_date": "2017-06-01",
                        "end_date": "2017-06-30",
                        "grant": "grant2",
                        "loading": 0.5,
                        "type": "pd",
                    },
                },
            },
            "2017-06-01",
            "2017-06-30",
            True,
        ),
        (
            {
                "name": "Johann Sebastian Bach",
                "_id": "jsbach",
                "appointments": {
                    "A": {
                        "begin_date": "2017-06-01",
                        "end_date": "2017-06-30",
                        "grant": "grant1",
                        "loading": 0.5,
                        "type": "pd",
                    },
                    "B": {
                        "begin_date": "2017-06-02",
                        "end_date": "2017-06-29",
                        "grant": "grant2",
                        "loading": 0.5,
                        "type": "pd",
                    },
                },
            },
            "2017-06-01",
            "2017-06-30",
            False,
        ),
        (
            {
                "name": "Evariste Galois",
                "_id": "egalois",
                "appointments": {
                    "A": {
                        "begin_date": "2017-06-01",
                        "end_date": "2017-06-15",
                        "grant": "grant1",
                        "loading": 1.0,
                        "type": "pd",
                    },
                    "B": {
                        "begin_date": "2017-06-16",
                        "end_date": "2017-06-30",
                        "grant": "grant2",
                        "loading": 1.0,
                        "type": "pd",
                    },
                },
            },
            "2017-06-01",
            "2017-06-30",
            True,
        ),
        (
            {
                "name": "Ludwig Wittgenstein",
                "_id": "lwittgenstein",
                "appointments": {
                    "A": {
                        "begin_date": "2017-06-01",
                        "end_date": "2017-06-15",
                        "grant": "grant1",
                        "loading": 1.0,
                        "type": "pd",
                    },
                    "B": {
                        "begin_date": "2017-06-17",
                        "end_date": "2017-06-30",
                        "grant": "grant2",
                        "loading": 1.0,
                        "type": "pd",
                    },
                    "C": {
                        "begin_date": "2017-07-01",
                        "end_date": "2017-07-30",
                        "grant": "grant3",
                        "loading": 1.0,
                        "type": "pd",
                    },
                },
            },
            "2017-06-01",
            "2017-06-30",
            False,
        ),
        (
            {
                "name": "Buckminster Fuller",
                "_id": "bfuller",
                "appointments": {
                    "A": {
                        "begin_date": "2017-06-01",
                        "end_date": "2017-06-30",
                        "grant": "grant1",
                        "loading": 1.0,
                        "type": "pd",
                    },
                    "B": {
                        "begin_date": "2017-06-17",
                        "end_date": "2017-06-30",
                        "grant": "grant2",
                        "loading": 1.0,
                        "type": "pd",
                    },
                },
            },
            "2017-06-01",
            "2017-06-30",
            False,
        ),
        (
            {
                "name": "Lorem Ipsum",
                "_id": "lipsum",
                "appointments": {
                    "A": {
                        "begin_date": "2017-06-01",
                        "end_date": "2017-06-30",
                        "grant": "grant1",
                        "loading": 1.0,
                        "type": "pd",
                    },
                    "B": {
                        "begin_date": "2017-06-17",
                        "end_date": "2017-06-30",
                        "grant": "grant2",
                        "loading": 1.0,
                        "type": "pd",
                    },
                },
            },
            "2017-06-01",
            "2017-06-30",
            False,
        ),
    ],
)
def test_is_fully_appointed(appts, start, end, expected):
    actual = is_fully_appointed(appts, start, end)
    assert actual == expected


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            "honors",
            [
                {"description": "Omega Laser User's Group Travel Award (\\$1,100)", "year": 2013, "_key": 2013.0},
            ],
        ),
        (
            "service",
            [
                {"_key": 2020.01, "description": "International Steering Committee", "year": 2020},
                {"description": "Omega Laser User's Group Travel Award (\\$1,100)", "year": 2013, "_key": 2013.0},
            ],
        ),
    ],
)
def test_awards_grants_honors(input, expected):
    assert awards_grants_honors(PEOPLE_COLL[0], input, funding=True, service_types=None) == expected


@pytest.mark.parametrize(
    "input, expected",
    [
        (([{"_id": "afriend", "aka": ["AB Friend", "Tony Friend"], "name": "Anthony B Friend"}], "Simon"), None),
        (
            (
                [{"_id": "afriend", "aka": ["AB Friend", "Tony Friend"], "name": "Anthony B Friend"}],
                "Anthony B Friend",
            ),
            "afriend",
        ),
        (
            (
                [
                    {"_id": "afriend", "aka": ["AB Friend", "Tony Friend"], "name": "Anthony B Friend"},
                    {"_id": "aeinstein", "aka": ["Einstein"], "name": "Albert Einstein"},
                ],
                "Albert Einstein",
            ),
            "aeinstein",
        ),
    ],
)
def test_get_id_from_name(input, expected):
    assert get_id_from_name(input[0], input[1]) == expected


@pytest.mark.parametrize(
    "input, expected",
    [
        ((2012, "Jan", 18), "Wed, 18 Jan 2012 00:00:00 -0000"),
        ((2020, 6, 22), "Mon, 22 Jun 2020 00:00:00 -0000"),
    ],
)
def test_date_to_rfc822(input, expected):
    assert date_to_rfc822(input[0], input[1], input[2]) == expected


person1 = {
    "_id": "scopatz",
    "aka": [
        "Scopatz",
        "Scopatz, A",
        "Scopatz, A.",
        "Scopatz, A M",
        "Anthony Michael Scopatz",
    ],
    "name": "Anthony Scopatz",
    "position": "Professor",
}
person2 = {
    "_id": "abc",
    "aka": [
        "A. BC",
        "BC, A",
        "Anthony BC",
    ],
    "name": "Anthony Bill Chris",
    "position": "Professor",
}
person3 = {
    "_id": "jdoe",
    "aka": [
        "A. BC",
        "BC, A",
        "Anthony BC",
    ],
    "name": "John Doe",
}
people = [person1, person2, person3]


@pytest.mark.parametrize(
    "input, expected",
    [
        ((people, ["name", "Doe"]), [person3]),
        ((people, ["name", "Jerry"]), []),
        ((people, ["position", "Prof"]), [person1, person2]),
        ((people, ["position", "Prof", "name", "Chris"]), [person2]),
    ],
)
def test_key_value_pair_filter(input, expected):
    assert key_value_pair_filter(input[0], input[1]) == expected


@pytest.mark.parametrize(
    "input, expected",
    [
        (([person3], None), "jdoe    \n"),
        (([], None), ""),
        (
            ([person1, person2], ["position"]),
            "scopatz    position: Professor    \nabc    position: Professor    \n",
        ),
        (([person2], ["position"]), "abc    position: Professor    \n"),
    ],
)
def test_collection_str(input, expected):
    assert collection_str(input[0], input[1]) == expected


@pytest.mark.parametrize(
    "input, expected",
    [
        ((people, ["name", "Doe"], None), "jdoe    \n"),
        ((people, ["name", "Jerry"], None), ""),
        ((people, ["position", "Prof", "name", "Chris"], None), "abc    \n"),
        ((people, ["position", "prof", "name", "Chris"], ["position"]), "abc    position: Professor    \n"),
    ],
)
def test_search_collection(input, expected):
    assert search_collection(input[0], input[1], input[2]) == expected


appointed_people = [
    {
        "name": "Kurt Godel",
        "_id": "kgodel",
        "appointments": {
            "A": {
                "begin_date": "2019-09-01",
                "end_date": "2019-09-10",
                "grant": "grant1",
                "loading": 0.5,
                "type": "gra",
            },
            "B": {
                "_id": "B",
                "begin_date": "2019-09-01",
                "end_date": "2019-09-10",
                "grant": "grant1",
                "loading": 0.25,
                "type": "gra",
            },
            "C": {
                "_id": "C",
                "begin_date": "2019-09-01",
                "end_date": "2019-09-10",
                "grant": "grant1",
                "loading": 0.25,
                "type": "gra",
            },
        },
        "employment": [
            {"group": "permutation", "begin_date": "2014-06-01", "end_date": "2015-06-01", "status": "phd"},
            {"group": "matrix", "begin_year": "2020", "end_day": "5", "end_month": "12", "end_year": "2020"},
            {
                "group": "permutation",
                "begin_day": 4,
                "begin_month": 9,
                "begin_year": 2012,
                "end_day": 5,
                "end_month": 9,
                "end_year": 2012,
                "permanent": "true",
            },
        ],
    },
    {
        "name": "MC Escher",
        "_id": "mcescher",
        "appointments": {
            "A": {
                "begin_date": "2019-10-01",
                "end_date": "2019-10-31",
                "grant": "grant1",
                "loading": 1.0,
                "type": "ss",
            },
            "B": {
                "begin_date": "2019-11-01",
                "end_date": "2019-11-30",
                "grant": "grant2",
                "loading": 0.5,
                "type": "ss",
            },
            "C": {
                "begin_date": "2019-11-01",
                "end_date": "2019-11-30",
                "grant": "grant3",
                "loading": 0.5,
                "type": "ss",
            },
        },
        "employment": [
            {
                "group": "transformation",
                "begin_date": "2018-07-24",
                "end_date": dt.date(2020, 8, 1),
                "status": "postdoc",
            },
            {"group": "abstract", "begin_year": 2010, "end_day": 5, "end_month": 12, "end_year": 2020},
            {"group": "abstract", "begin_date": "2012-06-30", "end_date": "2012-09-05"},
        ],
    },
    {
        "name": "Johann Sebastian Bach",
        "_id": "jsbach",
        "appointments": {
            "A": {
                "begin_date": "2019-12-01",
                "end_date": "2020-12-15",
                "grant": "grant1",
                "loading": 0.9,
                "type": "pd",
            },
            "B": {
                "begin_date": "2019-12-16",
                "end_date": "2020-12-31",
                "grant": "grant2",
                "loading": 0.9,
                "type": "pd",
            },
            "C": {
                "begin_date": "2019-12-01",
                "end_date": "2020-12-31",
                "grant": "grant3",
                "loading": 0.1,
                "type": "pd",
            },
        },
        "employment": [{"group": "bg", "begin_date": "2019-02-03"}],
    },
    {
        "name": "Ludwig Wittgenstein",
        "_id": "lwittgenstein",
        "appointments": {
            "A": {
                "begin_date": "2019-12-10",
                "end_date": "2019-12-20",
                "grant": "grant2",
                "loading": 1.0,
                "type": "ss",
            }
        },
    },
    {
        "name": "Karl Popper",
        "_id": "kpopper",
        "appointments": {
            "A": {
                "begin_date": "2019-12-25",
                "end_date": "2019-12-31",
                "grant": "grant2",
                "loading": 1.0,
                "type": "ss",
            }
        },
    },
    {"name": "GEM Anscombe", "_id": "ganscombe", "appointments": {}},
    {
        "name": "Sophie Germain",
        "_id": "sgermain",
        "appointments": {
            "A": {
                "begin_date": "2019-09-02",
                "end_date": "2019-09-06",
                "grant": "grant4",
                "loading": 1.0,
                "type": "ss",
            }
        },
    },
]


@pytest.mark.parametrize(
    "people,key,value,start,end,expected",
    [
        (
            appointed_people,
            "grant",
            "grant1",
            None,
            None,
            [
                {
                    "person": "kgodel",
                    "_id": "A",
                    "begin_date": "2019-09-01",
                    "end_date": "2019-09-10",
                    "grant": "grant1",
                    "loading": 0.5,
                    "type": "gra",
                },
                {
                    "person": "kgodel",
                    "_id": "B",
                    "begin_date": "2019-09-01",
                    "end_date": "2019-09-10",
                    "grant": "grant1",
                    "loading": 0.25,
                    "type": "gra",
                },
                {
                    "person": "kgodel",
                    "_id": "C",
                    "begin_date": "2019-09-01",
                    "end_date": "2019-09-10",
                    "grant": "grant1",
                    "loading": 0.25,
                    "type": "gra",
                },
                {
                    "person": "mcescher",
                    "_id": "A",
                    "begin_date": "2019-10-01",
                    "end_date": "2019-10-31",
                    "grant": "grant1",
                    "loading": 1.0,
                    "type": "ss",
                },
                {
                    "person": "jsbach",
                    "_id": "A",
                    "begin_date": "2019-12-01",
                    "end_date": "2020-12-15",
                    "grant": "grant1",
                    "loading": 0.9,
                    "type": "pd",
                },
            ],
        ),
        (
            appointed_people,
            None,
            None,
            "2019-09-01",
            "2019-09-30",
            [
                {
                    "person": "kgodel",
                    "_id": "A",
                    "begin_date": "2019-09-01",
                    "end_date": "2019-09-10",
                    "grant": "grant1",
                    "loading": 0.5,
                    "type": "gra",
                },
                {
                    "person": "kgodel",
                    "_id": "B",
                    "begin_date": "2019-09-01",
                    "end_date": "2019-09-10",
                    "grant": "grant1",
                    "loading": 0.25,
                    "type": "gra",
                },
                {
                    "person": "kgodel",
                    "_id": "C",
                    "begin_date": "2019-09-01",
                    "end_date": "2019-09-10",
                    "grant": "grant1",
                    "loading": 0.25,
                    "type": "gra",
                },
                {
                    "person": "sgermain",
                    "_id": "A",
                    "begin_date": "2019-09-02",
                    "end_date": "2019-09-06",
                    "grant": "grant4",
                    "loading": 1.0,
                    "type": "ss",
                },
            ],
        ),
        (
            appointed_people,
            ["loading", "type"],
            [1.0, "ss"],
            "2019-12-15",
            "2019-12-25",
            [
                {
                    "person": "lwittgenstein",
                    "_id": "A",
                    "begin_date": "2019-12-10",
                    "end_date": "2019-12-20",
                    "grant": "grant2",
                    "loading": 1.0,
                    "type": "ss",
                },
                {
                    "person": "kpopper",
                    "_id": "A",
                    "begin_date": "2019-12-25",
                    "end_date": "2019-12-31",
                    "grant": "grant2",
                    "loading": 1.0,
                    "type": "ss",
                },
            ],
        ),
        (appointed_people, ["loading", "type", "grant"], [0.9, "pd", "grant3"], None, None, []),
        (
            appointed_people,
            None,
            None,
            None,
            None,
            [
                {
                    "person": "kgodel",
                    "_id": "A",
                    "begin_date": "2019-09-01",
                    "end_date": "2019-09-10",
                    "grant": "grant1",
                    "loading": 0.5,
                    "type": "gra",
                },
                {
                    "person": "kgodel",
                    "_id": "B",
                    "begin_date": "2019-09-01",
                    "end_date": "2019-09-10",
                    "grant": "grant1",
                    "loading": 0.25,
                    "type": "gra",
                },
                {
                    "person": "kgodel",
                    "_id": "C",
                    "begin_date": "2019-09-01",
                    "end_date": "2019-09-10",
                    "grant": "grant1",
                    "loading": 0.25,
                    "type": "gra",
                },
                {
                    "person": "mcescher",
                    "_id": "A",
                    "begin_date": "2019-10-01",
                    "end_date": "2019-10-31",
                    "grant": "grant1",
                    "loading": 1.0,
                    "type": "ss",
                },
                {
                    "person": "mcescher",
                    "_id": "B",
                    "begin_date": "2019-11-01",
                    "end_date": "2019-11-30",
                    "grant": "grant2",
                    "loading": 0.5,
                    "type": "ss",
                },
                {
                    "person": "mcescher",
                    "_id": "C",
                    "begin_date": "2019-11-01",
                    "end_date": "2019-11-30",
                    "grant": "grant3",
                    "loading": 0.5,
                    "type": "ss",
                },
                {
                    "person": "jsbach",
                    "_id": "A",
                    "begin_date": "2019-12-01",
                    "end_date": "2020-12-15",
                    "grant": "grant1",
                    "loading": 0.9,
                    "type": "pd",
                },
                {
                    "person": "jsbach",
                    "_id": "B",
                    "begin_date": "2019-12-16",
                    "end_date": "2020-12-31",
                    "grant": "grant2",
                    "loading": 0.9,
                    "type": "pd",
                },
                {
                    "person": "jsbach",
                    "_id": "C",
                    "begin_date": "2019-12-01",
                    "end_date": "2020-12-31",
                    "grant": "grant3",
                    "loading": 0.1,
                    "type": "pd",
                },
                {
                    "person": "lwittgenstein",
                    "_id": "A",
                    "begin_date": "2019-12-10",
                    "end_date": "2019-12-20",
                    "grant": "grant2",
                    "loading": 1.0,
                    "type": "ss",
                },
                {
                    "person": "kpopper",
                    "_id": "A",
                    "begin_date": "2019-12-25",
                    "end_date": "2019-12-31",
                    "grant": "grant2",
                    "loading": 1.0,
                    "type": "ss",
                },
                {
                    "person": "sgermain",
                    "_id": "A",
                    "begin_date": "2019-09-02",
                    "end_date": "2019-09-06",
                    "grant": "grant4",
                    "loading": 1.0,
                    "type": "ss",
                },
            ],
        ),
        (appointed_people, "type", "ss", "2019-10-21", "2019-09-01", "begin date is after end date"),
        (
            appointed_people,
            ["type", "loading"],
            None,
            None,
            None,
            "number of filter keys and filter values do not match",
        ),
        (
            appointed_people,
            "type",
            "pd",
            "2019-12-10",
            None,
            "please enter both begin date and end date or neither",
        ),
        (
            [
                {
                    "name": "Magical Person",
                    "_id": "mperson",
                    "appointments": {
                        "A": {
                            "begin_date": "2019-09-01",
                            "end_date": "2019-09-05",
                            "loading": 1.0,
                            "grant": "grant1",
                            "type": "imaginary",
                        }
                    },
                }
            ],
            None,
            None,
            None,
            None,
            "invalid  type imaginary for appointment A of mperson",
        ),
    ],
)
def test_collect_appts(people, key, value, start, end, expected):
    try:
        actual = collect_appts(people, filter_key=key, filter_value=value, begin_date=start, end_date=end)
        assert actual == expected
    except ValueError:
        with pytest.raises(ValueError) as excinfo:
            actual = collect_appts(people, filter_key=key, filter_value=value, begin_date=start, end_date=end)
        assert str(excinfo.value) == expected
    except RuntimeError:
        with pytest.raises(RuntimeError) as excinfo:
            actual = collect_appts(people, filter_key=key, filter_value=value, begin_date=start, end_date=end)
        assert str(excinfo.value) == expected


appts = collect_appts(appointed_people)
grant1 = {
    "_id": "grant1",
    "alias": "grant_one",
    "budget": [
        {
            "begin_date": "2019-09-01",
            "end_date": "2019-09-03",
            "student_months": 1,
            "postdoc_months": 0.5,
            "ss_months": 0,
        },
        {
            "begin_date": "2019-09-04",
            "end_date": "2019-09-07",
            "student_months": 1.5,
            "postdoc_months": 0,
            "ss_months": 0,
        },
        {
            "begin_date": "2019-09-08",
            "end_date": "2019-09-10",
            "student_months": 2,
            "postdoc_months": 1.5,
            "ss_months": 0,
        },
    ],
}
grant2 = {
    "_id": "grant2",
    "alias": "grant_two",
    "budget": [
        {
            "begin_date": "2019-09-01",
            "end_date": "2019-12-31",
            "student_months": 4,
            "postdoc_months": 2.5,
            "ss_months": 1,
        }
    ],
}
grant3 = {
    "_id": "grant3",
    "budget": [
        {
            "begin_date": "2019-09-01",
            "end_date": "2019-10-31",
            "student_months": 0,
            "postdoc_months": 1,
            "ss_months": 2,
        },
        {
            "begin_date": "2019-11-01",
            "end_date": "2019-12-31",
            "student_months": 2,
            "postdoc_months": 0.5,
            "ss_months": 0,
        },
    ],
}
grant4 = {
    "_id": "grant4",
    "alias": "grant_four",
    "budget": [
        {
            "begin_date": "2019-09-01",
            "end_date": "2019-09-07",
            "student_months": 1,
            "postdoc_months": 1,
            "ss_months": 1,
        }
    ],
}


@pytest.mark.parametrize(
    "grant,appointments,start,end,expected",
    [
        (
            grant1,
            appts,
            None,
            None,
            {
                dt.date(2019, 9, 1): {"postdoc_days": 15.25, "ss_days": 0.0, "student_days": 29.5},
                dt.date(2019, 9, 2): {"postdoc_days": 15.25, "ss_days": 0.0, "student_days": 28.5},
                dt.date(2019, 9, 3): {"postdoc_days": 15.25, "ss_days": 0.0, "student_days": 27.5},
                dt.date(2019, 9, 4): {"postdoc_days": 15.25, "ss_days": 0.0, "student_days": 72.25},
                dt.date(2019, 9, 5): {"postdoc_days": 15.25, "ss_days": 0.0, "student_days": 71.25},
                dt.date(2019, 9, 6): {"postdoc_days": 15.25, "ss_days": 0.0, "student_days": 70.25},
                dt.date(2019, 9, 7): {"postdoc_days": 15.25, "ss_days": 0.0, "student_days": 69.25},
                dt.date(2019, 9, 8): {"postdoc_days": 61.0, "ss_days": 0.0, "student_days": 129.25},
                dt.date(2019, 9, 9): {"postdoc_days": 61.0, "ss_days": 0.0, "student_days": 128.25},
                dt.date(2019, 9, 10): {"postdoc_days": 61.0, "ss_days": 0.0, "student_days": 127.25},
            },
        ),
        (
            grant2,
            appts,
            "2019-12-15",
            "2019-12-31",
            {
                dt.date(2019, 12, 15): {"postdoc_days": 76.25, "ss_days": 9.5, "student_days": 122.0},
                dt.date(2019, 12, 16): {"postdoc_days": 75.35, "ss_days": 8.5, "student_days": 122.0},
                dt.date(2019, 12, 17): {"postdoc_days": 74.45, "ss_days": 7.5, "student_days": 122.0},
                dt.date(2019, 12, 18): {"postdoc_days": 73.55, "ss_days": 6.5, "student_days": 122.0},
                dt.date(2019, 12, 19): {"postdoc_days": 72.65, "ss_days": 5.5, "student_days": 122.0},
                dt.date(2019, 12, 20): {"postdoc_days": 71.75, "ss_days": 4.5, "student_days": 122.0},
                dt.date(2019, 12, 21): {"postdoc_days": 70.85, "ss_days": 4.5, "student_days": 122.0},
                dt.date(2019, 12, 22): {"postdoc_days": 69.95, "ss_days": 4.5, "student_days": 122.0},
                dt.date(2019, 12, 23): {"postdoc_days": 69.05, "ss_days": 4.5, "student_days": 122.0},
                dt.date(2019, 12, 24): {"postdoc_days": 68.15, "ss_days": 4.5, "student_days": 122.0},
                dt.date(2019, 12, 25): {"postdoc_days": 67.25, "ss_days": 3.5, "student_days": 122.0},
                dt.date(2019, 12, 26): {"postdoc_days": 66.35, "ss_days": 2.5, "student_days": 122.0},
                dt.date(2019, 12, 27): {"postdoc_days": 65.45, "ss_days": 1.5, "student_days": 122.0},
                dt.date(2019, 12, 28): {"postdoc_days": 64.55, "ss_days": 0.5, "student_days": 122.0},
                dt.date(2019, 12, 29): {"postdoc_days": 63.65, "ss_days": -0.5, "student_days": 122.0},
                dt.date(2019, 12, 30): {"postdoc_days": 62.75, "ss_days": -1.5, "student_days": 122.0},
                dt.date(2019, 12, 31): {"postdoc_days": 61.85, "ss_days": -2.5, "student_days": 122.0},
            },
        ),
        (
            grant3,
            appts,
            "2019-12-31",
            "2019-12-31",
            {dt.date(2019, 12, 31): {"postdoc_days": 42.65, "ss_days": 46.0, "student_days": 61.0}},
        ),
        (
            grant4,
            appts,
            None,
            None,
            {
                dt.date(2019, 9, 1): {"postdoc_days": 30.5, "ss_days": 30.5, "student_days": 30.5},
                dt.date(2019, 9, 2): {"postdoc_days": 30.5, "ss_days": 29.5, "student_days": 30.5},
                dt.date(2019, 9, 3): {"postdoc_days": 30.5, "ss_days": 28.5, "student_days": 30.5},
                dt.date(2019, 9, 4): {"postdoc_days": 30.5, "ss_days": 27.5, "student_days": 30.5},
                dt.date(2019, 9, 5): {"postdoc_days": 30.5, "ss_days": 26.5, "student_days": 30.5},
                dt.date(2019, 9, 6): {"postdoc_days": 30.5, "ss_days": 25.5, "student_days": 30.5},
                dt.date(2019, 9, 7): {"postdoc_days": 30.5, "ss_days": 25.5, "student_days": 30.5},
            },
        ),
        (
            {"_id": "magical_grant", "alias": "very_magical_grant"},
            appts,
            "2012-12-23",
            "2013-01-24",
            "magical_grant has no specified budget",
        ),
        (
            grant4,
            appointed_people[0].get("appointments"),
            None,
            None,
            {
                dt.date(2019, 9, 1): {"postdoc_days": 30.5, "ss_days": 30.5, "student_days": 30.5},
                dt.date(2019, 9, 2): {"postdoc_days": 30.5, "ss_days": 30.5, "student_days": 30.5},
                dt.date(2019, 9, 3): {"postdoc_days": 30.5, "ss_days": 30.5, "student_days": 30.5},
                dt.date(2019, 9, 4): {"postdoc_days": 30.5, "ss_days": 30.5, "student_days": 30.5},
                dt.date(2019, 9, 5): {"postdoc_days": 30.5, "ss_days": 30.5, "student_days": 30.5},
                dt.date(2019, 9, 6): {"postdoc_days": 30.5, "ss_days": 30.5, "student_days": 30.5},
                dt.date(2019, 9, 7): {"postdoc_days": 30.5, "ss_days": 30.5, "student_days": 30.5},
            },
        ),
    ],
)
def test_grant_burn(grant, appointments, start, end, expected):
    try:
        actual = grant_burn(grant, appointments, begin_date=start, end_date=end)
        assert actual == expected
    except ValueError:
        with pytest.raises(ValueError) as excinfo:
            actual = grant_burn(grant, appointments, begin_date=start, end_date=end)
        assert str(excinfo.value) == expected


meeting1 = {"_id": "grp2020-06-15", "journal_club": {"doi": "TBD"}}
meeting2 = {"_id": "grp2020-06-22", "presentation": {"link": "TBD"}}
meeting3 = {"_id": "grp2020-06-29", "presentation": {"link": "2002ak_grmtg_presnetation", "title": "tbd"}}


@pytest.mark.parametrize(
    "meeting,date,expected",
    [
        (meeting1, dt.date(2020, 8, 15), "grp2020-06-15 does not have a journal club doi"),
        (meeting1, dt.date(2020, 5, 15), None),
        (meeting2, dt.date(2020, 8, 15), "grp2020-06-22 does not have a presentation link"),
        (meeting2, dt.date(2020, 5, 15), None),
        (meeting3, dt.date(2020, 8, 15), "grp2020-06-29 does not have a presentation title"),
        (meeting3, dt.date(2020, 5, 15), None),
    ],
)
def test_validate_meeting(meeting, date, expected):
    try:
        actual = validate_meeting(meeting, date)
        assert actual == expected
    except ValueError:
        with pytest.raises(ValueError) as excinfo:
            actual = validate_meeting(meeting, date)
        assert str(excinfo.value) == expected


@pytest.mark.parametrize(
    "person,grpname,expected",
    [
        (
            appointed_people[0],
            "permutation",
            [
                {
                    "_id": "kgodel",
                    "begin_date": dt.date(2014, 6, 1),
                    "end_date": dt.date(2015, 6, 1),
                    "status": "phd",
                    "permanent": None,
                },
                {
                    "_id": "kgodel",
                    "begin_date": dt.date(2012, 9, 4),
                    "end_date": dt.date(2012, 9, 5),
                    "status": None,
                    "permanent": "true",
                },
            ],
        ),
        (
            appointed_people[1],
            "transformation",
            [
                {
                    "_id": "mcescher",
                    "begin_date": dt.date(2018, 7, 24),
                    "end_date": dt.date(2020, 8, 1),
                    "status": "postdoc",
                    "permanent": None,
                }
            ],
        ),
        (appointed_people[2], "bg", "WARNING: jsbach has no end date in employment for bg starting 2019-02-03"),
        (appointed_people[3], "abstract", []),
    ],
)
def test_group_member_employment_start_end(person, grpname, expected):
    try:
        actual = group_member_employment_start_end(person, grpname)
        assert actual == expected
    except RuntimeError:
        with pytest.raises(RuntimeError) as excinfo:
            actual = group_member_employment_start_end(person, grpname)
        assert str(excinfo.value) == expected


@pytest.mark.parametrize(
    "inp,expected",
    [
        ([{"dupe_key": 1, "nond": 2}], [{"dupe_key": 1, "nond": 2}]),
        ([{"dupe_key": 1, "nond": 2}, {"dupe_key": 1, "nond": 3}], [{"dupe_key": 1, "nond": 2}]),
        (
            [{"no_dupe_key": 1, "nond": 2}],
            "ERROR: Target key, dupe_key not found in {'no_dupe_key': 1, 'nond': 2}",
        ),
    ],
)
def test_remove_duplicate_docs(inp, expected):
    try:
        actual = remove_duplicate_docs(inp, "dupe_key")
        assert actual == expected
    except RuntimeError:
        with pytest.raises(RuntimeError) as excinfo:
            actual = remove_duplicate_docs(inp, "dupe_key")
        assert str(excinfo.value) == expected


@pytest.mark.parametrize(
    "inp,expected",
    [
        (
            [
                [
                    {
                        "_id": "student",
                        "name": "Lancelot",
                        "employment": [
                            {
                                "status": "ms",
                                "begin_date": "2020-05-05",
                                "end_date": "2020-10-10",
                                "advisor": "awesome",
                                "position": "masters researcher",
                            }
                        ],
                    }
                ],
                "2022-01-01",
            ],
            [],
        ),
        (
            [
                [
                    {
                        "_id": "student",
                        "name": "Lancelot",
                        "employment": [
                            {
                                "status": "ms",
                                "begin_date": "2020-05-05",
                                "end_date": "2020-10-10",
                                "advisor": "awesome",
                                "position": "masters researcher",
                            }
                        ],
                    }
                ],
                "2019-01-01",
            ],
            [
                {
                    "_id": "student",
                    "name": "Lancelot",
                    "employment": [
                        {
                            "status": "ms",
                            "begin_date": "2020-05-05",
                            "end_date": "2020-10-10",
                            "advisor": "awesome",
                            "position": "masters researcher",
                        }
                    ],
                    "role": "masters researcher",
                    "begin_year": 2020,
                    "end_year": 2020,
                    "end_date": dt.date(2020, 10, 10),
                    "status": "ms",
                    "position": "masters researcher",
                }
            ],
        ),
        (
            [
                [
                    {
                        "_id": "student",
                        "name": "Lancelot",
                        "employment": [
                            {
                                "status": "ms",
                                "advisor": "awesome",
                                "begin_date": "2020-05-05",
                                "position": "masters researcher",
                            }
                        ],
                    }
                ],
                "2019-01-01",
            ],
            [
                {
                    "_id": "student",
                    "name": "Lancelot",
                    "employment": [
                        {
                            "status": "ms",
                            "advisor": "awesome",
                            "begin_date": "2020-05-05",
                            "position": "masters researcher",
                        }
                    ],
                    "role": "masters researcher",
                    "begin_year": 2020,
                    "end_year": "present",
                    "end_date": dt.date(2021, 6, 3),
                    "status": "ms",
                    "position": "masters researcher",
                }
            ],
        ),
    ],
)
def test_filter_employment_for_advisees(inp, expected):
    actual = filter_employment_for_advisees(inp[0], inp[1], "ms", "awesome", dt.date(2021, 6, 3))
    assert actual == expected


person1 = {"_id": "tstark", "aka": "iron man", "name": "tony stark"}
person2 = {"_id": "nromanov", "aka": "black widow", "name": "natasha romanov"}
PEOPLE = [person1, person2]

presentation1 = {
    "_id": "abc",
    "authors": "tstark",
    "date": "2018-01-01",
    "department": "apam",
    "institution": "columbiau",
    "status": "accepted",
    "type": "award",
}
presentation2 = {
    "_id": "ghi",
    "authors": ["tstark", "nromanov"],
    "begin_date": "2019-01-02",
    "end_date": "2019-01-08",
    "department": "physics",
    "institution": "rutgersu",
    "status": "cancelled",
    "type": "poster",
}
presentation3 = {
    "_id": "jkl",
    "authors": ["nromanov"],
    "begin_year": 2020,
    "begin_month": 2,
    "begin_day": 2,
    "end_year": 2020,
    "end_month": 12,
    "end_day": 12,
    "department": "math",
    "institution": "rutgersu",
    "status": "declined",
    "type": "webinar",
}
PRESENTATIONS = [presentation1, presentation2, presentation3]

institution1 = {
    "_id": "columbiau",
    "city": "New York",
    "country": "USA",
    "name": "Columbia University",
    "state": "NY",
}
institution2 = {
    "_id": "rutgersu",
    "city": "New Brunswick",
    "country": "USA",
    "name": "Rutgers University",
    "state": "NJ",
}
institution3 = {
    "_id": "barnardc",
    "city": "New York",
    "country": "USA",
    "name": "Barnard College",
    "state": "NY",
    "departments": {"physics": {"name": "Department of Physics", "aka": "Phys"}},
}
institution4 = {
    "_id": "nyu",
    "city": "New York",
    "country": "USA",
    "name": "New York University",
    "state": "NY",
    "street": "23rd",
    "zip": "10001",
    "aka": "purple",
}
institution_overseas = {"_id": "overseasu", "city": "Toronto", "country": "Canada", "name": "Overseas University"}
organization1 = {"_id": "3m", "city": "Minneapolis", "country": "USA", "name": "3M", "state": "MN"}
INSTITUTIONS = [institution1, institution2, institution3, institution4, institution_overseas, organization1]


expected1 = {
    "_id": "abc",
    "authors": "tony stark",
    "begin_day_suffix": "st",
    "begin_year": 2018,
    "begin_month": 1,
    "begin_day": 1,
    "date": dt.date(2018, 1, 1),
    "day_suffix": "st",
    "department": {"name": "apam"},
    "institution": {"city": "New York", "country": "USA", "name": "Columbia University", "state": "NY"},
    "status": "accepted",
    "type": "award",
}
expected2 = {
    "_id": "ghi",
    "authors": "tony stark, natasha romanov",
    "begin_date": "2019-01-02",
    "begin_day_suffix": "nd",
    "begin_year": 2019,
    "begin_month": 1,
    "begin_day": 2,
    "date": dt.date(2019, 1, 2),
    "day_suffix": "nd",
    "end_day": 8,
    "end_day_suffix": "th",
    "department": {"name": "physics"},
    "end_date": "2019-01-08",
    "institution": {"city": "New Brunswick", "country": "USA", "name": "Rutgers University", "state": "NJ"},
    "status": "cancelled",
    "type": "poster",
}
expected3 = {
    "_id": "jkl",
    "authors": "natasha romanov",
    "begin_day": 2,
    "begin_day_suffix": "nd",
    "begin_month": 2,
    "begin_year": 2020,
    "date": dt.date(2020, 2, 2),
    "day_suffix": "nd",
    "department": {"name": "math"},
    "end_day": 12,
    "end_day_suffix": "th",
    "end_month": 12,
    "end_year": 2020,
    "institution": {"city": "New Brunswick", "country": "USA", "name": "Rutgers University", "state": "NJ"},
    "status": "declined",
    "type": "webinar",
}


@pytest.mark.parametrize(
    "input, expected, sysout",
    [
        (
            {"institution": "columbiau"},
            {
                "department": "unknown",
                "location": "New York, NY",
                "city": "New York",
                "country": "USA",
                "institution": "Columbia University",
                "organization": "Columbia University",
                "state": "NY",
            },
            "",
        ),
        (
            {"institution": "nyu"},
            {
                "department": "unknown",
                "location": "New York, NY",
                "city": "New York",
                "country": "USA",
                "institution": "New York University",
                "organization": "New York University",
                "state": "NY",
                "street": "23rd",
                "zip": "10001",
                "aka": "purple",
            },
            "",
        ),
        (
            {"institution": "barnardc", "department": "physics"},
            {
                "location": "New York, NY",
                "city": "New York",
                "country": "USA",
                "institution": "Barnard College",
                "organization": "Barnard College",
                "state": "NY",
                "department": "Department of Physics",
            },
            "",
        ),
        (
            {"institution": "columbiau", "department": "physics"},
            {
                "location": "New York, NY",
                "city": "New York",
                "country": "USA",
                "institution": "Columbia University",
                "organization": "Columbia University",
                "state": "NY",
                "department": "physics",
            },
            "WARNING: no departments in columbiau. physics sought\n",
        ),
        (
            {"organization": "3m"},
            {
                "department": "unknown",
                "location": "Minneapolis, MN",
                "city": "Minneapolis",
                "country": "USA",
                "institution": "3M",
                "organization": "3M",
                "state": "MN",
            },
            "",
        ),
        (
            {"institution": "notindbu"},
            {
                "location": "unknown, unknown",
                "city": "unknown",
                "country": "unknown",
                "institution": "notindbu",
                "department": "unknown",
                "organization": "notindbu",
                "state": "unknown",
            },
            "WARNING: notindbu not found in institutions\n",
        ),
        (
            {"institution": "notindbu", "location": "Near, BY"},
            {
                "location": "Near, BY",
                "city": "unknown",
                "country": "unknown",
                "institution": "notindbu",
                "department": "unknown",
                "organization": "notindbu",
                "state": "unknown",
            },
            "WARNING: notindbu not found in institutions\n",
        ),
        (
            {"institution": "notindbu", "city": "Near", "state": "BY"},
            {
                "location": "Near, BY",
                "city": "Near",
                "country": "unknown",
                "institution": "notindbu",
                "department": "unknown",
                "organization": "notindbu",
                "state": "BY",
            },
            "WARNING: notindbu not found in institutions\n",
        ),
        (
            {"institution": "overseasu"},
            {
                "location": "Toronto, Canada",
                "city": "Toronto",
                "country": "Canada",
                "department": "unknown",
                "institution": "Overseas University",
                "organization": "Overseas University",
            },
            "",
        ),
        (
            {"degree": "phd"},
            {"degree": "phd"},
            "WARNING: no institution or organization in entry: {'degree': 'phd'}\n",
        ),
    ],
)
def test_dereference_institution(input, expected, sysout, capsys):
    dereference_institution(input, INSTITUTIONS, verbose=True)
    assert expected == input
    out, err = capsys.readouterr()
    assert sysout == out


@pytest.mark.parametrize(
    "args, kwargs, expected",
    [
        # this tests no kwargs
        ([PEOPLE, PRESENTATIONS, INSTITUTIONS, "tstark"], {}, [expected1]),
        # this tests 'statuses' kwarg
        ([PEOPLE, PRESENTATIONS, INSTITUTIONS, "tstark"], {"statuses": ["all"]}, [expected2, expected1]),
        # this tests 'statuses' and 'types' kwargs together
        ([PEOPLE, PRESENTATIONS, INSTITUTIONS, "tstark"], {"statuses": ["all"], "types": ["poster"]}, [expected2]),
        # this tests 'statuses' and 'since' kwargs together
        (
            [PEOPLE, PRESENTATIONS, INSTITUTIONS, "nromanov"],
            {"statuses": ["all"], "since": dt.date(2019, 1, 1)},
            [expected3, expected2],
        ),
        # this tests the 'statuses' and 'before' kwargs together
        (
            [PEOPLE, PRESENTATIONS, INSTITUTIONS, "tstark"],
            {"statuses": ["all"], "before": dt.date(2018, 1, 2)},
            [expected1],
        ),
    ],
)
def test_filter_presentations(args, kwargs, expected):
    actual = filter_presentations(*args, **kwargs)
    assert actual == expected

person3 = {"_id": "sbillinge", "aka": "Simon", "name": "Simon Billinge"}
person4 = {"_id": "stevenhua0320", "aka": "Steven hua", "name": "Rundong Hua"}
PEOPLE = [person3, person4]
software1 = {
            "_id": "diffpy.utils",
            "groups": ["xrd"],
            "active": True,
            "org_name": "diffpy",
            "repo_name": "diffpy.utils",
            "platform_name": "Github",
            "grants": ["NSF Funding"],
            "program_description": "General utilities for analyzing diffraction data",
            "author": ["Simon Billinge", "Sanjoon Bob Lee", "Zhiming Xu", "Tieqiong Zhang"],
            "release": [
                {
                    "major": 3,
                    "minor": 1,
                    "patch": 0,
                    "release_type": "major",
                    "release_date": "2025-10-25",
                    "summary": "Python 3.14 and something else",
                    "changes": ["deprecated python2 feature.",
                                "changed to scikit-packaged standard.",
                                "Add some functionality.",
                                "Modify existing function to make convenient."
                    ],
                    "release_id": "3.1.0"
                }
            ]
        }
software2 = {
            "_id": "diffpy.srxplanar",
            "groups": ["billingegroup"],
            "active": True,
            "author": ["Xiaohao Yang", "Rundong Hua","Zhiming Xu", "Simon Billinge"],
            "org_name": "diffpy",
            "repo_name": "diffpy.srxplanar",
            "platform_name": "Github",
            "grants": ["NSF Funding"],
            "program_description": "2D diffraction image integration using non splitting pixel algorithm.",
            "release": [
                {
                    "major": 1,
                    "minor": 0,
                    "patch": 1,
                    "release_type": "major",
                    "release_date": "2025-10-26",
                    "summary": "Python 3.14 and something else",
                    "changes": [],
                    "release_id": "1.0.0"
                },
                {
                    "major": 0,
                    "minor": 1,
                    "patch": 1,
                    "release_type": "pre-release",
                    "pre_release": 2,
                    "release_date": "2025-10-20",
                    "summary": "Package pre-release",
                    "changes": ["change package to scikit-package level-5 standard."],
                    "release_id": "0.1.1-rc.2"
                }
            ]
        }
software3 = {
            "_id": "diffpy.distanceprinter",
            "groups": ["billingegroup"],
            "active": False,
            "org_name": "diffpy",
            "repo_name": "diffpy.distanceprinter",
            "platform_name": "Github",
            "grants": ["NSF Funding"],
            "program_description": "Distance Printer, calculate the inter atomic distances. Part of xPDFsuite",
            "author": ["Xiaohao Yang", "Dasun Abeykoon", "Simon Billinge"],
            "release": [
                {
                    "major": 0,
                    "minor": 1,
                    "patch": 0,
                    "release_type": "minor",
                    "release_date": "2025-10-26",
                    "summary": "Python 3.14 and something else",
                    "changes": [],
                    "release_id": "1.0.0"
                }
            ]
        }
SOFTWARE = [software1, software2, software3]

expected4 = {
  '_id': 'diffpy.srxplanar',
  'active': True,
  'author': ['Xiaohao Yang', 'Rundong Hua', 'Zhiming Xu', 'Simon Billinge'],
  'authors': 'Xiaohao Yang, Rundong Hua, Zhiming Xu, Simon Billinge',
  'grants': ['NSF Funding'],
  'groups': ['billingegroup'],
  'org_name': 'diffpy',
  'platform_name': 'Github',
  'program_description': '2D diffraction image integration using non splitting '
                         'pixel algorithm.',
  'release': [{'changes': [],
               'major': 1,
               'minor': 0,
               'patch': 1,
               'release_date': "2025-10-26",
               'release_id': '1.0.0',
               'release_type': 'major',
               'summary': 'Python 3.14 and something else'},
              {'changes': ['change package to scikit-package level-5 '
                           'standard.'],
               'major': 0,
               'minor': 1,
               'patch': 1,
               'pre_release': 2,
               'release_date': "2025-10-20",
               'release_id': '0.1.1-rc.2',
               'release_type': 'pre-release',
               'summary': 'Package pre-release'}],
               'repo_name': 'diffpy.srxplanar'}

expected5 =  {
  '_id': 'diffpy.distanceprinter',
  'active': False,
  'author': ['Xiaohao Yang', 'Dasun Abeykoon', 'Simon Billinge'],
  'authors': 'Xiaohao Yang, Dasun Abeykoon, Simon Billinge',
  'grants': ['NSF Funding'],
  'groups': ['billingegroup'],
  'org_name': 'diffpy',
  'platform_name': 'Github',
  'program_description': 'Distance Printer, calculate the inter atomic '
                         'distances. Part of xPDFsuite',
  'release': [{'changes': [],
               'major': 0,
               'minor': 1,
               'patch': 0,
               'release_date':"2025-10-26",
               'release_id': '1.0.0',
               'release_type': 'minor',
               'summary': 'Python 3.14 and something else'}],
  'repo_name': 'diffpy.distanceprinter'}

expected6 = {'_id': 'diffpy.utils',
  'active': True,
  'author': ['Simon Billinge',
             'Sanjoon Bob Lee',
             'Zhiming Xu',
             'Tieqiong Zhang'],
  'authors': 'Simon Billinge, Sanjoon Bob Lee, Zhiming Xu, Tieqiong Zhang',
  'grants': ['NSF Funding'],
  'groups': ['xrd'],
  'org_name': 'diffpy',
  'platform_name': 'Github',
  'program_description': 'General utilities for analyzing diffraction data',
  'release': [{'changes': ['deprecated python2 feature.',
                           'changed to scikit-packaged standard.',
                           'Add some functionality.',
                           'Modify existing function to make convenient.'],
               'major': 3,
               'minor': 1,
               'patch': 0,
               'release_date': "2025-10-25",
               'release_id': '3.1.0',
               'release_type': 'major',
               'summary': 'Python 3.14 and something else'}],
  'repo_name': 'diffpy.utils'}

expected7 = {
  '_id': 'diffpy.srxplanar',
  'active': True,
  'author': ['Xiaohao Yang', 'Rundong Hua', 'Zhiming Xu', 'Simon Billinge'],
  'authors': 'Xiaohao Yang, Rundong Hua, Zhiming Xu, Simon Billinge',
  'grants': ['NSF Funding'],
  'groups': ['billingegroup'],
  'org_name': 'diffpy',
  'platform_name': 'Github',
  'program_description': '2D diffraction image integration using non splitting '
                         'pixel algorithm.',
  'release': [{'changes': [],
               'major': 1,
               'minor': 0,
               'patch': 1,
               'release_date': "2025-10-26",
               'release_id': '1.0.0',
               'release_type': 'major',
               'summary': 'Python 3.14 and something else'},
              ],
               'repo_name': 'diffpy.srxplanar'}

@pytest.mark.parametrize(
    "args, kwargs, expected",
    [
        # this tests no kwargs
        ([PEOPLE, SOFTWARE, "sbillinge"], {}, [expected4, expected5, expected6]),
        # this tests 'statuses' kwarg
        ([PEOPLE, SOFTWARE, "sbillinge"], {"active": True}, [expected4, expected6]),
        # this tests 'active' and 'types' kwargs together
        ([PEOPLE, SOFTWARE, "stevenhua0320"], {"active": True, "types": ["major"]}, [expected7]),
        # this tests 'active' and 'since' kwargs together
        (
            [PEOPLE, SOFTWARE, "sbillinge"],
            {"active": True, "since": "2025-10-21"},
            [expected7, expected6],
        ),
        # this tests the 'active' and 'before' kwargs together
        (
            [PEOPLE, SOFTWARE, "sbillinge"],
            {"active": True, "before": "2025-10-30"},
            [expected4, expected6],
        ),
    ],
)

def test_filter_software(args, kwargs, expected):
    actual = filter_software(*args, **kwargs)
    assert actual == expected

@pytest.mark.parametrize(
    "coll, expected",
    [
        ([{"_id": "id", "name": "test"}], []),
        ([{"_id": "id", "tags": ""}], []),
        ([{"_id": "id", "tags": "thing1"}], ["thing1"]),
        ([{"_id": "id", "tags": "thing2,thing1"}], ["thing1", "thing2"]),
        ([{"_id": "id", "tags": "thing2 thing1"}], ["thing1", "thing2"]),
        ([{"_id": "id", "tags": "thing2,thing1 thing3"}], ["thing1", "thing2", "thing3"]),
    ],
)
def test_get_tags(coll, expected):
    actual = get_tags(coll)
    assert actual == expected


def test_get_tags_invalid():
    coll = [{"_id": "id", "tags": ["test"]}]
    with pytest.raises(TypeError) as e_info:
        get_tags(coll)
        assert e_info == "ERROR: valid tags are comma or space separated strings of tag names"


@pytest.mark.parametrize(
    "repo_information, expected",
    [
        # good input
        (
            [
                {
                    "_id": "repo1",
                    "params": {"namespace_id": "35", "initialize_with_readme": "false", "name": "repo name "},
                    "url": "https://example.com",
                    "api_route": "/url/example",
                    "namespace_name": "talks",
                }
            ],
            {
                "_id": "repo1",
                "built_url": "https://example.com/url/example",
                "params": {"namespace_id": "35", "initialize_with_readme": "false", "name": "repo_name"},
                "url": "https://example.com",
                "api_route": "/url/example",
                "namespace_name": "talks",
            },
        ),
        ({}, False),
        ([], False),
        # multiple docs with same _id
        ([{"_id": "repo1"}, {"_id": "repo1"}], False),
        # well formulated doc, but wrong id
        (
            [
                {
                    "_id": "wrong_id",
                    "params": {"namespace_id": "35", "initialize_with_readme": "false", "name": "repo name "},
                    "url": "https://example.com/url/example",
                }
            ],
            False,
        ),
        # no params section
        (
            [
                {"_id": "repo1", "url": "https://example.com/url/example"},
            ],
            False,
        ),
        # params section, but empty
        ([{"_id": "repo1", "params": {}, "url": "https://example.com/url/example"}], False),
        # name but name empty
        (
            [
                {
                    "_id": "repo1",
                    "params": {"namespace_id": "", "initialize_with_readme": "false", "name": ""},
                    "url": "https://example.com/url/example",
                }
            ],
            False,
        ),
        # url but url empty
        (
            [
                {
                    "_id": "repo1",
                    "params": {"namespace_id": "1", "initialize_with_readme": "false", "name": "repo name"},
                    "url": "",
                }
            ],
            False,
        ),
        # url but url not complete
        (
            [
                {
                    "_id": "repo1",
                    "params": {"namespace_id": "1", "initialize_with_readme": "false", "name": "repo name"},
                    "url": "https://example.com",
                }
            ],
            False,
        ),
        # url but url invalid
        (
            [
                {
                    "_id": "repo1",
                    "params": {"name": "some name", "namespace_id": "1", "initialize_with_readme": "false"},
                    "url": "random junk",
                }
            ],
            False,
        ),
    ],
)
def test_get_target_repo_info(repo_information, expected):
    actual = get_target_repo_info("repo1", repo_information)
    assert actual == expected


@pytest.mark.parametrize(
    "tokens, expected",
    [
        ([{"_id": "gitlab_private_token", "token": "<private-token>"}], "<private-token>"),
        ([{"_id": "wrong_name", "token": "<private-token>"}], None),
        (
            [
                {"_id": "gitlab_private_token", "token": "<private-token>"},
                {"_id": "gitlab_private_token", "token": "<private-token>"},
            ],
            None,
        ),
        ([{"_id": "gitlab_private_token", "token": ""}], None),
        ([{"_id": "gitlab_private_token"}], None),
        ([{"_id": "<private-token>"}], None),
        ({}, None),
    ],
)
def test_get_target_token(tokens, expected):
    actual = get_target_token("gitlab_private_token", tokens)
    assert actual == expected


# @mock.patch("requests.post")


@requests_mock.Mocker(kw="mock")
def test_create_repo(**kwargs):
    kwargs["mock"].post("https://example.com/url/example", status_code=201)
    # mock_requests_post.return_value = mock.Mock(**{"status_code": 201})
    rc = copy.copy(DEFAULT_RC)
    repo_token_information = {
        "repos": [
            {
                "_id": "talk_repo",
                "params": {"namespace_id": "35", "initialize_with_readme": "false", "name": "2206_my_talk"},
                "url": "https://example.com",
                "api_route": "/url/example",
                "namesapce_name": "talks",
            }
        ],
        "tokens": [{"_id": "gitlab_private_token", "token": "<private-token>"}],
    }
    rc._update(repo_token_information)
    actual = create_repo("talk_repo", "gitlab_private_token", rc)
    assert (
        actual == "repo 2206_my_talk has been created at https://example.com.\nClone this to your local using "
        "(HTTPS):\ngit clone https://example.com:<group/org name>/2206_my_talk.git\nor "
        "(SSH):\ngit clone git@example.com:<group/org name>/2206_my_talk.git"
    )


# @mock.patch('uuid.uuid4', return_value="test-uid")
@pytest.fixture
def test_get_uuid(mocker):
    mocker.patch("uuid.uuid4", return_value="test-uuid")
    expected = "test-uuid"
    actual = get_uuid()
    assert expected == actual


tga = [
    (
        {
            "_id": "good_person",
            "appointments": {
                "appt_id_1": {
                    "begin_date": "2022-06-01",
                    "end_date": "2022-06-30",
                    "grant": "good_grant",
                    "loading": 0.5,
                    "status": "submitted",
                    "type": "gra",
                    "notes": "",
                }
            },
        },
        [],
        "good_grant",
        [("good_person", dt.date(2022, 6, 1), dt.date(2022, 6, 30), 0.5, 0.48, "good_grant")],
    ),
    (
        {
            "_id": "good_person",
            "appointments": {
                "appt_id_1": {
                    "begin_date": "2022-06-01",
                    "end_date": "2022-06-30",
                    "grant": "good_grant",
                    "loading": 0.5,
                    "status": "submitted",
                    "type": "gra",
                    "notes": "",
                }
            },
        },
        [],
        None,
        [("good_person", dt.date(2022, 6, 1), dt.date(2022, 6, 30), 0.5, 0.48, "good_grant")],
    ),
    (
        {
            "_id": "good_person",
            "appointments": {
                "appt_id_1": {
                    "begin_date": "2022-06-01",
                    "end_date": "2022-06-30",
                    "grant": "good_grant",
                    "loading": 0.5,
                    "status": "submitted",
                    "type": "gra",
                    "notes": "",
                }
            },
        },
        [],
        "bad_grant",
        [],
    ),
]


@pytest.mark.parametrize("tga", tga)
def test_get_appointments(tga):
    expected = tga[3]
    actual = get_appointments(tga[0], tga[1], tga[2])
    assert expected == actual
