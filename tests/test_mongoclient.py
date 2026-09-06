"""Tests for the mongo backed client that do not need a live mongod."""

from pathlib import Path

from regolith.mongoclient import MongoClient


class FakePymongoDatabase:
    """A stand-in for a pymongo Database that offers only the collection
    listing call that pymongo 4 still provides."""

    def __init__(self, collection_names):
        self._collection_names = collection_names

    def list_collection_names(self):
        return list(self._collection_names)

    def __getattr__(self, name):
        # pymongo 4 removed Database.collection_names, so reaching for any
        # other attribute is the regression these tests guard against.
        raise AttributeError(f"pymongo 4 Database has no attribute {name!r}")


def _client_with(collection_names):
    """Build a MongoClient whose pymongo client is the fake database."""
    client = MongoClient.__new__(MongoClient)
    client.client = {"test": FakePymongoDatabase(collection_names)}
    client.rc = None
    return client


def test_collection_names_uses_the_pymongo_4_api():
    # Test listing the collections of a database, which must go through
    # list_collection_names because pymongo 4 removed collection_names
    client = _client_with(["people", "todos"])
    assert client.collection_names("test") == ["people", "todos"]


def test_dump_database_lists_collections_with_the_pymongo_4_api(mocker, tmp_path):
    # Test that dumping a mongo database lists its collections through the
    # pymongo 4 API, so that a mongo to filesystem backup does not fail
    mocker.patch("regolith.mongoclient.subprocess.check_call")
    client = _client_with(["people"])
    db = {"name": "test", "url": str(tmp_path), "path": "db", "local": True}
    to_add = client.dump_database(db)
    assert to_add == [str(Path("db") / "people.json")]
