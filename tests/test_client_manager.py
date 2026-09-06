import os
from copy import copy, deepcopy

import pytest

from regolith.chained_db import ChainDB
from regolith.client_manager import ClientManager
from regolith.database import connect
from regolith.fsclient import dump_yaml
from regolith.runcontrol import DEFAULT_RC, load_rcfile
from regolith.schemas import EXEMPLARS
from regolith.tools import all_docs_from_collection


def test_collection_retrieval_python(make_mixed_db):
    if make_mixed_db is False:
        pytest.skip("Mongoclient failed to start")
    else:
        repo, fs_coll, mongo_coll = make_mixed_db
    os.chdir(repo)
    rc = copy(DEFAULT_RC)
    rc._update(load_rcfile("regolithrc.json"))
    with connect(rc) as rc.client:
        fs_test_dict = dict(list(all_docs_from_collection(rc.client, "abstracts"))[0])
        mongo_test_dict = dict(list(all_docs_from_collection(rc.client, "assignments"))[0])
    fs_expected_dict = deepcopy(EXEMPLARS[fs_coll])
    mongo_expected_dict = deepcopy(EXEMPLARS[mongo_coll])
    assert fs_test_dict == fs_expected_dict
    assert mongo_test_dict == mongo_expected_dict


@pytest.fixture
def two_fs_dbs(tmp_path):
    """Build two filesystem databases that share a collection, so the
    chaining done by the client manager can be tested without mongo."""
    names = ["first", "second"]
    for name in names:
        dbpath = tmp_path / name / "db"
        dbpath.mkdir(parents=True)
        if name == "first":
            docs = {
                "scopatz": {"_id": "scopatz", "name": "Anthony Scopatz", "position": "prof"},
                "only_first": {"_id": "only_first", "name": "First Only"},
            }
        else:
            docs = {
                "scopatz": {"_id": "scopatz", "name": "A. Scopatz"},
                "only_second": {"_id": "only_second", "name": "Second Only", "position": "prof"},
            }
        dump_yaml(dbpath / "people.yaml", docs)
    rc = copy(DEFAULT_RC)
    rc._update(
        {
            "builddir": str(tmp_path / "_build"),
            "databases": [
                {
                    "name": name,
                    "url": str(tmp_path / name),
                    "path": "db",
                    "local": True,
                    "backend": "filesystem",
                    "blacklist": [],
                    "whitelist": [],
                }
                for name in names
            ],
        }
    )
    client = ClientManager(rc.databases, rc)
    client.open()
    for db in rc.databases:
        client.load_database(db)
    yield client


def test_get_merges_the_versions_held_by_each_database(two_fs_dbs):
    # Test reading one document that two databases both hold.  A scalar takes
    # its value from the last database in rc.databases that has the key, and a
    # key only one database has still comes through.
    doc = two_fs_dbs.get("people", "scopatz")
    assert doc["name"] == "A. Scopatz"
    assert doc["position"] == "prof"


def test_get_returns_a_document_only_one_database_holds(two_fs_dbs):
    # Test reading documents that live in a single database, one in each
    assert two_fs_dbs.get("people", "only_first")["name"] == "First Only"
    assert two_fs_dbs.get("people", "only_second")["name"] == "Second Only"


def test_get_returns_none_when_no_database_holds_the_document(two_fs_dbs):
    # Test asking for an id that is in neither database, and for a
    # collection that does not exist at all
    assert two_fs_dbs.get("people", "nobody") is None
    assert two_fs_dbs.get("nonexistent", "scopatz") is None


def test_get_agrees_with_the_chained_db(two_fs_dbs):
    # Test that get resolves a shared document the same way open_dbs does,
    # since the two must not drift apart
    chained = {}
    for db in two_fs_dbs.rc.databases:
        for _id, doc in two_fs_dbs.dbs[db["name"]]["people"].items():
            if _id in chained:
                chained[_id].maps.append(doc)
            else:
                chained[_id] = ChainDB(doc)
    for _id in chained:
        assert two_fs_dbs.get("people", _id)["name"] == chained[_id]["name"]


def test_find_without_a_filter_yields_every_merged_document(two_fs_dbs):
    # Test that a document held by both databases is yielded once, merged
    found = {doc["_id"]: doc for doc in two_fs_dbs.find("people")}
    assert sorted(found) == ["only_first", "only_second", "scopatz"]
    assert found["scopatz"]["name"] == "A. Scopatz"


def test_find_filters_on_the_merged_value(two_fs_dbs):
    # Test that the filter sees the merged document.  1. position is only in
    # the first database for scopatz but must still match. 2. a filter on a
    # value that was overridden must match the winning value, not the losing
    # one.
    positions = sorted(doc["_id"] for doc in two_fs_dbs.find("people", {"position": "prof"}))
    assert positions == ["only_second", "scopatz"]
    assert [doc["_id"] for doc in two_fs_dbs.find("people", {"name": "A. Scopatz"})] == ["scopatz"]
    assert list(two_fs_dbs.find("people", {"name": "Anthony Scopatz"})) == []


def test_find_and_get_return_copies_by_default(two_fs_dbs):
    # Test that mutating a returned document does not change the state the
    # client holds, which it would otherwise write out without knowing
    doc = two_fs_dbs.get("people", "only_first")
    doc["name"] = "mutated"
    assert two_fs_dbs.get("people", "only_first")["name"] == "First Only"
    for found in two_fs_dbs.find("people", {"_id": "only_first"}):
        found["name"] = "mutated again"
    assert two_fs_dbs.get("people", "only_first")["name"] == "First Only"
