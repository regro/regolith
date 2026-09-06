"""Tests for the mongo backed client that do not need a live mongod."""

from pathlib import Path

from regolith.mongoclient import MongoClient


class FakePymongoCollection:
    """A stand-in for a pymongo Collection that records the queries it
    is asked, so a test can tell a pushed down query from a full
    read."""

    def __init__(self, docs, queries):
        self._docs = docs
        self.queries = queries

    def find_one(self, filter):
        self.queries.append(("find_one", filter))
        for doc in self._docs:
            if all(doc.get(key) == value for key, value in filter.items()):
                return doc
        return None

    def find(self, filter=None):
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


def test_get_asks_the_server_for_one_document():
    # Test that reading one document sends an _id query to the server rather
    # than reading the collection, which is the whole point of the method
    docs = [{"_id": "scopatz", "name": "Anthony Scopatz"}, {"_id": "sbillinge", "name": "Simon Billinge"}]
    client, queries = _client_with({"people": docs})
    assert client.get("test", "people", "scopatz")["name"] == "Anthony Scopatz"
    assert queries == [("find_one", {"_id": "scopatz"})]


def test_get_returns_none_when_the_server_has_no_such_document():
    # Test the miss, which must not raise
    client, _ = _client_with({"people": [{"_id": "scopatz", "name": "Anthony Scopatz"}]})
    assert client.get("test", "people", "nobody") is None


def test_find_sends_the_filter_to_the_server():
    # Test that the filter is pushed down, so only matching documents cross
    # the network rather than the whole collection
    docs = [
        {"_id": "scopatz", "position": "prof"},
        {"_id": "sbillinge", "position": "prof"},
        {"_id": "student", "position": "grad"},
    ]
    client, queries = _client_with({"people": docs})
    found = [doc["_id"] for doc in client.find("test", "people", {"position": "prof"})]
    assert found == ["scopatz", "sbillinge"]
    assert queries == [("find", {"position": "prof"})]


def test_find_without_a_filter_reads_the_whole_collection():
    # Test that an absent filter still becomes a valid empty mongo query
    docs = [{"_id": "scopatz"}, {"_id": "sbillinge"}]
    client, queries = _client_with({"people": docs})
    assert [doc["_id"] for doc in client.find("test", "people")] == ["scopatz", "sbillinge"]
    assert queries == [("find", {})]
