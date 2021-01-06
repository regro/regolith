"""Copyright (c) 2017, Anthony Scopatz
All rights reserved."""
import json
import os
import tempfile
from copy import deepcopy

import pytest
from pymongo import MongoClient
from pymongo import errors as mongo_errors
from xonsh.lib import subprocess
from xonsh.lib.os import rmtree

from regolith.fsclient import dump_yaml
from regolith.schemas import EXEMPLARS

OUTPUT_FAKE_DB = False  # always turn it to false after you used it
REGOLITH_MONGODB_NAME = "test"


@pytest.fixture(scope="session")
def make_db():
    """A test fixutre that creates and destroys a git repo in a temporary
    directory.
    This will yield the path to the repo.
    """
    cwd = os.getcwd()
    name = "regolith_fake"
    repo = os.path.join(tempfile.gettempdir(), name)
    if os.path.exists(repo):
        rmtree(repo)
    subprocess.run(["git", "init", repo])
    os.chdir(repo)
    with open("README", "w") as f:
        f.write("testing " + name)
    with open("regolithrc.json", "w") as f:
        json.dump(
            {
                "groupname": "ERGS",
                "databases": [
                    {
                        "name": "test",
                        "url": repo,
                        "public": True,
                        "path": "db",
                        "local": True,
                    }
                ],
                "stores": [
                    {
                        "name": "store",
                        "url": repo,
                        "path": repo,
                        "public": True,
                    }
                ],
                "backend": "filesystem"
            },
            f,
        )
    os.mkdir("db")
    # Write collection docs
    for coll, example in deepcopy(EXEMPLARS).items():
        if isinstance(example, list):
            d = {dd["_id"]: dd for dd in example}
        else:
            d = {example["_id"]: example}
        dump_yaml("db/{}.yaml".format(coll), d)
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-am", "Initial readme"])
    yield repo
    os.chdir(cwd)
    if not OUTPUT_FAKE_DB:
        rmtree(repo)


@pytest.fixture(scope="session")
def make_mongodb():
    """A test fixutre that creates and destroys a git repo in a temporary
    directory.
    This will yield the path to the repo.
    """
    cwd = os.getcwd()
    name = "regolith_mongo_fake"
    repo = os.path.join(tempfile.gettempdir(), name)
    if os.path.exists(repo):
        rmtree(repo)
    subprocess.run(["git", "init", repo])
    os.chdir(repo)
    with open("README", "w") as f:
        f.write("testing " + name)
    mongodbpath = os.path.join(repo, 'dbs')
    os.mkdir(mongodbpath)
    with open("regolithrc.json", "w") as f:
        json.dump(
            {
                "groupname": "ERGS",
                "databases": [
                    {
                        "name": REGOLITH_MONGODB_NAME,
                        "url": 'localhost',
                        "path": repo,
                        "public": True,
                        "local": True,
                    }
                ],
                "stores": [
                    {
                        "name": "store",
                        "url": repo,
                        "path": repo,
                        "public": True,
                    }
                ],
                "mongodbpath": mongodbpath,
                "backend": "mongodb"
            },
            f,
        )
    if os.name == 'nt':
        # If on windows, the mongod command cannot be run with the fork or syslog options. Instead, it is installed as
        # a service and the exceptions that would typically be log outputs are handled by the exception handlers below.
        # In addition, the database must always be manually deleted from the windows mongo instance before running a
        # fresh test.
        #cmd = ["mongod", "--dbpath", mongodbpath]
        cmd = ["mongo", REGOLITH_MONGODB_NAME, "--eval", "db.dropDatabase()"]
        try:
            subprocess.check_call(cmd, cwd=repo)
        except subprocess.CalledProcessError:
            print(
                "If on linux or mac, Mongod command failed to execute. If on windows, mongod has not been installed as \n"
                "a service. In order to run mongodb tests, make sure to install the mongodb community edition\n"
                "for your OS with the following link: https://docs.mongodb.com/manual/installation/")
            yield False
            return
        cmd = ["mongostat", "--host", "localhost", "-n", "1"]
    else:
        cmd = ['mongod', '--fork', '--syslog', '--dbpath', mongodbpath]
    try:
        subprocess.check_call(cmd, cwd=repo)
    except subprocess.CalledProcessError:
        print("If on linux or mac, Mongod command failed to execute. If on windows, mongod has not been installed as \n"
              "a service. In order to run mongodb tests, make sure to install the mongodb community edition\n"
              "for your OS with the following link: https://docs.mongodb.com/manual/installation/")
        yield False
        return
    # Write collection docs
    for col_name, example in deepcopy(EXEMPLARS).items():
        try:
            client = MongoClient('localhost', serverSelectionTimeoutMS=2000)
            client.server_info()
        except Exception as e:
            yield False
            return
        db = client['test']
        col = db[col_name]
        try:
            if isinstance(example, list):
                for doc in example:
                    doc['_id'].replace('.', '')
                col.insert_many(example)
            else:
                example['_id'].replace('.', '')
                col.insert_one(example)
        except mongo_errors.DuplicateKeyError:
            print('Duplicate key error, check exemplars for duplicates if tests fail')
        except mongo_errors.BulkWriteError:
            print('Duplicate key error, check exemplars for duplicates if tests fail')
    yield repo
    cmd = ["mongo", REGOLITH_MONGODB_NAME, "--eval", "db.dropDatabase()"]
    try:
        subprocess.check_call(cmd, cwd=repo)
    except subprocess.CalledProcessError:
        print(f'Deleting the test database failed, insert \"mongo {REGOLITH_MONGODB_NAME} --eval '
              f'\"db.dropDatabase()\"\" into command line manually')
    if not OUTPUT_FAKE_DB:
        rmtree(repo)


@pytest.fixture(scope="session")
def make_bad_db():
    """A test fixutre that creates and destroys a git repo in a temporary
    directory.
    This will yield the path to the repo.
    """
    cwd = os.getcwd()
    name = "regolith_fake_bad"
    repo = os.path.join(tempfile.gettempdir(), name)
    if os.path.exists(repo):
        rmtree(repo)
    subprocess.run(["git", "init", repo])
    os.chdir(repo)
    with open("README", "w") as f:
        f.write("testing " + name)
    with open("regolithrc.json", "w") as f:
        json.dump(
            {
                "groupname": "ERGS",
                "databases": [
                    {
                        "name": "test",
                        "url": repo,
                        "public": True,
                        "path": "db",
                        "local": True,
                    }
                ],
            },
            f,
        )
    os.mkdir("db")
    # Write collection docs
    for coll, example in deepcopy(EXEMPLARS).items():
        if isinstance(example, list):
            d = {dd["_id"]: dd for dd in example}
        else:
            d = {example["_id"]: example}
        d.update({"bad": {"_id": "bad", "bad": True}})
        if coll == "presentations":
            d.update(
                {
                    "bad_inst": {
                        "_id": "bad_inst",
                        "institution": "noinstitution",
                        "department": "nodept",
                    }
                }
            )
        dump_yaml("db/{}.yaml".format(coll), d)
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-am", "Initial readme"])
    yield repo
    os.chdir(cwd)
    rmtree(repo)
