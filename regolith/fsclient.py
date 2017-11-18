"""Contains a client database backed by the file system."""
import os
import sys
import json
from glob import iglob
from collections import defaultdict

from ruamel.yaml import YAML

from regolith.tools import dbdirname, dbpathname


def _id_key(doc):
    return doc['_id']


def load_json(filename):
    """Loads a JSON file and returns a dict of its documents."""
    docs = {}
    with open(filename) as fh:
        lines = fh.readlines()
    for line in lines:
        doc = json.loads(line)
        docs[doc['_id']] = doc
    return docs


def dump_json(filename, docs):
    """Dumps a dict of documents into a file."""
    docs = sorted(docs.values(), key=_id_key)
    lines = [json.dumps(doc, sort_keys=True) for doc in docs]
    s = '\n'.join(lines)
    with open(filename, 'w') as fh:
        fh.write(s)


def load_yaml(filename, return_inst=False):
    """Loads a YAML file and returns a dict of its documents."""
    with open(filename) as fh:
        yaml = YAML()
        docs = yaml.load(fh)
    for _id, doc in docs.items():
        doc['_id'] = _id
    return (docs, yaml) if return_insts else docs


def dump_yaml(filename, docs, inst=None):
    """Dumps a dict of documents into a file."""
    inst = YAML() if inst is None else inst
    inst.indent(mapping=2, sequence=4, offset=2)
    for doc in docs:
        _id = doc.pop('_id')
    with open(filename, 'w') as fh:
        yaml.dump(docs, stream=fh)


def json_to_yaml(inp, out):
    """Converts a JSON file to a YAML one."""
    docs = load_json(inp)
    dump_yaml(out, docs)


def yaml_to_json(inp, out):
    """Converts a YAML file to a JSON one."""
    docs = load_yaml(inp)
    dump_json(out, docs)


class FileSystemClient:
    """A client database backed by the file system."""

    def __init__(self, rc):
        self.rc = rc
        self.closed = True
        self.dbs = None
        self.open()
        self._collfiletypes = {}
        self._collexts = {}
        self._yamlinsts = {}

    def is_alive(self):
        return not self.closed

    def open(self):
        self.dbs = defaultdict(lambda: defaultdict(dict))
        self.closed = False

    def load_json(self, db, dbpath):
        """Loads the JSON part of a database."""
        dbs = self.dbs
        for f in iglob(os.path.join(dbpath, '*.json')):
            collfilename = os.path.split(f)[-1]
            base, ext = os.path.splitext(collfilename)
            self._collfiletypes[base] = 'json'
            print('loading ' + f + '...', file=sys.stderr)
            dbs[db['name']][base] = load_json(f)

    def load_yaml(self, db, dbpath):
        """Loads the YAML part of a database."""
        dbs = self.dbs
        for f in iglob(os.path.join(dbpath, '*.ya?ml')):
            collfilename = os.path.split(f)[-1]
            base, ext = os.path.splitext(collfilename)
            self._collexts[base] = ext
            self._collfiletypes[base] = 'yaml'
            print('loading ' + f + '...', file=sys.stderr)
            dbs[db['name']][base], inst = load_yaml(f, return_inst=True)
            self._yamlinsts[dbpath, base] = inst

    def load_database(self, db):
        """Loads a database."""
        dbpath = dbpathname(db, self.rc)
        self.load_json(db, dbpath)
        self.load_yaml(db, dbpath)


    def dump_json(self, docs, collname, dbpath):
        """Dumps json docs and returns filename"""
        f = os.path.join(dbpath, collname + '.json')
        dump_json(f, docs)
        return f

    def dump_yaml(self, docs, collname, dbpath):
        """Dumps json docs and returns filename"""
        f = os.path.join(dbpath, collname + self._collexts.get(collname, '.yaml'))
        inst = self._yamlinsts.get((dbpath, collname), None)
        dump_yaml(f, docs, inst=inst)
        return f

    def dump_database(self, db):
        """Dumps a database back to the filesystem."""
        dbpath = dbpathname(db, self.rc)
        os.makedirs(dbpath, exist_ok=True)
        to_add = []
        for collname, collection in self.dbs[db['name']].items():
            print('dumping ' + collname + '...', file=sys.stderr)
            filetype = self._collfiletypes.get(collname, 'yaml')
            if filetype == 'json':
                filename = self.dump_json(collection, collname, dbpath)
            elif filetype == 'yaml':
                filename = self.dump_yaml(collection, collname, dbpath)
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
