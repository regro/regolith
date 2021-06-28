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
# Currently the first two must be named test solely to match the helper map test output text
REGOLITH_MONGODB_NAME = "test"
FS_DB_NAME = 'test'
ALTERNATE_REGOLITH_MONGODB_NAME = "mongo_test"


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
                        "backend": "filesystem"
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


@pytest.fixture(scope="module")
def make_mongodb():
    """A test fixture that creates and destroys a git repo in a temporary
    directory, as well as a mongo database.
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
                        "backend": "mongodb"
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
            },
            f,
        )
    if os.name == 'nt':
        # If on windows, the mongod command cannot be run with the fork or syslog options. Instead, it is installed as
        # a service and the exceptions that would typically be log outputs are handled by the exception handlers below.
        # In addition, the database must always be manually deleted from the windows mongo instance before running a
        # fresh test.
        cmd = ["mongo", REGOLITH_MONGODB_NAME, "--eval", "db.dropDatabase()"]
        try:
            subprocess.check_call(cmd, cwd=repo)
        except subprocess.CalledProcessError:
            print(
                "Mongodb likely has not been installed as a service. In order to run mongodb tests, make sure\n"
                "to install the mongodb community edition with the following link: \n"
                "https://docs.mongodb.com/manual/installation/")
            yield False
            return
        cmd = ["mongostat", "--host", "localhost", "-n", "1"]
    else:
        cmd = ['mongod', '--fork', '--syslog', '--dbpath', mongodbpath]
    try:
        subprocess.check_call(cmd, cwd=repo)
    except subprocess.CalledProcessError:
        print("If using linux or mac, Mongod command failed to execute. If using windows, the status of mongo could \n"
              "not be retrieved. In order to run mongodb tests, make sure to install the mongodb community edition with"
              "\nthe following link:\n"
              "https://docs.mongodb.com/manual/installation/")
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
        db = client[REGOLITH_MONGODB_NAME]
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

@pytest.fixture(scope="module")
def make_mixed_db():
    """A test fixture that creates and destroys a git repo in a temporary
    directory, as well as a mongo database.
    This will yield the path to the repo.

    This specific test fixture points to a repo that mixes mongo and filesystem backends for the assignments and
    abstracts test collections in EXEMPLARS respectively.
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
    fspath = os.path.join(repo, 'db')
    os.mkdir(fspath)
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
                        "backend": "mongodb"
                    },
                    {
                        "name": FS_DB_NAME,
                        "url": repo,
                        "public": True,
                        "path": "db",
                        "local": True,
                        "backend": "filesystem"
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
            },
            f,
        )
    if os.name == 'nt':
        # If on windows, the mongod command cannot be run with the fork or syslog options. Instead, it is installed as
        # a service and the exceptions that would typically be log outputs are handled by the exception handlers below.
        # In addition, the database must always be manually deleted from the windows mongo instance before running a
        # fresh test.
        cmd = ["mongo", REGOLITH_MONGODB_NAME, "--eval", "db.dropDatabase()"]
        try:
            subprocess.check_call(cmd, cwd=repo)
        except subprocess.CalledProcessError:
            print(
                "Mongod likely has not been installed as a service. In order to run mongodb tests, make sure\n"
                "to install the mongodb community edition with the following link: \n"
                "https://docs.mongodb.com/manual/installation/")
            yield False
            return
        cmd = ["mongostat", "--host", "localhost", "-n", "1"]
    else:
        cmd = ['mongod', '--fork', '--syslog', '--dbpath', mongodbpath]
    try:
        subprocess.check_call(cmd, cwd=repo)
    except subprocess.CalledProcessError:
        print("If on linux/mac, Mongod command failed to execute. If on windows, the status of mongo could not be\n"
              "retrieved. In order to run mongodb tests, make sure to install the mongodb community edition with\n"
              "the following link:\n"
              "https://docs.mongodb.com/manual/installation/")
        yield False
        return
    # Write one collection doc in mongo
    mongo_coll = 'assignments'
    mongo_example = deepcopy(EXEMPLARS[mongo_coll])
    try:
        client = MongoClient('localhost', serverSelectionTimeoutMS=2000)
        client.server_info()
    except Exception as e:
        yield False
        return
    db = client[REGOLITH_MONGODB_NAME]
    col = db[mongo_coll]
    try:
        mongo_example['_id'].replace('.', '')
        col.insert_one(mongo_example)
    except mongo_errors.DuplicateKeyError:
        print('Duplicate key error, check exemplars for duplicates if tests fail')
    except mongo_errors.BulkWriteError:
        print('Duplicate key error, check exemplars for duplicates if tests fail')
    # Write one collection doc in file system
    fs_coll = 'abstracts'
    fs_example = deepcopy(EXEMPLARS[fs_coll])
    d = {fs_example["_id"]: fs_example}
    os.chdir(repo)
    dump_yaml("db/{}.yaml".format(fs_coll), d)
    yield repo, fs_coll, mongo_coll
    cmd = ["mongo", REGOLITH_MONGODB_NAME, "--eval", "db.dropDatabase()"]
    try:
        subprocess.check_call(cmd, cwd=repo)
    except subprocess.CalledProcessError:
        print(f'Deleting the test database failed, insert \"mongo {REGOLITH_MONGODB_NAME} --eval '
              f'\"db.dropDatabase()\"\" into command line manually')
    os.chdir(cwd)
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


@pytest.fixture(scope="module")
def make_fs_to_mongo_migration_db():
    """A test fixture that creates and destroys a git repo in a temporary
    directory, as well as a mongo database.
    This will yield the path to the repo.

    This specific test fixture points to a repo that mixes mongo and filesystem backends for the assignments and
    abstracts test collections in EXEMPLARS respectively.
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
    fspath = os.path.join(repo, 'db')
    os.mkdir(fspath)
    with open("regolithrc.json", "w") as f:
        json.dump(
            {
                "groupname": "ERGS",
                "databases": [
                    {
                        "name": ALTERNATE_REGOLITH_MONGODB_NAME,
                        "dst_url": 'localhost',
                        "url": repo,
                        "path": "db",
                        "public": True,
                        "local": True,
                        "backend": "mongodb"
                    }
                ],
                "mongodbpath": mongodbpath,
            },
            f,
        )
    if os.name == 'nt':
        # If on windows, the mongod command cannot be run with the fork or syslog options. Instead, it is installed as
        # a service and the exceptions that would typically be log outputs are handled by the exception handlers below.
        # In addition, the database must always be manually deleted from the windows mongo instance before running a
        # fresh test.
        cmd = ["mongo", ALTERNATE_REGOLITH_MONGODB_NAME, "--eval", "db.dropDatabase()"]
        try:
            subprocess.check_call(cmd, cwd=repo)
        except subprocess.CalledProcessError:
            print(
                "Mongod likely has not been installed as a service. In order to run mongodb tests, make sure\n"
                "to install the mongodb community edition with the following link: \n"
                "https://docs.mongodb.com/manual/installation/")
            yield False
            return
        cmd = ["mongostat", "--host", "localhost", "-n", "1"]
    else:
        cmd = ['mongod', '--fork', '--syslog', '--dbpath', mongodbpath]
    try:
        subprocess.check_call(cmd, cwd=repo)
    except subprocess.CalledProcessError:
        print("If on linux/mac, Mongod command failed to execute. If on windows, the status of mongo could not be\n"
              "retrieved. In order to run mongodb tests, make sure to install the mongodb community edition with\n"
              "the following link:\n"
              "https://docs.mongodb.com/manual/installation/")
        yield False
        return
    # Write collection docs
    os.chdir(fspath)
    for coll, example in deepcopy(EXEMPLARS).items():
        if isinstance(example, list):
            d = {dd["_id"]: dd for dd in example}
        else:
            d = {example["_id"]: example}
        dump_yaml("{}.yaml".format(coll), d)
    os.chdir(repo)
    yield repo
    cmd = ["mongo", ALTERNATE_REGOLITH_MONGODB_NAME, "--eval", "db.dropDatabase()"]
    try:
        subprocess.check_call(cmd, cwd=repo)
    except subprocess.CalledProcessError:
        print(f'Deleting the test database failed, insert \"mongo {ALTERNATE_REGOLITH_MONGODB_NAME} --eval '
              f'\"db.dropDatabase()\"\" into command line manually')
    os.chdir(cwd)
    if not OUTPUT_FAKE_DB:
        rmtree(repo)
