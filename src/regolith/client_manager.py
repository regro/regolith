from collections import defaultdict
from copy import deepcopy

from regolith.fsclient import FileSystemClient
from regolith.mongoclient import MongoClient

CLIENTS = {
    "mongo": MongoClient,
    "mongodb": MongoClient,
    "fs": FileSystemClient,
    "filesystem": FileSystemClient,
}


class ClientManager:
    """Client wrapper that allows for multiple backend clients to be
    used in parallel with one chained DB."""

    def __init__(self, databases, rc):
        client_tuple = tuple()
        if hasattr(rc, "backend"):
            for database in databases:
                database["backend"] = rc.backend
        for database in databases:
            if "backend" not in database:
                database["backend"] = "filesystem"
            backend_object_type = CLIENTS[database["backend"]]
            # Checks to see if the clients tuple contains a client with the database's backend
            if len(client_tuple) == 0:
                client_tuple = client_tuple + (CLIENTS[database["backend"]](rc),)
            elif True not in [isinstance(client, backend_object_type) for client in client_tuple]:
                client_tuple = client_tuple + (CLIENTS[database["backend"]](rc),)
        self.clients = client_tuple
        self.rc = rc
        self.closed = True
        self.chained_db = None
        # self.open()
        self._collfiletypes = {}
        self._collexts = {}
        self._yamlinsts = {}

    def __getattr__(self, attr):
        if attr == "dbs":
            concatenated_dbs_dict = defaultdict(lambda: defaultdict(dict))
            for client in self.clients:
                concatenated_dbs_dict.update(client.dbs)
            return concatenated_dbs_dict
        else:
            raise AttributeError

    def __getitem__(self, key):
        for client in self.clients:
            if key in client.keys():
                return client[key]

    def open(self):
        """Opens the database connections."""
        for client in self.clients:
            client.open()

    def close(self):
        """Closes the database connections."""
        for client in self.clients:
            client.close()

    def load_database(self, db):
        for client in self.clients:
            if isinstance(client, CLIENTS[db["backend"]]):
                client.load_database(db)

    def import_database(self, db: dict):
        for client in self.clients:
            if isinstance(client, MongoClient):
                client.import_database(db)

    def export_database(self, db: dict):
        for client in self.clients:
            if isinstance(client, MongoClient):
                client.export_database(db)

    def dump_database(self, db):
        to_add = []
        # Iterate through the clients just in case databases on different backends have same name
        for client in self.clients:
            if isinstance(client, CLIENTS[db["backend"]]):
                if db["name"] in client.keys():
                    temp_add = client.dump_database(db)
                    if temp_add:
                        to_add.extend(temp_add)
        return to_add

    def keys(self):
        keys = []
        for client in self.clients:
            keys.append(client.keys())
        return keys

    def collection_names(self, dbname, include_system_collections=True):
        """Returns the collection names for a database."""
        for client in self.clients:
            if dbname in client.keys():
                return client.collection_names(dbname)

    def all_documents(self, collname, copy=True):
        """Returns an iterable over all documents in a collection."""
        if copy:
            return deepcopy(self.chained_db.get(collname, {})).values()
        return self.chained_db.get(collname, {}).values()

    def insert_one(self, dbname, collname, doc):
        """Inserts one document to a database/collection."""
        for client in self.clients:
            if dbname in client.keys():
                client.insert_one(dbname, collname, doc)

    def insert_many(self, dbname, collname, docs):
        """Inserts many documents into a database/collection."""
        for client in self.clients:
            if dbname in client.keys():
                client.insert_many(dbname, collname, docs)

    def delete_one(self, dbname, collname, doc):
        """Removes a single document from a collection."""
        for client in self.clients:
            if dbname in client.keys():
                client.delete_one(dbname, collname, doc)

    def find_one(self, dbname, collname, filter):
        """Finds the first document matching filter."""
        for client in self.clients:
            if dbname in client.keys():
                return client.find_one(dbname, collname, filter)

    def update_one(self, dbname, collname, filter, update, **kwargs):
        """Updates one document."""
        for client in self.clients:
            if dbname in client.keys():
                client.update_one(dbname, collname, filter, update, **kwargs)
