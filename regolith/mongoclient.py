"""Client interface for MongoDB."""
import os
import sys
import time
import shutil
import subprocess
from glob import iglob

#
# setup mongo
#
try:
    import pymongo
    from pymongo.errors import AutoReconnect, ConnectionFailure
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False

from regolith.tools import dbdirname, dbpathname


if not MONGO_AVAILABLE:
    ON_PYMONGO_V2 = ON_PYMONGO_V3 = False
elif pymongo.version.split('.')[0] == '2':
    ON_PYMONGO_V2 = True
    ON_PYMONGO_V3 = False
else:
    ON_PYMONGO_V2 = False
    ON_PYMONGO_V3 = True



class MongoClient:
    """A client backed by MongoDB."""

    def __init__(self, rc):
        if not MONGO_AVAILABLE:
            raise RuntimeError("MongoDB is not available on the current system.")
        self.rc = rc
        self.client = self.proc = None
        # actually startup mongo
        self._preclean()
        self._startserver()
        self.open()

    def _preclean(self):
        mongodbpath = self.rc.mongodbpath
        if os.path.isdir(mongodbpath):
            shutil.rmtree(mongodbpath)
        os.makedirs(mongodbpath)

    def _startserver(self):
        self.proc = subprocess.Popen(['mongod', '--dbpath', mongodbpath],
                                      universal_newlines=True)
        print('mongod pid: {0}'.format(self.proc.pid), file=sys.stderr)

    def is_alive(self):
        """Returns whether or not the client is alive and availabe to
        send/recieve data.
        """
        if self.client is None:
            return False
        elif ON_PYMONGO_V2:
            return self.client.alive()
        elif ON_PYMONGO_V3:
            cmd = ['mongostat', '--host', 'localhost', '-n', '1']
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
        while self.client is None:
            try:
                self.client = pymongo.MongoClient()
            except (AutoReconnect, ConnectionFailure):
                time.sleep(0.1)
        while not self.is_alive():
            # we need to wait for the server to startup
            time.sleep(0.1)

    def load_database(self, db):
        """Loads a database via mongoimport.  Takes a database dict db."""
        dbpath = dbpathname(db, self.rc)
        for f in iglob(os.path.join(dbpath, '*.json')):
            base, ext = os.path.splitext(os.path.split(f)[-1])
            cmd = ['mongoimport', '--db',  db['name'], '--collection', base,
                   '--file', f]
            subprocess.check_call(cmd)

    def dump_database(self, db):
        """Dumps a database dict via mongoexport."""
        dbpath = dbpathname(db, self.rc)
        os.makedirs(dbpath, exist_ok=True)
        to_add = []
        colls = self.client[db['name']].collection_names(
                                            include_system_collections=False)
        for collection in colls:
            f = os.path.join(dbpath, collection + '.json')
            cmd = ['mongoexport', '--db',  db['name'],
                   '--collection', collection, '--out', f]
            subprocess.check_call(cmd)
            to_add.append(os.path.join(db['path'], collection + '.json'))

    def close(self):
        """Closes the database connection."""
        if not self.is_alive():
            pass
        elif ON_PYMONGO_V2:
            self.client.disconnect()
        elif ON_PYMONGO_V3:
            self.client.close()
        else:
            raise RuntimeError('did not recognize pymongo version')
        self.proc.terminate()
        mongodbpath = self.rc.mongodbpath
        if os.path.isdir(mongodbpath):
            shutil.rmtree(mongodbpath, ignore_errors=True)
