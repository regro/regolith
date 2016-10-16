"""Contains a client database backed by the file system."""
import os
import sys
import json
from glob import iglob
from collections import defaultdict

from regolith.tools import dbdirname, dbpathname


class FileSystemClient:
    """A client database backed by the file system."""

    def __init__(self, rc):
        self.rc = rc
        self.closed = True
        self.dbs = None
        self.open()

    def is_alive(self):
        return not self.closed

    def open(self):
        self.dbs = defaultdict(lambda: deafultdict(dict))
        self.closed = False

    def load_database(self, db):
        """Loads a database."""
        dbs = self.dbs
        dbpath = dbpathname(db, self.rc)
        for f in iglob(os.path.join(dbpath, '*.json')):
            base, ext = os.path.splitext(os.path.split(f)[-1])
            print('loading ' + f + '...', file=sys.stderr)
            with open(f) as fh:
                lines = fh.readlines()
            for line in lines:
                doc = json.loads(line)
                dbs[db['name']][base][doc['_id']] = doc

    @staticmethod
    def _id_key(doc):
        return doc['_id']

    def dump_database(self, db):
        """Dumps a database back to the filesystem."""
        dbpath = dbpathname(db, self.rc)
        os.makedirs(dbpath, exist_ok=True)
        for collname, collection in self.dbs[db['name']].items():
            print('dumping ' + collname + '...', file=sys.stderr)
            docs = sorted(collection.values(), key=self._id_key)
            lines = [json.dumps(doc, sort_keys=True) for doc in docs]
            s = '\n'.join(lines)
            f = os.path.join(dbpath, collname + '.json')
            with open(f, 'w') as fh:
                fh.write(s)

    def close(self):
        self.dbs = None
        self.closed = True

    def keys(self):
        return self.dbs.keys()

    def __getitem__(self, key):
        return self.dbs[key]

    def collection_names(self, dbname):
        """Returns the collaction names for a database."""
        return set(self.dbs[dbname].keys())

    def all_documents(self, dbname, collname):
        """Returns an iteratable over all documents in a collection."""
        return self.dbs[dbname][collname].values()
