"""Tests for the mongo backed client that do not need a live mongod."""

import datetime as dt
from pathlib import Path
from types import SimpleNamespace

import pytest

from regolith.mongoclient import MongoClient

from .conftest import assert_mongo_encodable


class FakePymongoCollection:
    """A stand-in for a pymongo Collection that records the queries it
    is asked, so a test can tell a pushed down query from a full
    read."""

    def __init__(self, docs, queries):
        self._docs = docs
        self.queries = queries

    def find_one(self, filter):
        assert_mongo_encodable("filter", filter)
        self.queries.append(("find_one", filter))
        for doc in self._docs:
            if all(doc.get(key) == value for key, value in filter.items()):
                return doc
        return None

    def update_one(self, filter, update):
        assert_mongo_encodable("filter", filter)
        assert_mongo_encodable("update", update)
        self.queries.append(("update_one", filter, update))
        matched = sum(1 for doc in self._docs if all(doc.get(k) == v for k, v in filter.items()))
        return SimpleNamespace(matched_count=matched)

    def find(self, filter=None):
        assert_mongo_encodable("filter", filter or {})
        self.queries.append(("find", filter))
        for doc in self._docs:
            if all(doc.get(key) == value for key, value in (filter or {}).items()):
                yield doc


class FakePymongoDatabase:
    """A stand-in for a pymongo Database that offers only the collection
    listing call that pymongo 4 still provides."""

    def __init__(self, collections, queries):
        self._collections = collections
        self.queries = queries

    def list_collection_names(self):
        return list(self._collections)

    def __getitem__(self, collname):
        return FakePymongoCollection(self._collections.get(collname, []), self.queries)

    def __getattr__(self, name):
        # pymongo 4 removed Database.collection_names, so reaching for any
        # other attribute is the regression these tests guard against.
        raise AttributeError(f"pymongo 4 Database has no attribute {name!r}")


def _client_with(collections):
    """Build a MongoClient whose pymongo client is the fake database.

    Returns the client and the list its collections append queries to.
    """
    queries = []
    if not isinstance(collections, dict):
        collections = {name: [] for name in collections}
    client = MongoClient.__new__(MongoClient)
    client.client = {"test": FakePymongoDatabase(collections, queries)}
    client.rc = None
    return client, queries


def test_collection_names_uses_the_pymongo_4_api():
    # Test listing the collections of a database, which must go through
    # list_collection_names because pymongo 4 removed collection_names
    client, _ = _client_with(["people", "todos"])
    assert client.collection_names("test") == ["people", "todos"]


def test_dump_database_lists_collections_with_the_pymongo_4_api(mocker, tmp_path):
    # Test that dumping a mongo database lists its collections through the
    # pymongo 4 API, so that a mongo to filesystem backup does not fail
    mocker.patch("regolith.mongoclient.subprocess.check_call")
    client, _ = _client_with(["people"])
    db = {"name": "test", "url": str(tmp_path), "path": "db", "local": True}
    to_add = client.dump_database(db)
    assert to_add == [str(Path("db") / "people.json")]


PEOPLE_DOCS = [
    {"_id": "scopatz", "name": "Anthony Scopatz", "position": "prof"},
    {"_id": "sbillinge", "name": "Simon Billinge", "position": "prof"},
    {"_id": "student", "name": "A Student", "position": "grad"},
]


@pytest.mark.parametrize(
    "_id, expected_name",
    [
        # Test that reading one document sends an _id query to the server
        # instead of reading the collection, which is the point of the method
        # C1: a document the server holds, expect that document
        ("scopatz", "Anthony Scopatz"),
        # C2: an id the server does not hold, expect None
        ("nobody", None),
    ],
)
def test_get_asks_the_server_for_one_document(_id, expected_name):
    client, queries = _client_with({"people": PEOPLE_DOCS})
    doc = client.get("test", "people", _id)
    assert (doc["name"] if doc is not None else None) == expected_name
    assert queries == [("find_one", {"_id": _id})]


@pytest.mark.parametrize(
    "filter, expected_ids, expected_query",
    [
        # Test that the filter reaches the server, so only the matching
        # documents cross the network rather than the whole collection
        # C1: no filter, expect every document and a valid empty mongo query
        (None, ["scopatz", "sbillinge", "student"], {}),
        # C2: a filter several documents match, expect all of them
        ({"position": "prof"}, ["scopatz", "sbillinge"], {"position": "prof"}),
        # C3: a filter no document matches, expect nothing
        ({"position": "postdoc"}, [], {"position": "postdoc"}),
    ],
)
def test_find_sends_the_filter_to_the_server(filter, expected_ids, expected_query):
    client, queries = _client_with({"people": PEOPLE_DOCS})
    assert [doc["_id"] for doc in client.find("test", "people", filter)] == expected_ids
    assert queries == [("find", expected_query)]


@pytest.mark.parametrize(
    "path, value, expected_found",
    [
        # Test that setting one field sends only that field to the server,
        # where replacing the document would send all of it
        # C1: one entry of a list, which is the case this exists for
        ("todos.3", {"description": "changed"}, True),
        # C2: a top level field
        ("name", "Renamed", True),
    ],
)
def test_update_field_sends_only_that_field(path, value, expected_found):
    client, queries = _client_with({"people": PEOPLE_DOCS})
    assert client.update_field("test", "people", "scopatz", path, value) is expected_found
    assert queries == [("update_one", {"_id": "scopatz"}, {"$set": {path: value}})]


def test_update_field_does_not_read_the_document_first():
    # Test that no find is issued.  update_one reads the document back in
    # order to validate it, which is the round trip this avoids.
    client, queries = _client_with({"people": PEOPLE_DOCS})
    client.update_field("test", "people", "scopatz", "todos.3", {"description": "changed"})
    assert not any(q[0].startswith("find") for q in queries)


def test_update_field_reports_a_miss():
    # Test that setting a field of a document the server does not have says
    # so rather than raising
    client, _ = _client_with({"people": PEOPLE_DOCS})
    assert client.update_field("test", "people", "nobody", "name", "x") is False


@pytest.mark.parametrize(
    "value, expected_sent",
    [
        # Test that a value is encodable by the time it reaches the server.
        # Mongo cannot encode a datetime.date, and regolith stores dates as iso
        # strings, so update_field has to clean the value the way update_one
        # does.
        # C1: a task carrying a date, which is what finishing one sends
        (
            {"description": "a task", "end_date": dt.date(2026, 9, 6)},
            {"description": "a task", "end_date": "2026-09-06"},
        ),
        # C2: a bare date
        (dt.date(2026, 9, 6), "2026-09-06"),
        # C3: dates nested in a list, which the recursion has to reach
        ({"notes": [{"on": dt.date(2026, 1, 2)}]}, {"notes": [{"on": "2026-01-02"}]}),
        # C4: a value with no dates in it, expect it sent unchanged
        ({"description": "a task"}, {"description": "a task"}),
    ],
)
def test_update_field_sends_an_encodable_value(value, expected_sent):
    client, queries = _client_with({"people": PEOPLE_DOCS})
    client.update_field("test", "people", "scopatz", "todos.3", value)
    assert queries == [("update_one", {"_id": "scopatz"}, {"$set": {"todos.3": expected_sent}})]


def test_update_field_does_not_rewrite_the_path():
    # Test that the path survives cleaning.  bson_cleanup replaces the periods
    # in keys, so cleaning the whole $set would turn "todos.3" into "todos-3"
    # and set a field of that name rather than the fourth entry of the list.
    client, queries = _client_with({"people": PEOPLE_DOCS})
    client.update_field("test", "people", "scopatz", "todos.3", {"end_date": dt.date(2026, 9, 6)})
    ((_, _, update),) = queries
    assert list(update["$set"]) == ["todos.3"]


def test_the_fake_collection_refuses_what_mongo_would_refuse():
    # Test the guard itself.  A test that sends an unencodable value must fail
    # here rather than passing and failing against a real server, which is how
    # the datetime.date bug in update_field reached production.
    client, _ = _client_with({"people": PEOPLE_DOCS})
    with pytest.raises(AssertionError, match="mongo cannot be sent this update"):
        client.client["test"]["people"].update_one({"_id": "scopatz"}, {"$set": {"end_date": dt.date(2026, 9, 6)}})
