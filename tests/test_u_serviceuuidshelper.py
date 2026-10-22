"""Tests for giving every service entry in the people collection a
uuid."""

import copy

import pytest

from regolith.database import connect
from regolith.main import main
from regolith.runcontrol import DEFAULT_RC, filter_databases, load_rcfile
from regolith.schemas import EXEMPLARS


def stored_service(person_id):
    """Return one person's service entries straight from the
    collection."""
    rc = copy.copy(DEFAULT_RC)
    rc._update(load_rcfile("regolithrc.json"))
    filter_databases(rc)
    with connect(rc) as rc.client:
        return rc.client.get("people", person_id).get("service", [])


def exemplar_service(person_id):
    """Return one person's service entries as the exemplars hold
    them."""
    return next(person for person in EXEMPLARS["people"] if person["_id"] == person_id)["service"]


@pytest.mark.parametrize(
    "people_args, expected_with_uuids, expected_without_uuids",
    [
        # Test which people's service entries are given uuids, where the exemplar
        # sbillinge has none and scopatz has them all
        # C1: no people given, expect every person's entries to have one
        ([], ["scopatz", "sbillinge"], []),
        # C2: one person given, expect the people not given to be left alone
        (["scopatz"], ["scopatz"], ["sbillinge"]),
    ],
)
def test_service_entries_are_given_uuids(people_args, expected_with_uuids, expected_without_uuids, make_fresh_db):
    main(["helper", "u_service_uuids"] + people_args)
    for person_id in expected_with_uuids:
        service = stored_service(person_id)
        assert service
        assert all(entry.get("uuid") for entry in service)
    for person_id in expected_without_uuids:
        assert not any(entry.get("uuid") for entry in stored_service(person_id))


def test_existing_uuids_are_kept(make_fresh_db):
    # Test that existing uuids are left alone, since builders select entries by them
    main(["helper", "u_service_uuids"])
    expected_uuids = [entry["uuid"] for entry in exemplar_service("scopatz")]
    actual_uuids = [entry["uuid"] for entry in stored_service("scopatz")]
    assert actual_uuids == expected_uuids


def test_only_uuids_are_added(make_fresh_db):
    # Test that giving uuids changes nothing else about the service entries
    main(["helper", "u_service_uuids", "sbillinge"])
    actual_service = [
        {key: value for key, value in entry.items() if key != "uuid"} for entry in stored_service("sbillinge")
    ]
    assert actual_service == exemplar_service("sbillinge")


def test_unknown_people_are_all_reported(make_fresh_db):
    # Test that every unknown id is reported together and nothing is written,
    # so the ids can all be fixed before one clean rerun
    with pytest.raises(ValueError, match="nobody, nobodyelse"):
        main(["helper", "u_service_uuids", "nobody", "sbillinge", "nobodyelse"])
    assert stored_service("sbillinge") == exemplar_service("sbillinge")
