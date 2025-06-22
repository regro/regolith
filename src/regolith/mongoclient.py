"""Client interface for MongoDB.

Maintained such that only pymongo is necessary when using
helper/builders, and additional command-line tools are necessary to
install for maintenance tasks, such as fs-to-mongo.
"""

import datetime
import itertools
import os
import shutil
import subprocess
import sys
import time
import urllib
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

from ruamel.yaml import YAML

from regolith.tools import validate_doc

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

from regolith import fsclient
from regolith.tools import dbpathname, fallback

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
            cmd += ["--host", host, "--db", dbname]
        if uri is not None:
            cmd += ["--uri", uri]
        cmd += ["--collection", json_path.stem, "--file", str(json_path)]
        try:
            subprocess.check_call(cmd, stderr=subprocess.STDOUT)
        except FileNotFoundError:
            print(
                "mongoimport command not found in environment path.\n\n"
                "If mongo server v4.4+ installed, download MongoDB Database Tools from:"
                " https://www.mongodb.com/try/download/database-tools\n"
                "and add C:\\Program Files\\MongoDB\\Tools\\<ToolsVersion>\\bin\\ to path.\n\n"
                "If mongo server <v4.4, ensure that C:\\Program Files\\MongoDB\\Server\\<ServerVersion>\\bin\\ \n"
                "has been added to the environment path.\n"
            )
            print("..................Upload failed..................")
        except subprocess.CalledProcessError as exc:
            print("Status : FAIL", exc.returncode, exc.output)
            raise exc
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
    yaml_files = itertools.chain(Path(dbpath).glob("*.yaml"), Path(dbpath).glob("*.yml"))
    with TemporaryDirectory() as tempd:
        for yaml_file in yaml_files:
            json_file = Path(tempd).joinpath(yaml_file.with_suffix(".json").name)
            loader = YAML(typ="safe")
            loader.constructor.yaml_constructors["tag:yaml.org,2002:timestamp"] = (
                loader.constructor.yaml_constructors["tag:yaml.org,2002:str"]
            )
            fsclient.yaml_to_json(str(yaml_file), str(json_file), loader=loader)
        import_jsons(tempd, dbname, host=host, uri=uri)
    return


def export_json(collection: str, dbpath: str, dbname: str, host: str = None, uri: str = None) -> None:
    cmd = ["mongoexport", "--collection", collection]
    if host is not None:
        cmd += ["--host", host, "--db", dbname]
    if uri is not None:
        cmd += ["--uri", uri]
    cmd += ["--out", str(os.path.join(dbpath, collection + ".json"))]
    try:
        subprocess.check_call(cmd, stderr=subprocess.STDOUT)
    except FileNotFoundError:
        print(
            "mongoexport command not found in environment path.\n\n"
            "If mongo server v4.4+ installed, download MongoDB Database Tools from:"
            " https://www.mongodb.com/try/download/database-tools\n"
            "and add C:\\Program Files\\MongoDB\\Tools\\<ToolsVersion>\\bin\\ to path.\n\n"
            "If mongo server <v4.4, ensure that C:\\Program Files\\MongoDB\\Server\\<ServerVersion>\\bin\\ \n"
            "has been added to the environment path.\n"
        )
        print("..................Upload failed..................")
    except subprocess.CalledProcessError as exc:
        print("Status : FAIL", exc.returncode, exc.output)
        raise exc


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
    return {doc["_id"]: doc for doc in col.find({})}


def doc_cleanup(doc: dict):
    doc = bson_cleanup(doc)
    doc["_id"].replace(".", "")
    return doc


def bson_cleanup(doc: dict):
    """This method should be used prior to updating or adding a document
    to a collection in mongo. Specifically, this replaces all periods in
    keys and _id value with a blank, and changes datetime.date to an iso
    string. It does so recursively for nested dictionaries.

    Parameters
    ----------
    doc

    Returns
    -------
    doc
    """

    def change_keys_id_and_date(obj, convert):
        """Recursively goes through the dictionary obj and replaces keys
        with the convert function."""
        if isinstance(obj, datetime.date):
            # Mongo cannot handle datetime.date format,
            # but we have infrastructure to handle iso date strings present
            # Do not convert to datetime.datetime. Mongo can handle this, but regolith cannot.
            return obj.isoformat()
        if isinstance(obj, (str, int, float)):
            return obj
        if isinstance(obj, dict):
            new = obj.__class__()
            for k, v in obj.items():
                new[convert(k)] = change_keys_id_and_date(v, convert)
        elif isinstance(obj, (list, set, tuple)):
            new = obj.__class__(change_keys_id_and_date(v, convert) for v in obj)
        else:
            return obj
        return new

    def convert(k):
        return k.replace(".", "-")

    doc = change_keys_id_and_date(doc, convert)
    return doc


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
            raise RuntimeError("MongoDB is not available on the current system.")
        self.rc = rc
        self.client = None
        self.proc = None
        self.dbs = defaultdict(lambda: defaultdict(dict))
        self.chained_db = dict()
        self.closed = True
        self.local = True

    def _preclean(self):
        mongodbpath = self.rc.mongodbpath
        if os.path.isdir(mongodbpath):
            shutil.rmtree(mongodbpath)
        os.makedirs(mongodbpath)

    def _startserver(self):
        mongodbpath = self.rc.mongodbpath
        self.proc = subprocess.Popen(
            ["mongod", "--fork", "--syslog", "--dbpath", mongodbpath], universal_newlines=True
        )
        print("mongod pid: {0}".format(self.proc.pid), file=sys.stderr)

    def is_alive(self):
        """Returns whether or not the client is alive and available to
        send/receive data."""
        if self.client is None:
            return False
        elif ON_PYMONGO_V2:
            return self.client.alive()
        elif ON_PYMONGO_V3:
            alive = False
            if self.local is False:
                from pymongo.errors import ConnectionFailure

                try:
                    # The ismaster command is cheap and does not require auth.
                    self.client.admin.command("ismaster")
                    alive = True
                except ConnectionFailure:
                    print("Server not available")
                    alive = False
            else:
                cmd = ["mongostat", "--host", "localhost", "-n", "1"]
                try:
                    subprocess.check_call(cmd, stderr=subprocess.STDOUT)
                    alive = True
                except subprocess.CalledProcessError as exc:
                    print("Status : FAIL", exc.returncode, exc.output)
                    alive = False
            return alive
        else:
            return False

    def open(self):
        """Opens the database client."""
        if self.closed:
            rc = self.rc
            mongo_dbs_filter = filter(
                lambda db: db["backend"] == "mongo" or db["backend"] == "mongodb", rc.databases
            )
            mongo_dbs_list = list(mongo_dbs_filter)
            host = None
            if hasattr(rc, "host"):
                host = rc.host
            else:
                for db in mongo_dbs_list:
                    if host is not None:
                        if host != db["url"]:
                            print("WARNING: Multiple mongo clusters not supported. Use single cluster per rc.")
                            return
                    host = db["url"]
            if host is not None:
                if "+srv" in host:
                    self.local = False
            elif "dst_url" in rc.databases[0]:
                if "+srv" in rc.databases[0]["dst_url"]:
                    self.local = False
            # Currently configured such that password deemed unnecessary for strictly local mongo instance
            password_req = not self.local
            if password_req:
                try:
                    password = rc.mongo_db_password
                    if host is not None:
                        host = host.replace("pwd_from_config", urllib.parse.quote_plus(password))
                        host = host.replace("uname_from_config", urllib.parse.quote_plus(rc.mongo_id))
                    elif "dst_url" in rc.databases[0]:
                        rc.databases[0]["dst_url"] = rc.databases[0]["dst_url"].replace(
                            "pwd_from_config", urllib.parse.quote_plus(password)
                        )
                        rc.databases[0]["dst_url"] = rc.databases[0]["dst_url"].replace(
                            "uname_from_config", urllib.parse.quote_plus(rc.mongo_id)
                        )
                        host = rc.databases[0]["dst_url"]
                except AttributeError:
                    print(
                        "ERROR:\n"
                        "Add a username and password to user.json in "
                        "user/.config/regolith/user.json with the keys\n"
                        "mongo_id and mongo_db_password respectively.\n\n"
                        "'uname_from_config' and 'pwd_from_config' can/should stand in for these field in the\n"
                        "mongo URL string in regolithrc.json.\n"
                    )
            self.client = pymongo.MongoClient(host, authSource="admin")
            if not self.is_alive():
                if self.local:
                    # we need to wait for the server to startup
                    self._preclean()
                    self._startserver()
                    time.sleep(0.1)
                else:
                    raise ConnectionError(
                        "Mongo server exists, communication refused. Potential TLS issue.\n"
                        "Attempt the following in regolith env bash terminal:\n"
                        'export SSL_CERT_FILE=$(python -c "import certifi; print(certifi.where())")'
                    )
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
        from pymongo.errors import OperationFailure

        try:
            mongodb = client[db["name"]]
        except OperationFailure:
            print("WARNING: Database name provided in regolithrc.json not found in mongodb")
        try:
            for colname in [
                coll
                for coll in mongodb.list_collection_names()
                if coll not in db["blacklist"] and len(db["whitelist"]) == 0 or coll in db["whitelist"]
            ]:
                col = mongodb[colname]
                dbs[db["name"]][colname] = load_mongo_col(col)
        except OperationFailure as fail:
            print("Mongo's Error Message:" + str(fail) + "\n")
            print("The user does not have permission to access " + db["name"] + "\n\n")
            print(
                "If erroneous, the role/mongo-account utilized likely is only read/write. List collection \n"
                "permission as well as finding is needed"
            )
        return

    def import_database(self, db: dict):
        """Import the database from filesystem to the mongo backend.

        Parameters
        ----------
        db : dict
            The dictionary of data base information, such as 'name'.
        """
        host = getattr(self.rc, "host", None)
        uri = db.get("dst_url", None)
        # Catch the easy/common regolith rc error of putting the db uri as localhost rather than host
        if uri == "localhost":
            uri = None
            host = "localhost"
        dbpath = dbpathname(db, self.rc)
        dbname = db["name"]
        import_jsons(dbpath, dbname, host=host, uri=uri)
        import_yamls(dbpath, dbname, host=host, uri=uri)
        return

    def export_database(self, db: dict):
        """Exports the database from mongo backend to the filesystem.

        Parameters
        ----------
        db : dict
            The dictionary of data base information, such as 'name'.
        """
        host = getattr(self.rc, "host", None)
        uri = db.get("dst_url", None)
        # Catch the easy/common regolith rc error of putting the db uri as localhost rather than host
        if uri == "localhost":
            uri = None
            host = "localhost"
        dbpath = os.path.abspath(dbpathname(db, self.rc))
        dbname = db["name"]
        for collection in self.dbs[dbname].keys():
            export_json(collection, dbpath, dbname, host=host, uri=uri)
        return

    def dump_database(self, db):
        """Dumps a database dict via mongoexport."""
        dbpath = dbpathname(db, self.rc)
        os.makedirs(dbpath, exist_ok=True)
        to_add = []
        colls = self.client[db["name"]].collection_names(include_system_collections=False)
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
            try:
                subprocess.check_call(cmd, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as exc:
                print("Status : FAIL", exc.returncode, exc.output)
                raise exc
            to_add.append(os.path.join(db["path"], collection + ".json"))
        return to_add

    def close(self):
        """Closes the database connection."""
        self.closed = True
        return

    def keys(self):
        return self.client.list_database_names()

    def __getitem__(self, key):
        return self.client[key]

    def collection_names(self, dbname, include_system_collections=True):
        """Returns the collection names for the database name."""
        return self.client[dbname].collection_names()

    def all_documents(self, collname, copy=True):
        """Returns an iterable over all documents in a collection."""
        if copy:
            return deepcopy(self.chained_db.get(collname, {})).values()
        return self.chained_db.get(collname, {}).values()

    def insert_one(self, dbname, collname, doc):
        """Inserts one document to a database/collection."""
        doc = doc_cleanup(doc)
        valid, potential_error = validate_doc(collname, doc, self.rc)
        if not valid:
            raise ValueError(potential_error)
        coll = self.client[dbname][collname]
        if ON_PYMONGO_V2:
            i = coll.insert(doc)
            return InsertOneProxy(i, True)
        else:
            return coll.insert_one(doc)

    def insert_many(self, dbname, collname, docs):
        """Inserts many documents into a database/collection."""
        docs = [doc_cleanup(doc) for doc in docs]

        screened_docs = []
        full_error = ""
        for doc in docs:
            valid, potential_error = validate_doc(collname, doc, self.rc)
            if not valid:
                screened_docs.append(doc)
                full_error += potential_error
                full_error += "\n"
        if len(screened_docs) != 0:
            print("The following documents failed validation and were not uploaded\n")
            for doc in screened_docs:
                print(full_error)
                if doc in docs:
                    docs.remove(doc)
        coll = self.client[dbname][collname]
        if ON_PYMONGO_V2:
            return coll.insert(docs)
        else:
            return coll.insert_many(docs)

    def delete_one(self, dbname, collname, doc):
        """Removes a single document from a collection."""
        coll = self.client[dbname][collname]
        doc = doc_cleanup(doc)
        if ON_PYMONGO_V2:
            return coll.remove(doc, multi=False)
        else:
            return coll.delete_one(doc)

    def find_one(self, dbname, collname, filter):
        """Finds the first document matching filter."""
        filter["_id"].replace(".", "")
        coll = self.client[dbname][collname]
        doc = coll.find_one(filter)
        return doc

    def update_one(self, dbname, collname, filter, update, **kwargs):
        """Updates one document."""
        filter["_id"].replace(".", "")
        doc = self.find_one(dbname, collname, filter)
        newdoc = dict(filter if doc is None else doc)
        newdoc.update(update)
        valid, potential_error = validate_doc(collname, newdoc, self.rc)
        if not valid:
            raise ValueError(potential_error)
        coll = self.client[dbname][collname]
        update = bson_cleanup(update)
        if ON_PYMONGO_V2:
            doc = coll.find_one(filter)
            if doc is None:
                if not kwargs.get("upsert", False):
                    raise RuntimeError("could not update non-existing document")
                newdoc = dict(filter)
                newdoc.update(update["$set"])
                return self.insert_one(dbname, collname, newdoc)
            return coll.update(doc, update, **kwargs)
        else:
            return coll.find_one_and_update(filter, {"$set": update}, **kwargs)
