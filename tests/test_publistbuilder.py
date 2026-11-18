import pytest

from regolith.builders.publistbuilder import _select_people

PEOPLE = [
    {"_id": "sbillinge", "name": "Simon J. L. Billinge", "aka": ["S. J. L. Billinge", "Simon Billinge"]},
    {"_id": "scopatz", "name": "Anthony Scopatz", "aka": ["A. Scopatz"]},
]


# Test selection of the people whose publication lists are built
@pytest.mark.parametrize(
    "requested, expected_ids",
    [
        # C1: all people requested, expect every person in collection order
        pytest.param(["all"], ["sbillinge", "scopatz"], id="all"),
        # C2: people requested by 1. id, 2. canonical name, 3. aka, 4. any case,
        #   expect the matching person
        pytest.param(["scopatz"], ["scopatz"], id="by-id"),
        pytest.param(["Anthony Scopatz"], ["scopatz"], id="by-name"),
        pytest.param(["S. J. L. Billinge"], ["sbillinge"], id="by-aka"),
        pytest.param(["SBILLINGE"], ["sbillinge"], id="case-insensitive"),
        # C3: several people requested out of collection order, expect them in
        #   collection order
        pytest.param(["scopatz", "sbillinge"], ["sbillinge", "scopatz"], id="several"),
        # C4: the same person requested by id and by aka, expect them once
        pytest.param(["sbillinge", "Simon Billinge"], ["sbillinge"], id="duplicate"),
    ],
)
def test_select_people(requested, expected_ids):
    actual_ids = [person["_id"] for person in _select_people(PEOPLE, requested)]
    assert actual_ids == expected_ids


# Test that people missing from the collection are all reported at once
def test_select_people_missing():
    with pytest.raises(ValueError, match="nobody, nonesuch"):
        _select_people(PEOPLE, ["nobody", "sbillinge", "nonesuch"])
