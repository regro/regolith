"""Client interface for MongoDB."""
import itertools
import os
import shutil
import subprocess
import sys
import time
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

from ruamel.yaml import YAML

#
# setup mongo
#
try:
    import pymongo

    MONGO_AVAILABLE = True
except ImportError:
    print(
        "pymongo not found. Please install it following the instructions "
        "https://pymongo.readthedocs.io/en/stable/installation.html"
    )
    MONGO_AVAILABLE = False

from pymongo.collection import Collection

from regolith.tools import dbpathname, fallback
from regolith import fsclient

if not MONGO_AVAILABLE:
    ON_PYMONGO_V2 = ON_PYMONGO_V3 = False
elif pymongo.version.split(".")[0] == "2":
    ON_PYMONGO_V2 = True
    ON_PYMONGO_V3 = False
else:
    ON_PYMONGO_V2 = False
    ON_PYMONGO_V3 = True


def import_jsons(dbpath: str, dbname: str, host: str = None, uri: str = None) -> None:
    """Import the json files to mongo db.

    Each json file will be a collection in the database. The _id will be the same as it is in the json file.

    Parameters
    ----------
    dbpath : str
        The path to the db folder.

    dbname : str
        The name of the database in mongo.

    host : str
        The hostname or IP address or Unix domain socket path of a single mongod or mongos instance to connect
        to, or a mongodb URI, or a list of hostnames / mongodb URIs.

    uri : str
        Specify a resolvable URI connection string (enclose in quotes) to connect to the MongoDB deployment.
    """
    for json_path in Path(dbpath).glob("*.json"):
        cmd = ["mongoimport"]
        if host is not None:
            cmd += ['--host', host, "--db", dbname]
        if uri is not None:
            cmd += ['--uri', uri]
        cmd += ["--collection", json_path.stem, "--file", str(json_path)]
        subprocess.check_call(cmd)
    return


def import_yamls(dbpath: str, dbname: str, host: str = None, uri: str = None) -> None:
    """Import the yaml files to mongo db.

    Each yaml file will be a collection in the database. The _id will be the id_key for each doc in the yaml file.

    Parameters
    ----------
    dbpath : str
        The path to the db folder.

    dbname : str
        The name of the database in mongo.

    host : str
        The hostname or IP address or Unix domain socket path of a single mongod or mongos instance to connect
        to, or a mongodb URI, or a list of hostnames / mongodb URIs.

    uri : str
        Specify a resolvable URI connection string (enclose in quotes) to connect to the MongoDB deployment.
    """
    yaml_files = itertools.chain(Path(dbpath).glob('*.yaml'), Path(dbpath).glob('*.yml'))
    with TemporaryDirectory() as tempd:
        for yaml_file in yaml_files:
            json_file = Path(tempd).joinpath(yaml_file.with_suffix('.json').name)
            loader = YAML(typ='safe')
            loader.constructor.yaml_constructors[u'tag:yaml.org,2002:timestamp'] = \
                loader.constructor.yaml_constructors[u'tag:yaml.org,2002:str']
            fsclient.yaml_to_json(str(yaml_file), str(json_file), loader=loader)
        import_jsons(tempd, dbname, host=host, uri=uri)
    return


def load_mongo_col(col: Collection) -> dict:
    """Load the pymongo collection to a dictionary.

    In the dictionary. The key will be the '_id' and in each value which is a dictionary there will also be a
    key '_id' so that the structure will be the same as the filesystem collection.

    Parameters
    ----------
    col : Collection
        The mongodb collection.

    Returns
    -------
    dct : dict
        A dictionary with all the info in the collection.
    """
    return {
        doc['_id']: doc for doc in col.find({})
    }


@fallback(ON_PYMONGO_V2, None)
class InsertOneProxy(object):
    def __init__(self, inserted_id, acknowledged):
        self.inserted_id = inserted_id
        self.acknowledged = acknowledged


class MongoClient:
    """A client backed by MongoDB.

    The mongodb server will be automatically opened when the client is initiated.

    Attributes
    ----------
    rc : RunControl
        The RunControl. It may include the 'mongohost' attribute to initiate the client.

    client : MongoClient
        The mongo client. It is initiate from the 'mongohost' attribute if it exists in rc. Otherwise,
        it will be initiated from the 'localhost'.

    proc : Popen
        The Popen of 'mongod --dpath <mongodbpath>'. The 'mongodbpath' is from rc.
    """

    def __init__(self, rc):
        if not MONGO_AVAILABLE:
            raise RuntimeError(
                "MongoDB is not available on the current system."
            )
        self.rc = rc
        self.client = None
        self.proc = None
        self.dbs = defaultdict(lambda: defaultdict(dict))
        self.chained_db = dict()
        self.closed = True
        # actually startup mongo
        self.open()

    def _preclean(self):
        mongodbpath = self.rc.mongodbpath
        if os.path.isdir(mongodbpath):
            shutil.rmtree(mongodbpath)
        os.makedirs(mongodbpath)

    def _startserver(self):
        mongodbpath = self.rc.mongodbpath
        self.proc = subprocess.Popen(
            ["mongod", "--fork", "--syslog", "--dbpath", mongodbpath],
            universal_newlines=True
        )
        print("mongod pid: {0}".format(self.proc.pid), file=sys.stderr)

    def is_alive(self):
        """Returns whether or not the client is alive and availabe to
        send/recieve data.
        """
        if self.client is None:
            return False
        elif ON_PYMONGO_V2:
            return self.client.alive()
        elif ON_PYMONGO_V3:
            alive = False
            if self.rc.local is False:
                from pymongo.errors import ConnectionFailure
                try:
                    # The ismaster command is cheap and does not require auth.
                    self.client.admin.command('ismaster')
                    alive = True
                except ConnectionFailure:
                    print("Server not available")
                    alive = False
            else:
                cmd = ["mongostat", "--host", "localhost", "-n", "1"]
                try:
                    subprocess.check_call(cmd)
                    alive = True
                except subprocess.CalledProcessError:
                    alive = False
            return alive
        else:
            return False

    def open(self):
        """Opens the database client"""
        rc = self.rc
        if hasattr(rc, 'host'):
            host = getattr(rc, 'host')
        else:
            dbs = getattr(rc, 'databases')
            host = dbs[0]['url']
        self.client = pymongo.MongoClient(host)
        if not self.is_alive():
            # we need to wait for the server to startup
            self._preclean()
            self._startserver()
            time.sleep(0.1)
        self.closed = False

    def load_database(self, db: dict):
        """Load the database information from mongo database.

        It populate the 'dbs' attribute with a dictionary like {database: {collection: docs_dict}}.

        Parameters
        ----------
        db : dict
            The dictionary of data base information, such as 'name'.
        """
        dbs: dict = self.dbs
        client: pymongo.MongoClient = self.client
        if db['name'] in client.list_database_names():
            mongodb = client[db['name']]
            for colname in mongodb.list_collection_names():
                col = mongodb[colname]
                dbs[db['name']][colname] = load_mongo_col(col)
        else:
            print('Database name provided in regolithrc.json not found in mongodb')
        return

    def import_database(self, db: dict):
        """Import the database from filesystem to the mongo backend.

        Parameters
        ----------
        db : dict
            The dictionary of data base information, such as 'name'.
        """
        host = getattr(self.rc, 'host', None)
        uri = db.get('dst_url', None)
        dbpath = dbpathname(db, self.rc)
        dbname = db['name']
        import_jsons(dbpath, dbname, host=host, uri=uri)
        import_yamls(dbpath, dbname, host=host, uri=uri)
        return

    def dump_database(self, db):
        """Dumps a database dict via mongoexport."""
        dbpath = dbpathname(db, self.rc)
        os.makedirs(dbpath, exist_ok=True)
        to_add = []
        colls = self.client[db["name"]].collection_names(
            include_system_collections=False
        )
        for collection in colls:
            f = os.path.join(dbpath, collection + ".json")
            cmd = [
                "mongoexport",
                "--db",
                db["name"],
                "--collection",
                collection,
                "--out",
                f,
            ]
            subprocess.check_call(cmd)
            to_add.append(os.path.join(db["path"], collection + ".json"))
        return to_add

    def close(self):
        """Closes the database connection."""
        self.closed = True
        return

    def keys(self):
        return self.client.database_names()

    def __getitem__(self, key):
        return self.client[key]

    def collection_names(self, dbname):
        """Returns the collection names for the database name."""
        return self.client[dbname].collection_names()

    def all_documents(self, collname, copy=True):
        """Returns an iterable over all documents in a collection."""
        if copy:
            return deepcopy(self.chained_db.get(collname, {})).values()
        return self.chained_db.get(collname, {}).values()

    def insert_one(self, dbname, collname, doc):
        """Inserts one document to a database/collection."""
        coll = self.client[dbname][collname]
        doc['_id'].replace('.', '')
        if ON_PYMONGO_V2:
            i = coll.insert(doc)
            return InsertOneProxy(i, True)
        else:
            return coll.insert_one(doc)

    def insert_many(self, dbname, collname, docs):
        """Inserts many documents into a database/collection."""
        coll = self.client[dbname][collname]
        for doc in docs:
            doc['_id'].replace('.', '')
        if ON_PYMONGO_V2:
            return coll.insert(docs)
        else:
            return coll.insert_many(docs)

    def delete_one(self, dbname, collname, doc):
        """Removes a single document from a collection"""
        coll = self.client[dbname][collname]
        doc['_id'].replace('.', '')
        if ON_PYMONGO_V2:
            return coll.remove(doc, multi=False)
        else:
            return coll.delete_one(doc)

    def find_one(self, dbname, collname, filter):
        """Finds the first document matching filter."""
        coll = self.dbs[dbname][collname]
        filter.replace('.', '')
        doc = coll.find_one(filter)
        return doc

    def update_one(self, dbname, collname, filter, update, **kwargs):
        """Updates one document."""
        coll = self.client[dbname][collname]
        filter.replace('.', '')
        if ON_PYMONGO_V2:
            doc = coll.find_one(filter)
            if doc is None:
                if not kwargs.get("upsert", False):
                    raise RuntimeError(
                        "could not update non-existing document"
                    )
                newdoc = dict(filter)
                newdoc.update(update["$set"])
                return self.insert_one(dbname, collname, newdoc)
            return coll.update(doc, update, **kwargs)
        else:
            return coll.find_one_and_update(filter, update, **kwargs)
