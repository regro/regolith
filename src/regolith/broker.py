"""API for accessing the metadata and file storage."""

import copy

from regolith.database import dump_database, open_dbs
from regolith.runcontrol import DEFAULT_RC, filter_databases, load_rcfile
from regolith.storage import push, store_client


def load_db(rc_file="regolithrc.json"):
    """Create a Broker instance from an rc file."""
    rc = copy.copy(DEFAULT_RC)
    rc._update(load_rcfile(rc_file))
    filter_databases(rc)
    return Broker(rc)


class Broker:
    """Interface to the database and file storage systems.

    Examples
    --------

    >>> # Load the db
    >>> db = Broker.from_rc()
    >>> # Get a document from the broker
    >>> ergs =db['group']['ergs']
    >>> # Store a file
    >>> db.add_file(ergs, 'myfile', '/path/to/file/hello.txt')
    >>> # Get a file from the store
    >>> path = db.get_file_path(ergs, 'myfile')
    """

    def __init__(self, rc=DEFAULT_RC):
        self.rc = rc
        # TODO: Lazy load these
        with store_client(rc) as sclient:
            self.store = sclient
        rc.client = open_dbs(rc)
        self._dbs = rc.client.dbs
        self.md = rc.client.chained_db
        self.db_client = rc.client

    def add_file(self, document, name, filepath):
        """Add a file to a document in a collection.

        Parameters
        ----------
        document : dict
            The document to add the file to
        name : str
            Name of the reference to the file
        filepath : str
            Location of the file on local disk
        """
        output_path = self.store.copydoc(filepath)
        if "files" not in document:
            document["files"] = {}
        document["files"][name] = output_path
        for db in self.rc.databases:
            dump_database(db, self.db_client, self.rc)
        push(self.store.store, self.store.path)

    @classmethod
    def from_rc(cls, rc_file="regolithrc.json"):
        """Return a Broker instance."""
        return load_db(rc_file)

    def get_file_path(self, document, name):
        """Get a file from the file storage associated with the document
        and name.

        Parameters
        ----------
        document : dict
            The document which stores the reference to the file
        name : str
            The name of the file stored (note that this can be different from
            the filename itself)

        Returns
        -------
        path : str or None
            The file path, if not in the storage None
        """
        if "files" in document:
            return self.store.retrieve(document["files"][name])
        else:
            return None

    def __getitem__(self, item):
        return self.md[item]
