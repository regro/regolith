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


@pytest.mark.parametrize(
    "_id, expected_name, expected_position",
    [
        # Test reading one document through every database that holds it
        # C1: an id both databases hold, expect the two versions merged
        # 1. name is in both, expect the last database in rc.databases to win
        # 2. position is only in the first, expect it to come through anyway
        ("scopatz", "A. Scopatz", "prof"),
        # C2: an id only the first database holds, expect that version
        ("only_first", "First Only", None),
        # C3: an id only the second database holds, expect that version
        ("only_second", "Second Only", "prof"),
    ],
)
def test_get_merges_the_versions_each_database_holds(_id, expected_name, expected_position, two_fs_dbs):
    doc = two_fs_dbs.get("people", _id)
    assert doc["name"] == expected_name
    assert doc.get("position") == expected_position


@pytest.mark.parametrize(
    "collname, _id",
    [
        # Test asking for a document that is not there, which must not raise
        # C1: an id no database holds, expect None
        ("people", "nobody"),
        # C2: a collection no database holds, expect None
        ("nonexistent", "scopatz"),
    ],
)
def test_get_returns_none_when_no_database_holds_the_document(collname, _id, two_fs_dbs):
    assert two_fs_dbs.get(collname, _id) is None


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


@pytest.mark.parametrize(
    "filter, expected_ids",
    [
        # Test that find matches the merged document rather than any single
        # database's version of it
        # C1: no filter, expect every document, each merged and yielded once
        (None, ["only_first", "only_second", "scopatz"]),
        # C2: a filter on a key only one database supplies, expect both of the
        # documents that carry it once merged
        ({"position": "prof"}, ["only_second", "scopatz"]),
        # C3: a filter on the value that wins the merge, expect that document
        ({"name": "A. Scopatz"}, ["scopatz"]),
        # C4: a filter on the value that lost the merge, expect nothing
        ({"name": "Anthony Scopatz"}, []),
    ],
)
def test_find_filters_on_the_merged_document(filter, expected_ids, two_fs_dbs):
    assert sorted(doc["_id"] for doc in two_fs_dbs.find("people", filter)) == expected_ids


@pytest.mark.parametrize(
    "read_document",
    [
        # Test that a caller cannot change the state the client holds, which it
        # would otherwise write out without knowing it had to
        # C1: read through get, expect the client to keep its own value
        lambda client: client.get("people", "only_first"),
        # C2: read through find, expect the client to keep its own value
        lambda client: next(iter(client.find("people", {"_id": "only_first"}))),
    ],
)
def test_reads_return_copies_by_default(read_document, two_fs_dbs):
    doc = read_document(two_fs_dbs)
    doc["name"] = "mutated"
    assert two_fs_dbs.get("people", "only_first")["name"] == "First Only"
