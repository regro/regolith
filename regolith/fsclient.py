"""Contains a client database backed by the file system."""
import os
import sys
import json
import yaml
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
        self._collfiletypes = {}

    def is_alive(self):
        return not self.closed

    def open(self):
        self.dbs = defaultdict(lambda: defaultdict(dict))
        self.closed = False

    def load_database(self, db):
        """Loads a database."""
        dbs = self.dbs
        dbpath = dbpathname(db, self.rc)
        for f in iglob(os.path.join(dbpath, '*.json')):
            collfilename = os.path.split(f)[-1]
            base, ext = os.path.splitext(collfilename)
            self._collfiletypes[base] = 'json'
            print('loading ' + f + '...', file=sys.stderr)
            with open(f) as fh:
                lines = fh.readlines()
            for line in lines:
                doc = json.loads(line)
                dbs[db['name']][base][doc['_id']] = doc

    @staticmethod
    def _id_key(doc):
        return doc['_id']

    def dump_json(self, docs, collname, dbpath):
        """Dumps json docs and returns filename"""
        lines = [json.dumps(doc, sort_keys=True) for doc in docs]
        s = '\n'.join(lines)
        f = os.path.join(dbpath, collname + '.json')
        with open(f, 'w') as fh:
            fh.write(s)
        return f

    def dump_database(self, db):
        """Dumps a database back to the filesystem."""
        dbpath = dbpathname(db, self.rc)
        os.makedirs(dbpath, exist_ok=True)
        to_add = []
        for collname, collection in self.dbs[db['name']].items():
            print('dumping ' + collname + '...', file=sys.stderr)
            docs = sorted(collection.values(), key=self._id_key)
            filetype = self._collfiletypes.get(collname, 'yaml')
            if filetype == 'json':
                filename = self.dump_json(docs, collname, dbpath)
            else:
                raise ValueError('did not recognize file type for regolith')
            to_add.append(filename)
        return to_add

    def close(self):
        self.dbs = None
        self.closed = True

    def keys(self):
        return self.dbs.keys()

    def __getitem__(self, key):
        return self.dbs[key]

    def collection_names(self, dbname, include_system_collections=True):
        """Returns the collaction names for a database."""
        return set(self.dbs[dbname].keys())

    def all_documents(self, dbname, collname):
        """Returns an iteratable over all documents in a collection."""
        return self.dbs[dbname][collname].values()

    def insert_one(self, dbname, collname, doc):
        """Inserts one document to a database/collection."""
        coll = self.dbs[dbname][collname]
        coll[doc['_id']] = doc

    def insert_many(self, dbname, collname, docs):
        """Inserts many documents into a database/collection."""
        coll = self.dbs[dbname][collname]
        for doc in docs:
            coll[doc['_id']] = doc

    def delete_one(self, dbname, collname, doc):
        """Removes a single document from a collection"""
        coll = self.dbs[dbname][collname]
        del coll[doc['_id']]

    def find_one(self, dbname, collname, filter):
        """Finds the first document matching filter."""
        coll = self.dbs[dbname][collname]
        for doc in coll.values():
            matches = True
            for key, value in filter.items():
                if key not in doc or doc[key] != value:
                    matches = False
                    break
            if matches:
                return doc

    def update_one(self, dbname, collname, filter, update, **kwargs):
        """Updates one document."""
        coll = self.dbs[dbname][collname]
        doc = self.find_one(dbname, collname, filter)
        newdoc = dict(filter if doc is None else doc)
        newdoc.update(update)
        coll[newdoc['_id']] = newdoc
