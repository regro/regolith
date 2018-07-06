"""API for accessing the metadata and file storage"""
from regolith.database import connect, dump_database
from regolith.main import DEFAULT_RC, load_rcfile, filter_databases
from regolith.storage import store_client, push


def load_db(rc_file='regolithrc.json'):
    rc = DEFAULT_RC
    rc._update(load_rcfile(rc_file))
    filter_databases(rc)
    return Broker(rc)


class Broker:
    def __init__(self, rc=DEFAULT_RC):
        self.rc = rc
        # TODO: Lazy load these
        with connect(rc) as rc.client, store_client(rc) as sclient:
            self._dbs = rc.client.dbs
            self.md = rc.client.chained_db
            self.db_client = rc.client
            self.store = sclient

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

        Returns
        -------

        """
        output_path = self.store.copydoc(filepath)
        if 'files' not in document:
            document['files'] = {}
        document['files'][name] = output_path
        for db in self.rc.databases:
            dump_database(db, self.db_client, self.rc)
        push(self.store.store, self.store.path)

    @classmethod
    def from_rc(cls, rc_file='regolithrc.json'):
        return load_db(rc_file)

    def get_file(self, document, name):
        return self.store.retrieve(document['files'][name])

    def __getitem__(self, item):
        return self.md[item]
