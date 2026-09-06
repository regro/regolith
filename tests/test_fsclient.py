import datetime
import logging
import tempfile
from copy import copy
from pathlib import Path

import pytest

from regolith.fsclient import FileSystemClient, date_encoder, dump_json, dump_yaml
from regolith.runcontrol import DEFAULT_RC


def test_date_encoder():
    day = datetime.date(2021, 1, 1)
    time = datetime.datetime(2021, 5, 18, 6, 28, 21, 504549)
    assert date_encoder(day) == "2021-01-01"
    assert date_encoder(time) == "2021-05-18T06:28:21.504549"


def test_dump_json():
    doc = {
        "first": {"_id": "first", "name": "me", "date": datetime.date(2021, 5, 1), "test_list": [5, 4]},
        "second": {"_id": "second"},
    }
    json_doc = '{"_id": "first", "date": "2021-05-01", "name": "me", "test_list": [5, 4]}\n{"_id": "second"}'
    temp_dir = Path(tempfile.gettempdir())
    filename = temp_dir / "test.json"
    dump_json(filename, doc, date_handler=date_encoder)
    with open(filename, "r", encoding="utf-8") as f:
        actual = f.read()
    assert actual == json_doc


# datasets = [
#     (
#         {"first": {"date": "2021-05-01", "name": "me", "test_list": [5, 4]}, "second": {}},
#         {
#             "first": {"_id": "first", "name": "me", "date": datetime.date(2021, 5, 1), "test_list": [5, 4]},
#             "second": {"_id": "second"},
#         },
#     ),
# ]
# @pytest.mark.parametrize("json_doc, expected", datasets)
# def test_load_json(json_doc, expected):
#     temp_dir = Path(tempfile.gettempdir())
#     filename = temp_dir / "test.json"
#     with open(filename, "w", encoding="utf-8") as f:
#         json.dump(json_doc, f)
#     actual = load_json(filename)
#     assert actual == expected


@pytest.fixture
def fs_db(tmp_path):
    """Build a two collection filesystem database and return its client
    and db description."""
    dbpath = tmp_path / "db"
    dbpath.mkdir()
    dump_yaml(dbpath / "people.yaml", {"scopatz": {"_id": "scopatz", "name": "Anthony Scopatz"}})
    dump_yaml(dbpath / "abstracts.yaml", {"first": {"_id": "first", "text": "an abstract"}})
    db = {
        "name": "test",
        "url": str(tmp_path),
        "path": "db",
        "local": True,
        "backend": "filesystem",
        "blacklist": [],
        "whitelist": [],
    }
    rc = copy(DEFAULT_RC)
    rc._update({"builddir": str(tmp_path / "_build")})
    client = FileSystemClient(rc)
    client.load_database(db)
    yield client, db, dbpath


def _mtimes(dbpath):
    """Return a dict mapping each collection filename to its
    modification time."""
    return {f.name: f.stat().st_mtime_ns for f in sorted(dbpath.iterdir())}


def test_dump_database_skips_unmodified_collections(fs_db):
    # Test that a read-only session leaves every collection file untouched
    client, db, dbpath = fs_db
    before = _mtimes(dbpath)
    # Reading is not a modification, so it must not mark anything dirty
    list(client.all_documents("people"))
    written = client.dump_database(db)
    assert written == []
    assert _mtimes(dbpath) == before


def test_dump_database_writes_only_modified_collections(fs_db):
    # Test that a write to one collection dumps that collection alone
    client, db, dbpath = fs_db
    before = _mtimes(dbpath)
    client.insert_one("test", "people", {"_id": "sbillinge", "name": "Simon Billinge"})
    written = client.dump_database(db)
    assert written == [str(Path("db") / "people.yaml")]
    after = _mtimes(dbpath)
    assert after["people.yaml"] != before["people.yaml"]
    assert after["abstracts.yaml"] == before["abstracts.yaml"]


def test_dump_database_clears_dirty_state(fs_db):
    # Test that a collection is written once per modification, so that a
    # second dump with no further writes is a no-op
    client, db, dbpath = fs_db
    client.insert_one("test", "people", {"_id": "sbillinge", "name": "Simon Billinge"})
    assert client.is_dirty("test", "people") is True
    client.dump_database(db)
    assert client.is_dirty("test", "people") is False
    assert client.is_dirty("test") is False
    before = _mtimes(dbpath)
    assert client.dump_database(db) == []
    assert _mtimes(dbpath) == before


def test_dump_database_force_writes_every_loaded_collection(fs_db):
    # Test that force writes collections that were read but not modified,
    # which is what an in-place edit outside the client needs.  Collections
    # are read on demand, so only the ones that were asked for are written.
    client, db, dbpath = fs_db
    client.raw_collection("test", "people")
    client.raw_collection("test", "abstracts")
    before = _mtimes(dbpath)
    written = client.dump_database(db, force=True)
    assert sorted(written) == [str(Path("db") / "abstracts.yaml"), str(Path("db") / "people.yaml")]
    after = _mtimes(dbpath)
    assert after["people.yaml"] != before["people.yaml"]
    assert after["abstracts.yaml"] != before["abstracts.yaml"]


@pytest.mark.parametrize(
    "write",
    [
        # C1: inserting one document marks the collection dirty
        lambda client: client.insert_one("test", "people", {"_id": "new", "name": "New Person"}),
        # C2: inserting many documents marks the collection dirty
        lambda client: client.insert_many("test", "people", [{"_id": "new", "name": "New Person"}]),
        # C3: updating a document marks the collection dirty
        lambda client: client.update_one("test", "people", {"_id": "scopatz"}, {"name": "A. Scopatz"}),
        # C4: deleting a document marks the collection dirty
        lambda client: client.delete_one("test", "people", {"_id": "scopatz"}),
    ],
)
def test_writes_mark_the_collection_dirty(fs_db, write):
    # Test that every mutating client method records the collection as dirty
    client, db, dbpath = fs_db
    assert client.is_dirty("test", "people") is False
    write(client)
    assert client.is_dirty("test", "people") is True
    assert client.is_dirty("test", "abstracts") is False


def test_insert_many_of_nothing_is_not_a_modification(fs_db):
    # Test that inserting an empty list of documents leaves the collection clean
    client, db, dbpath = fs_db
    client.insert_many("test", "people", [])
    assert client.is_dirty("test", "people") is False
    assert client.dump_database(db) == []


@pytest.mark.parametrize(
    "dbname, collname, _id, expected_name",
    [
        # Test looking one document up by id instead of reading a collection
        # C1: a document the database holds, expect that document
        ("test", "people", "scopatz", "Anthony Scopatz"),
        # C2: an id the collection does not have, expect None
        ("test", "people", "nobody", None),
        # C3: a collection the database does not have, expect None
        ("test", "nonexistent", "scopatz", None),
        # C4: a database the client has not loaded, expect None
        ("nonexistent", "people", "scopatz", None),
    ],
)
def test_get_returns_one_document_by_id(dbname, collname, _id, expected_name, fs_db):
    client, db, dbpath = fs_db
    doc = client.get(dbname, collname, _id)
    assert (doc["name"] if doc is not None else None) == expected_name


def test_get_of_a_missing_database_does_not_create_it(fs_db):
    # Test that a miss leaves dbs alone, since dbs is a defaultdict and a
    # stray lookup would otherwise add an empty database that gets dumped
    client, db, dbpath = fs_db
    client.get("nonexistent", "people", "scopatz")
    assert "nonexistent" not in client.dbs


@pytest.mark.parametrize(
    "filter, expected_ids",
    [
        # Test filtering a collection on the filesystem backend
        # C1: no filter, expect every document in the collection
        (None, ["scopatz"]),
        # C2: a filter on a value that matches, expect that document
        ({"name": "Anthony Scopatz"}, ["scopatz"]),
        # C3: a filter on a value that does not match, expect nothing
        ({"name": "Nobody"}, []),
        # C4: a filter on a key no document has, expect nothing
        ({"missing_key": "any"}, []),
    ],
)
def test_find_matches_documents_on_every_filter_key(filter, expected_ids, fs_db):
    client, db, dbpath = fs_db
    assert [doc["_id"] for doc in client.find("test", "people", filter)] == expected_ids


def test_find_one_by_id_agrees_with_a_scan(fs_db):
    # Test that the id fast path in find_one returns what scanning would
    client, db, dbpath = fs_db
    client.insert_one("test", "people", {"_id": "sbillinge", "name": "Simon Billinge"})
    by_id = client.find_one("test", "people", {"_id": "sbillinge"})
    by_scan = client.find_one("test", "people", {"name": "Simon Billinge"})
    assert by_id == by_scan


def test_loading_a_collection_is_silent_but_logged(fs_db, caplog, capsys):
    # Test that reading a collection prints nothing, since a helper's output is
    # meant to be readable, while still saying what it read for debugging
    client, db, dbpath = fs_db
    with caplog.at_level(logging.DEBUG, logger="regolith.fsclient"):
        client.raw_collection("test", "people")
    assert capsys.readouterr().err == ""
    assert any("people" in record.getMessage() for record in caplog.records)


@pytest.mark.parametrize(
    "write, expected_name",
    [
        # Test that a write reaches a database whose collections have not been
        # read yet.  The client is asked whether it holds the database before
        # the write is routed to it, so a client that names no database until
        # something is read would drop the write silently.
        # C1: inserting a document, expect it to be stored
        (lambda c: c.insert_one("test", "people", {"_id": "new", "name": "New Person"}), "New Person"),
        # C2: inserting several documents, expect them stored
        (lambda c: c.insert_many("test", "people", [{"_id": "new", "name": "New Person"}]), "New Person"),
        # C3: updating a document, expect the new value
        (lambda c: c.update_one("test", "people", {"_id": "new"}, {"name": "New Person"}), "New Person"),
    ],
)
def test_a_write_reaches_a_database_whose_collections_are_unread(write, expected_name, fs_db):
    client, db, dbpath = fs_db
    assert "test" in client.keys()
    assert client.dbs.get("test", {}) == {}
    write(client)
    assert client.get("test", "people", "new")["name"] == expected_name


def test_a_database_is_named_before_its_collections_are_read(fs_db):
    # Test that loading a database names it straight away, since routing a
    # write depends on the client saying which databases it backs
    client, db, dbpath = fs_db
    assert set(client.keys()) == {"test"}
    assert client.dbs.get("test", {}) == {}


@pytest.mark.parametrize(
    "load, expected_how",
    [
        # Test which loader reads a collection.  The round trip loader records
        # the comments and formatting a file has, and is around nine times
        # slower, so it is used only when the file is going to be written.
        # C1: reading a collection, expect the fast loader
        (lambda c: c.raw_collection("test", "people"), "fast"),
        # C2: writing to a collection, expect the round trip loader
        (lambda c: c.insert_one("test", "people", {"_id": "new"}), "round_trip"),
        # C3: reading then writing, expect the round trip loader to replace the
        # fast read, so the dump still keeps the file's formatting
        (
            lambda c: (c.raw_collection("test", "people"), c.insert_one("test", "people", {"_id": "new"})),
            "round_trip",
        ),
    ],
)
def test_a_collection_is_read_round_trip_only_when_it_will_be_written(load, expected_how, fs_db):
    client, db, dbpath = fs_db
    load(client)
    assert client._loaded[("test", "people")] == expected_how


def test_writing_after_a_fast_read_keeps_the_file_formatting(fs_db):
    # Test that a collection read fast and then written comes back with its
    # formatting intact, which is the reason the round trip loader exists
    client, db, dbpath = fs_db
    before = (dbpath / "people.yaml").read_text()
    client.raw_collection("test", "people")
    client.insert_one("test", "people", {"_id": "sbillinge", "name": "Simon Billinge"})
    client.dump_database(db)
    after = (dbpath / "people.yaml").read_text()
    assert before.rstrip("\n") in after or "Anthony Scopatz" in after
    assert "Simon Billinge" in after
