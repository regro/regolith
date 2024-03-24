from regolith.schemas import insert_alloweds, _update_dict_target


def test_update_dict_target():
    alloweds = {"TEST": ["string", "float"], "TEST2": "string"}
    doc = {
            "email": {
                "description": "contact email for the author.",
                "required": True,
                "deeper": {"eallowed": "TEST"}
            },
            "_id": {
                "description": "Unique identifier for submission. This generally includes the author name and part of the title.",
                "required": True,
                "type": "string"
            },
            "coauthors": {
                "description": "names of coauthors",
                "required": False,
                "eallowed": "TEST2"
            },
            "test_repeated": {
                "description": "names of coauthors",
                "required": False,
                "eallowed": "TEST2"
            }
    }
    expected = {
            "_id": {
                "description": "Unique identifier for submission. This generally includes the author name and part of the title.",
                "required": True,
                "type": "string"
            },
            "coauthors": {
                "description": "names of coauthors",
                "required": False,
                "eallowed": "string"
            },
            "test_repeated": {
                "description": "names of coauthors",
                "required": False,
                "eallowed": "string"
            },
            "email": {
                "description": "contact email for the author.",
                "required": True,
                "deeper": {"eallowed": ["string", "float"]}
            }
        }
    first_cut = _update_dict_target(doc,  {"eallowed":"TEST"}, ["string", "float"])
    actual = _update_dict_target(first_cut,  {"eallowed":"TEST2"}, "string")
    assert actual == expected

def test_insert_alloweds():
    alloweds = {
        "TEST": ["string", "float"],
        "TEST2": "string"
    }
    doc = {
            "email": {
                "description": "contact email for the author.",
                "required": True,
                "deeper": {"eallowed": "TEST"}
            },
            "_id": {
                "description": "Unique identifier for submission. This generally includes the author name and part of the title.",
                "required": True,
                "type": "string"
            },
            "coauthors": {
                "description": "names of coauthors",
                "required": False,
                "eallowed": "TEST2"
            },
            "test_repeated": {
                "description": "names of coauthors",
                "required": False,
                "eallowed": "TEST2"
            }
    }
    expected = {
            "_id": {
                "description": "Unique identifier for submission. This generally includes the author name and part of the title.",
                "required": True,
                "type": "string"
            },
            "coauthors": {
                "description": "names of coauthors",
                "required": False,
                "eallowed": "string"
            },
            "test_repeated": {
                "description": "names of coauthors",
                "required": False,
                "eallowed": "string"
            },
            "email": {
                "description": "contact email for the author.",
                "required": True,
                "deeper": {"eallowed": ["string", "float"]}
            }
        }
    actual = insert_alloweds(doc, alloweds, "eallowed")
    assert actual == expected
