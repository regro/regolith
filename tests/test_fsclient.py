import datetime
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


def test_dump_database_force_writes_every_collection(fs_db):
    # Test that force writes the unmodified collections too, which is what
    # an in-place edit outside the client needs
    client, db, dbpath = fs_db
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
