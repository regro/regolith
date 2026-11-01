import pytest

from regolith.schemas import SCHEMAS, _update_dict_target, insert_alloweds, validate


def test_update_dict_target():
    doc = {
        "email": {
            "description": "contact email for the author.",
            "required": True,
            "deeper": {"eallowed": "TEST"},
        },
        "_id": {
            "description": "Unique identifier for submission. "
            "This generally includes the author name and part of the title.",
            "required": True,
            "type": "string",
        },
        "coauthors": {"description": "names of coauthors", "required": False, "eallowed": "TEST2"},
        "test_repeated": {"description": "names of coauthors", "required": False, "eallowed": "TEST2"},
    }
    expected = {
        "_id": {
            "description": "Unique identifier for submission. "
            "This generally includes the author name and part of the title.",
            "required": True,
            "type": "string",
        },
        "coauthors": {"description": "names of coauthors", "required": False, "eallowed": "string"},
        "test_repeated": {"description": "names of coauthors", "required": False, "eallowed": "string"},
        "email": {
            "description": "contact email for the author.",
            "required": True,
            "deeper": {"eallowed": ["string", "float"]},
        },
    }
    first_cut = _update_dict_target(doc, {"eallowed": "TEST"}, ["string", "float"])
    actual = _update_dict_target(first_cut, {"eallowed": "TEST2"}, "string")
    assert actual == expected


# Test checking a record that holds only part of a document, such as the private half of a grant
@pytest.mark.parametrize(
    "record, partial, expected_errors",
    [
        # C1: the private half of a grant checked as a whole grant, expect the public required fields missing
        pytest.param(
            {"_id": "g1", "account": "GG"},
            False,
            {
                "amount": ["required field"],
                "funder": ["required field"],
                "team": ["required field"],
                "title": ["required field"],
            },
            id="whole",
        ),
        # C2: the private half of a grant checked as a part, expect it valid
        pytest.param({"_id": "g1", "account": "GG"}, True, {}, id="partial"),
        # C3: a part with a field of the wrong type, expect that field reported though the check is partial
        pytest.param({"_id": "g1", "account": 42}, True, {"account": ["must be of string type"]}, id="wrong-type"),
    ],
)
def test_validate_partial(record, partial, expected_errors):
    valid, errors = validate("grants", record, SCHEMAS, partial=partial)
    assert valid == (not expected_errors)
    assert errors == expected_errors


def test_insert_alloweds():
    alloweds = {"TEST": ["string", "float"], "TEST2": "string"}
    doc = {
        "email": {
            "description": "contact email for the author.",
            "required": True,
            "deeper": {"eallowed": "TEST"},
        },
        "_id": {
            "description": "Unique identifier for submission. "
            "This generally includes the author name and part of the title.",
            "required": True,
            "type": "string",
        },
        "coauthors": {"description": "names of coauthors", "required": False, "eallowed": "TEST2"},
        "test_repeated": {"description": "names of coauthors", "required": False, "eallowed": "TEST2"},
    }
    expected = {
        "_id": {
            "description": "Unique identifier for submission. "
            "This generally includes the author name and part of the title.",
            "required": True,
            "type": "string",
        },
        "coauthors": {"description": "names of coauthors", "required": False, "eallowed": "string"},
        "test_repeated": {"description": "names of coauthors", "required": False, "eallowed": "string"},
        "email": {
            "description": "contact email for the author.",
            "required": True,
            "deeper": {"eallowed": ["string", "float"]},
        },
    }
    actual = insert_alloweds(doc, alloweds, "eallowed")
    assert actual == expected
