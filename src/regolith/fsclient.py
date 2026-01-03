"""Contains a client database backed by the file system."""

import datetime
import json
import logging
import os
import signal
import sys
from collections import defaultdict
from copy import deepcopy
from glob import iglob

import ruamel.yaml
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

from regolith.tools import dbpathname


class DelayedKeyboardInterrupt:

    def __enter__(self):
        self.signal_received = False
        self.old_handler = signal.signal(signal.SIGINT, self.handler)

    def handler(self, sig, frame):
        self.signal_received = (sig, frame)
        logging.debug("SIGINT received. Delaying KeyboardInterrupt.")

    def __exit__(self, type, value, traceback):
        signal.signal(signal.SIGINT, self.old_handler)
        if self.signal_received:
            self.old_handler(*self.signal_received)


YAML_BASE_MAP = {CommentedMap: dict, CommentedSeq: list}


def _rec_re_type(i):
    """Destroy this when ruamel.yaml supports basetypes again."""
    if type(i) in YAML_BASE_MAP:
        base = YAML_BASE_MAP[type(i)]()
        if isinstance(base, dict):
            for k, v in i.items():
                base[_rec_re_type(k)] = _rec_re_type(v)
        elif isinstance(base, list):
            for j in i:
                base.append(_rec_re_type(j))
    else:
        base = i
    return base


def _id_key(doc):
    return doc["_id"]


def load_json(filename):
    """Loads a JSON file and returns a dict of its documents."""
    docs = {}
    with open(filename, encoding="utf-8") as fh:
        lines = fh.readlines()
    for line in lines:
        doc = json.loads(line)
        docs[doc["_id"]] = doc
    return docs


def date_encoder(obj):
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()


def dump_json(filename, docs, date_handler=None):
    """Dumps a dict of documents into a file."""
    docs = sorted(docs.values(), key=_id_key)
    lines = [json.dumps(doc, sort_keys=True, default=date_handler) for doc in docs]
    s = "\n".join(lines)
    with open(filename, "w", encoding="utf-8") as fh:
        fh.write(s)


def load_yaml(filename, return_inst=False, loader=None):
    """Loads a YAML file and returns a dict of its documents."""
    if loader is None:
        inst = YAML()
    else:
        inst = loader
    with open(filename, encoding="utf-8") as fh:
        docs = inst.load(fh)
        docs = _rec_re_type(docs)
    for _id, doc in docs.items():
        doc["_id"] = _id
    return (docs, inst) if return_inst else docs


def dump_yaml(filename, docs, inst=None):
    """Dumps a dict of documents into a file."""
    inst = YAML() if inst is None else inst
    inst.representer.ignore_aliases = lambda *data: True
    inst.indent(mapping=2, sequence=4, offset=2)
    sorted_dict = ruamel.yaml.comments.CommentedMap()
    for k in sorted(docs):
        doc = docs[k]
        doc.pop("_id")
        sorted_dict[k] = ruamel.yaml.comments.CommentedMap()
        for kk in sorted(doc.keys()):
            sorted_dict[k][kk] = doc[kk]
    with open(filename, "w", encoding="utf-8") as fh:
        with DelayedKeyboardInterrupt():
            inst.dump(sorted_dict, stream=fh)


def json_to_yaml(inp, out):
    """Converts a JSON file to a YAML one."""
    docs = load_json(inp)
    dump_yaml(out, docs)


def yaml_to_json(inp, out, loader=None):
    """Converts a YAML file to a JSON one."""
    docs = load_yaml(inp, loader=loader)
    dump_json(out, docs)


class FileSystemClient:
    """A client database backed by the file system."""

    def __init__(self, rc):
        self.rc = rc
        self.closed = True
        self.dbs = None
        self.chained_db = None
        self.open()
        self._collfiletypes = {}
        self._collexts = {}
        self._yamlinsts = {}

    def is_alive(self):
        return not self.closed

    def open(self):
        if self.closed:
            self.dbs = defaultdict(lambda: defaultdict(dict))
            self.chained_db = {}
            self.closed = False

    def load_json(self, db, dbpath):
        """Loads the JSON part of a database."""
        dbs = self.dbs
        for f in [
            file
            for file in iglob(os.path.join(dbpath, "*.json"))
            if file not in db["blacklist"]
            and len(db["whitelist"]) == 0
            or os.path.basename(file).split(".")[0] in db["whitelist"]
        ]:
            collfilename = os.path.split(f)[-1]
            base, ext = os.path.splitext(collfilename)
            self._collfiletypes[base] = "json"
            print("loading " + f + "...", file=sys.stderr)
            dbs[db["name"]][base] = load_json(f)

    def load_yaml(self, db, dbpath):
        """Loads the YAML part of a database."""
        dbs = self.dbs
        for f in [
            file
            for file in iglob(os.path.join(dbpath, "*.y*ml"))
            if file not in db["blacklist"]
            and len(db["whitelist"]) == 0
            or os.path.basename(file).split(".")[0] in db["whitelist"]
        ]:
            collfilename = os.path.split(f)[-1]
            base, ext = os.path.splitext(collfilename)
            self._collexts[base] = ext
            self._collfiletypes[base] = "yaml"
            # print("loading " + f + "...", file=sys.stderr)
            coll, inst = load_yaml(f, return_inst=True)
            dbs[db["name"]][base] = coll
            self._yamlinsts[dbpath, base] = inst

    def load_database(self, db):
        """Loads a database."""
        dbpath = dbpathname(db, self.rc)
        self.load_json(db, dbpath)
        self.load_yaml(db, dbpath)

    def dump_json(self, docs, collname, dbpath):
        """Dumps json docs and returns filename."""
        f = os.path.join(dbpath, collname + ".json")
        dump_json(f, docs)
        filename = os.path.split(f)[-1]
        return filename

    def dump_yaml(self, docs, collname, dbpath):
        """Dumps json docs and returns filename."""
        f = os.path.join(dbpath, collname + self._collexts.get(collname, ".yaml"))
        inst = self._yamlinsts.get((dbpath, collname), None)
        dump_yaml(f, docs, inst=inst)
        filename = os.path.split(f)[-1]
        return filename

    def dump_database(self, db):
        """Dumps a database back to the filesystem."""
        dbpath = dbpathname(db, self.rc)
        os.makedirs(dbpath, exist_ok=True)
        to_add = []
        for collname, collection in self.dbs[db["name"]].items():
            # print("dumping " + collname + "...", file=sys.stderr)
            filetype = self._collfiletypes.get(collname, "yaml")
            if filetype == "json":
                filename = self.dump_json(collection, collname, dbpath)
            elif filetype == "yaml":
                filename = self.dump_yaml(collection, collname, dbpath)
            else:
                raise ValueError("did not recognize file type for regolith")
            to_add.append(os.path.join(db["path"], filename))
        return to_add

    def close(self):
        self.dbs = None
        self.closed = True

    def keys(self):
        return self.dbs.keys()

    def __getitem__(self, key):
        return self.dbs[key]

    def collection_names(self, dbname, include_system_collections=True):
        """Returns the collection names for a database."""
        return set(self.dbs[dbname].keys())

    def all_documents(self, collname, copy=True):
        """Returns an iterable over all documents in a collection."""
        if copy:
            return deepcopy(self.chained_db.get(collname, {})).values()
        return self.chained_db.get(collname, {}).values()

    def insert_one(self, dbname, collname, doc):
        """Inserts one document to a database/collection."""
        coll = self.dbs[dbname][collname]
        coll[doc["_id"]] = doc

    def insert_many(self, dbname, collname, docs):
        """Inserts many documents into a database/collection."""
        coll = self.dbs[dbname][collname]
        for doc in docs:
            coll[doc["_id"]] = doc

    def delete_one(self, dbname, collname, doc):
        """Removes a single document from a collection."""
        coll = self.dbs[dbname][collname]
        del coll[doc["_id"]]

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
        coll[newdoc["_id"]] = newdoc
