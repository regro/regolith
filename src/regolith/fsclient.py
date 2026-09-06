"""Contains a client database backed by the file system."""

import datetime
import json
import logging
import signal
from collections import defaultdict
from copy import deepcopy
from pathlib import Path

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


logger = logging.getLogger(__name__)

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


def doc_matches(doc, filter):
    """Return True if a document has every key and value of a filter.

    Parameters
    ----------
    doc : dict
        The document to test.
    filter : dict or None
        The keys and values the document must have.  An empty or absent
        filter matches every document.

    Returns
    -------
    bool
        Whether the document matches.
    """
    if not filter:
        return True
    for key, value in filter.items():
        if key not in doc or doc[key] != value:
            return False
    return True


def load_json(filename):
    """Loads a JSON file and returns a dict of its documents."""
    docs = {}
    with Path(filename).open(encoding="utf-8") as fh:
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
    with Path(filename).open("w", encoding="utf-8") as fh:
        fh.write(s)


def load_yaml(filename, return_inst=False, loader=None):
    """Loads a YAML file and returns a dict of its documents."""
    if loader is None:
        inst = YAML()
    else:
        inst = loader
    with Path(filename).open(encoding="utf-8") as fh:
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
    with Path(filename).open("w", encoding="utf-8") as fh:
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
        self._dirty = set()
        self._available = {}
        self._loaded = set()
        self._dbpaths = {}
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
            self._dirty = set()
            self._available = {}
            self._loaded = set()
            self._dbpaths = {}
            self.closed = False

    def mark_dirty(self, dbname, collname):
        """Record that a collection has changes that are not yet on
        disk.

        Parameters
        ----------
        dbname : str
            The name of the database holding the collection.
        collname : str
            The name of the collection that was modified.
        """
        self._dirty.add((dbname, collname))

    def is_dirty(self, dbname, collname=None):
        """Return True if a collection, or any collection of a database,
        has changes that are not yet on disk.

        Parameters
        ----------
        dbname : str
            The name of the database to check.
        collname : str, optional
            The name of the collection to check.  The default checks
            every collection of the database.

        Returns
        -------
        bool
            The dirty state of the requested collection or database.
        """
        if collname is not None:
            return (dbname, collname) in self._dirty
        return any(dirty_dbname == dbname for dirty_dbname, _ in self._dirty)

    def _collection_files(self, db):
        """Return the file of each collection of a database.

        The files are not read, so this costs one directory listing and no
        parsing.

        Parameters
        ----------
        db : dict
            The database description, supplying ``blacklist`` and
            ``whitelist``.

        Returns
        -------
        dict
            The path of each collection, keyed by collection name.
        """
        dbpath = dbpathname(db, self.rc)
        files = {}
        for pattern in ("*.json", "*.y*ml"):
            for f in sorted(Path(dbpath).glob(pattern)):
                if not (
                    str(f) not in db["blacklist"]
                    and len(db["whitelist"]) == 0
                    or f.name.split(".")[0] in db["whitelist"]
                ):
                    continue
                files[f.stem] = f
        return files

    def load_database(self, db):
        """Record which collections a database holds, without reading
        them.

        The documents of a collection are read by ``load_collection``, when
        something first asks for them.

        Parameters
        ----------
        db : dict
            The database description.
        """
        dbname = db["name"]
        self._dbpaths[dbname] = dbpathname(db, self.rc)
        files = self._collection_files(db)
        self._available[dbname] = files
        for collname, f in files.items():
            if f.suffix == ".json":
                self._collfiletypes[collname] = "json"
            else:
                self._collexts[collname] = f.suffix
                self._collfiletypes[collname] = "yaml"

    def available_collections(self, dbname):
        """Return the names of the collections a database holds.

        Parameters
        ----------
        dbname : str
            The name of the database to list.

        Returns
        -------
        set of str
            The collection names, whether or not they have been read.
        """
        return set(self._available.get(dbname, {}))

    def load_collection(self, dbname, collname):
        """Read one collection into memory unless it is already there.

        Parameters
        ----------
        dbname : str
            The name of the database holding the collection.
        collname : str
            The name of the collection to read.
        """
        if (dbname, collname) in self._loaded:
            return
        f = self._available.get(dbname, {}).get(collname)
        if f is None:
            return
        logger.debug("loading %s", f)
        if self._collfiletypes.get(collname) == "json":
            docs = load_json(f)
        else:
            docs, inst = load_yaml(f, return_inst=True)
            self._yamlinsts[self._dbpaths[dbname], collname] = inst
        self.dbs[dbname][collname] = docs
        self._loaded.add((dbname, collname))

    def raw_collection(self, dbname, collname):
        """Return the documents of one collection as this database holds
        them, unmerged with any other database.

        Parameters
        ----------
        dbname : str
            The name of the database holding the collection.
        collname : str
            The name of the collection to read.

        Returns
        -------
        dict
            The documents, keyed by id.
        """
        self.load_collection(dbname, collname)
        return self.dbs.get(dbname, {}).get(collname, {})

    def dump_json(self, docs, collname, dbpath):
        """Dumps json docs and returns filename."""
        f = Path(dbpath) / (collname + ".json")
        dump_json(f, docs)
        return f.name

    def dump_yaml(self, docs, collname, dbpath):
        """Dumps json docs and returns filename."""
        f = Path(dbpath) / (collname + self._collexts.get(collname, ".yaml"))
        inst = self._yamlinsts.get((Path(dbpath), collname), None)
        dump_yaml(f, docs, inst=inst)
        return f.name

    def dump_database(self, db, force=False):
        """Dump the modified collections of a database back to the
        filesystem.

        A collection is written only if it was modified since it was
        loaded, so a command that reads without writing leaves the
        database files untouched.

        Parameters
        ----------
        db : dict
            The database description, supplying ``name`` and ``path``.
        force : bool, optional
            The switch to write every loaded collection rather than only
            the modified ones.  The default is False.

        Returns
        -------
        list of str
            The paths, relative to the database directory, of the files
            that were written.
        """
        dbname = db["name"]
        collnames = [collname for collname in self.dbs[dbname] if force or self.is_dirty(dbname, collname)]
        if not collnames:
            return []
        dbpath = dbpathname(db, self.rc)
        Path(dbpath).mkdir(parents=True, exist_ok=True)
        to_add = []
        for collname in collnames:
            # logger.debug("dumping %s", collname)
            collection = self.dbs[dbname][collname]
            filetype = self._collfiletypes.get(collname, "yaml")
            if filetype == "json":
                filename = self.dump_json(collection, collname, dbpath)
            elif filetype == "yaml":
                filename = self.dump_yaml(collection, collname, dbpath)
            else:
                raise ValueError("did not recognize file type for regolith")
            to_add.append(str(Path(db["path"]) / filename))
            self._dirty.discard((dbname, collname))
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
        return self.available_collections(dbname)

    def all_documents(self, collname, copy=True):
        """Returns an iterable over all documents in a collection."""
        if copy:
            return deepcopy(self.chained_db.get(collname, {})).values()
        return self.chained_db.get(collname, {}).values()

    def insert_one(self, dbname, collname, doc):
        """Inserts one document to a database/collection."""
        self.load_collection(dbname, collname)
        coll = self.dbs[dbname][collname]
        coll[doc["_id"]] = doc
        self.mark_dirty(dbname, collname)

    def insert_many(self, dbname, collname, docs):
        """Inserts many documents into a database/collection."""
        self.load_collection(dbname, collname)
        coll = self.dbs[dbname][collname]
        for doc in docs:
            coll[doc["_id"]] = doc
            self.mark_dirty(dbname, collname)

    def delete_one(self, dbname, collname, doc):
        """Removes a single document from a collection."""
        self.load_collection(dbname, collname)
        coll = self.dbs[dbname][collname]
        del coll[doc["_id"]]
        self.mark_dirty(dbname, collname)

    def get(self, dbname, collname, _id):
        """Return one document of a collection by id.

        Parameters
        ----------
        dbname : str
            The name of the database holding the collection.
        collname : str
            The name of the collection to read.
        _id : str
            The id of the document.

        Returns
        -------
        dict or None
            The document, or None when the database has no such document.
        """
        return self.raw_collection(dbname, collname).get(_id)

    def find(self, dbname, collname, filter=None):
        """Yield the documents of a collection that match a filter.

        Parameters
        ----------
        dbname : str
            The name of the database holding the collection.
        collname : str
            The name of the collection to read.
        filter : dict, optional
            The keys and values a document must have.  The default
            yields every document of the collection.

        Yields
        ------
        dict
            The matching documents.
        """
        for doc in self.raw_collection(dbname, collname).values():
            if doc_matches(doc, filter):
                yield doc

    def find_one(self, dbname, collname, filter):
        """Finds the first document matching filter."""
        # An id is unique, so look it up rather than scanning the collection
        if filter and set(filter) == {"_id"}:
            return self.get(dbname, collname, filter["_id"])
        for doc in self.find(dbname, collname, filter):
            return doc

    def update_one(self, dbname, collname, filter, update, **kwargs):
        """Updates one document."""
        self.load_collection(dbname, collname)
        coll = self.dbs[dbname][collname]
        doc = self.find_one(dbname, collname, filter)
        newdoc = dict(filter if doc is None else doc)
        newdoc.update(update)
        coll[newdoc["_id"]] = newdoc
        self.mark_dirty(dbname, collname)
