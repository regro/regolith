"""Copyright (c) 2017, Anthony Scopatz
All rights reserved."""
import json
import os
import tempfile
from copy import deepcopy

import pytest
from pymongo import MongoClient
from xonsh.lib import subprocess
from xonsh.lib.os import rmtree

from regolith.fsclient import dump_yaml
from regolith.schemas import EXEMPLARS

OUTPUT_FAKE_DB = False  # always turn it to false after you used it


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
                        "name": "test",
                        "url": 'localhost',
                        "path": repo,
                        "public": True,
                        "local": False,
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
    subprocess.run(['mongod', '--fork', '--syslog', '--dbpath', mongodbpath])
    # Write collection docs
    for col_name, example in deepcopy(EXEMPLARS).items():
        client = MongoClient('localhost', serverSelectionTimeoutMS=2000)
        db = client['test']
        col = db[col_name]
        if isinstance(example, list):
            for doc in example:
                doc['_id'].replace('.', '')
            col.insert_many(example)
        else:
            example['_id'].replace('.', '')
            col.insert_one(example)
    yield repo
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
