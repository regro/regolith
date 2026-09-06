import os
from copy import copy, deepcopy

import pytest

from regolith.chained_db import ChainDB, LazyChainedDB
from regolith.client_manager import ClientManager
from regolith.database import connect
from regolith.fsclient import FileSystemClient, dump_yaml
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
        if name == "second":
            dump_yaml(dbpath / "abstracts.yaml", {"first": {"_id": "first", "text": "an abstract"}})
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
    # open_dbs attaches the lazy chained view; mirror it so the fixture
    # behaves like a real connection
    client.chained_db = LazyChainedDB(client)
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


@pytest.mark.parametrize(
    "collname, expected_dbnames",
    [
        # Test the source map that says which databases hold a collection,
        # built from a directory listing rather than by reading documents
        # C1: a collection both databases hold, expect both in rc.databases
        # order, since that is the order the merge resolves in
        ("people", ["first", "second"]),
        # C2: a collection only the second database holds, expect only it
        ("abstracts", ["second"]),
        # C3: a collection no database holds, expect nothing
        ("nonexistent", []),
    ],
)
def test_collection_sources_reports_the_databases_holding_a_collection(collname, expected_dbnames, two_fs_dbs):
    sources = two_fs_dbs.collection_sources(collname)
    assert [db["name"] for db in sources] == expected_dbnames


def test_opening_the_databases_reads_no_documents(two_fs_dbs):
    # Test that opening builds the source map without reading any collection,
    # which is what stops a command paying for collections it never uses
    assert two_fs_dbs.chained_collection_names() == {"people", "abstracts"}
    for db in two_fs_dbs.rc.databases:
        assert two_fs_dbs.dbs[db["name"]] == {}


@pytest.mark.parametrize(
    "read_collection, expected_loaded",
    [
        # Test that reading one collection leaves the others unread
        # C1: chain a collection, expect only that collection read
        (lambda client: client.chained_db["people"], {"people"}),
        # C2: get one document, expect only that collection read
        (lambda client: client.get("people", "scopatz"), {"people"}),
        # C3: read the other collection, expect people left alone
        (lambda client: client.chained_db["abstracts"], {"abstracts"}),
    ],
)
def test_reading_one_collection_does_not_read_the_others(read_collection, expected_loaded, two_fs_dbs):
    read_collection(two_fs_dbs)
    loaded = set()
    for db in two_fs_dbs.rc.databases:
        loaded.update(two_fs_dbs.dbs[db["name"]])
    assert loaded == expected_loaded


def test_the_chained_db_matches_what_eager_chaining_produced(two_fs_dbs):
    # Test that chaining a collection on demand gives the same documents as
    # building the whole chained db up front did, so nothing downstream shifts
    people = two_fs_dbs.chained_db["people"]
    assert sorted(people) == ["only_first", "only_second", "scopatz"]
    assert people["scopatz"]["name"] == "A. Scopatz"
    assert people["scopatz"]["position"] == "prof"


def test_a_missing_collection_is_absent_without_being_read(two_fs_dbs):
    # Test that testing for a collection answers from the source map, and that
    # a missing one behaves like a missing key rather than an empty collection
    assert "nonexistent" not in two_fs_dbs.chained_db
    assert "people" in two_fs_dbs.chained_db
    assert two_fs_dbs.dbs["first"] == {}
    with pytest.raises(KeyError):
        two_fs_dbs.chained_db["nonexistent"]


def test_materialize_reads_every_collection(two_fs_dbs):
    # Test the explicit whole-database read that connect_db needs, since it
    # hands data to callers that outlive the connection
    materialized = two_fs_dbs.chained_db.materialize()
    assert sorted(materialized) == ["abstracts", "people"]
    assert materialized["people"]["scopatz"]["name"] == "A. Scopatz"


@pytest.mark.parametrize(
    "operation",
    [
        # Test that routing a document operation asks no server which
        # databases exist.  MongoClient.keys is list_database_names, a round
        # trip, and the rc already says which backend each database has.
        # C1: reading one document by id
        lambda client: client.find_one("first", "people", {"_id": "scopatz"}),
        # C2: inserting a document
        lambda client: client.insert_one("first", "people", {"_id": "new", "name": "New"}),
        # C3: updating a document
        lambda client: client.update_one("first", "people", {"_id": "scopatz"}, {"name": "A"}),
        # C4: deleting a document
        lambda client: client.delete_one("first", "people", {"_id": "scopatz"}),
    ],
)
def test_routing_an_operation_does_not_ask_which_databases_exist(operation, two_fs_dbs, mocker):
    keys = mocker.patch.object(FileSystemClient, "keys", autospec=True, side_effect=FileSystemClient.keys)
    operation(two_fs_dbs)
    assert keys.call_count == 0


def test_an_operation_on_an_unknown_database_is_a_no_op(two_fs_dbs):
    # Test that naming a database the rc does not have is ignored rather than
    # raising, which is how the old routing behaved
    assert two_fs_dbs.find_one("nonexistent", "people", {"_id": "scopatz"}) is None
    two_fs_dbs.insert_one("nonexistent", "people", {"_id": "new"})
    assert two_fs_dbs.get("people", "new") is None
