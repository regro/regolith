from collections import defaultdict
from copy import deepcopy

from regolith.chained_db import ChainDB
from regolith.fsclient import FileSystemClient, doc_matches
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
        self._sources = {}
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
        self._sources = {}
        for client in self.clients:
            client.open()

    def close(self):
        """Closes the database connections."""
        for client in self.clients:
            client.close()

    def load_database(self, db):
        """Record which collections a database holds, without reading
        them.

        Parameters
        ----------
        db : dict
            The database description, supplying ``name`` and ``backend``.
        """
        for client in self.clients:
            if isinstance(client, CLIENTS[db["backend"]]):
                client.load_database(db)
                for collname in client.available_collections(db["name"]):
                    self._sources.setdefault(collname, []).append(db)

    def collection_sources(self, collname):
        """Return the databases that hold a collection.

        The list is in ``rc.databases`` order, which is the order the
        merge resolves in.

        Parameters
        ----------
        collname : str
            The name of the collection.

        Returns
        -------
        list of dict
            The descriptions of the databases holding the collection.
        """
        return self._sources.get(collname, [])

    def chained_collection_names(self):
        """Return the names of every collection any database holds.

        Returns
        -------
        set of str
            The collection names.
        """
        return set(self._sources)

    def load_collection(self, collname):
        """Read one collection into memory from each database that holds
        it.

        Parameters
        ----------
        collname : str
            The name of the collection to read.
        """
        for db in self.collection_sources(collname):
            client = self._client_for(db)
            if client is not None:
                client.load_collection(db["name"], collname)

    def chain_collection(self, collname):
        """Build the chained view of one collection.

        Parameters
        ----------
        collname : str
            The name of the collection to chain.

        Returns
        -------
        dict
            The merged documents, keyed by id.

        Raises
        ------
        KeyError
            When no database holds the collection.
        """
        sources = self.collection_sources(collname)
        if not sources:
            raise KeyError(collname)
        chained = {}
        for db in sources:
            client = self._client_for(db)
            if client is None:
                continue
            for _id, doc in client.raw_collection(db["name"], collname).items():
                if _id in chained:
                    chained[_id].maps.append(doc)
                else:
                    chained[_id] = ChainDB(doc)
        return chained

    def import_database(self, db: dict):
        for client in self.clients:
            if isinstance(client, MongoClient):
                client.import_database(db)

    def export_database(self, db: dict):
        for client in self.clients:
            if isinstance(client, MongoClient):
                client.export_database(db)

    def dump_database(self, db, force=False):
        """Dump a database with each client that backs it.

        Parameters
        ----------
        db : dict
            The database description, supplying ``name`` and ``backend``.
        force : bool, optional
            The switch to write every loaded collection rather than only
            the modified ones.  The default is False.

        Returns
        -------
        list of str
            The paths, relative to the database directory, of the files
            that were written.
        """
        to_add = []
        # Iterate through the clients just in case databases on different backends have same name
        for client in self.clients:
            if isinstance(client, CLIENTS[db["backend"]]):
                if db["name"] in client.keys():
                    temp_add = client.dump_database(db, force=force)
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

    def _client_for(self, db):
        """Return the client that backs a database, or None.

        Parameters
        ----------
        db : dict
            The database description, supplying ``backend``.

        Returns
        -------
        FileSystemClient, MongoClient or None
            The client for the database's backend.
        """
        for client in self.clients:
            if isinstance(client, CLIENTS[db["backend"]]):
                return client
        return None

    def _chain(self, docs):
        """Merge the versions of one document held by several databases.

        Parameters
        ----------
        docs : list of dict
            The versions of the document, ordered as ``rc.databases`` is,
            so that the merge resolves the way ``open_dbs`` does.

        Returns
        -------
        dict, ChainDB or None
            The single document when only one database holds it, a
            ChainDB over all of them when several do, and None when the
            list is empty.
        """
        if not docs:
            return None
        if len(docs) == 1:
            return docs[0]
        chained = ChainDB(docs[0])
        for doc in docs[1:]:
            chained.maps.append(doc)
        return chained

    def get(self, collname, _id, copy=True):
        """Return one document of a collection by id, chained across the
        databases that hold it.

        Each database is asked for the single document rather than for
        the whole collection, so a mongo backend answers from its index
        on ``_id``.

        Parameters
        ----------
        collname : str
            The name of the collection to read.
        _id : str
            The id of the document.
        copy : bool, optional
            The switch to return a copy rather than the client's own
            document.  Mutating an uncopied document changes state the
            client does not know it has to write.  The default is True.

        Returns
        -------
        dict, ChainDB or None
            The merged document, or None when no database holds it.
        """
        docs = []
        for db in self.collection_sources(collname):
            client = self._client_for(db)
            if client is None:
                continue
            doc = client.get(db["name"], collname, _id)
            if doc is not None:
                docs.append(doc)
        chained = self._chain(docs)
        if chained is None:
            return None
        return deepcopy(chained) if copy else chained

    def find(self, collname, filter=None, copy=True):
        """Yield the documents of a collection that match a filter,
        chained across the databases that hold them.

        A document is matched on its merged value, which no single
        database knows, so the versions are gathered per database and the
        filter is applied to the merge.  Each database is read once.

        Parameters
        ----------
        collname : str
            The name of the collection to read.
        filter : dict, optional
            The keys and values a document must have.  The default
            yields every document of the collection.
        copy : bool, optional
            The switch to yield copies rather than the clients' own
            documents.  The default is True.

        Yields
        ------
        dict or ChainDB
            The matching merged documents.
        """
        versions = {}
        for db in self.collection_sources(collname):
            client = self._client_for(db)
            if client is None:
                continue
            for doc in client.find(db["name"], collname):
                versions.setdefault(doc["_id"], []).append(doc)
        for docs in versions.values():
            merged = self._chain(docs)
            if doc_matches(merged, filter):
                yield deepcopy(merged) if copy else merged

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
