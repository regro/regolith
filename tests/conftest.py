"""Copyright (c) 2017, Anthony Scopatz All rights reserved."""

import json
import os
import tempfile
from copy import deepcopy
from pathlib import Path
from subprocess import CalledProcessError

import pytest
from pymongo import MongoClient
from pymongo import errors as mongo_errors
from xonsh.api import subprocess
from xonsh.api.os import rmtree

from regolith.fsclient import dump_yaml
from regolith.schemas import EXEMPLARS

OUTPUT_FAKE_DB = False  # always turn it to false after you used it
# Currently the first two must be named test solely to match the helper map test output text
REGOLITH_MONGODB_NAME = "test"
FS_DB_NAME = "test"
ALTERNATE_REGOLITH_MONGODB_NAME = "mongo_test"


# copied over from cookiecutter conftest.py
@pytest.fixture
def user_filesystem(tmp_path):
    base_dir = Path(tmp_path)
    home_dir = base_dir / "home_dir"
    home_dir.mkdir(parents=True, exist_ok=True)
    cwd_dir = base_dir / "cwd_dir"
    cwd_dir.mkdir(parents=True, exist_ok=True)

    home_config_data = {"username": "home_username", "email": "home@email.com"}
    with open(home_dir / "diffpyconfig.json", "w") as f:
        json.dump(home_config_data, f)

    yield tmp_path


@pytest.fixture(scope="session")
def make_db():
    """A test fixutre that creates and destroys a git repo in a
    temporary directory.

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
                "default_user_id": "sbillinge",
                "groupname": "ERGS",
                "databases": [
                    {
                        "name": "test",
                        "url": repo,
                        "public": True,
                        "path": "db",
                        "local": True,
                        "backend": "filesystem",
                    }
                ],
                "repos": [
                    {
                        "_id": "talk_repo",
                        "params": {"namespace_id": "35", "initialize_with_readme": "true", "name": "repo name"},
                        "url": "https://example.com",
                        "api_route": "/url/example",
                        "namespace_name": "talks",
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
                "tokens": [{"_id": "gitlab_private_token", "token": "<private_token>"}],
            },
            f,
        )
    fspath = os.path.join(repo, "db")
    os.mkdir(fspath)
    exemplars_to_fs(fspath)
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-am", "Initial readme"])
    yield repo
    os.chdir(cwd)
    if not OUTPUT_FAKE_DB:
        rmtree(repo)


@pytest.fixture(scope="module")
def make_mongodb():
    """A test fixture that creates and destroys a git repo in a
    temporary directory, as well as a mongo database.

    This will yield the path to the repo.
    """
    forked = False
    name = "regolith_mongo_fake"
    repo = os.path.join(tempfile.gettempdir(), name)
    if os.path.exists(repo):
        rmtree(repo)
    subprocess.run(["git", "init", repo])
    os.chdir(repo)
    with open("README", "w") as f:
        f.write("testing " + name)
    mongodbpath = os.path.join(repo, "dbs")
    os.mkdir(mongodbpath)
    with open("regolithrc.json", "w") as f:
        json.dump(
            {
                "groupname": "ERGS",
                "databases": [
                    {
                        "name": REGOLITH_MONGODB_NAME,
                        "url": "localhost",
                        "path": repo,
                        "public": True,
                        "local": True,
                        "backend": "mongodb",
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
    if os.name == "nt":
        # If on windows, the mongod command cannot be run with the fork or syslog options.
        # Instead, it is installed as a service and the exceptions that would typically be log outputs
        # are handled by the exception handlers below. In addition, the database must always be manually
        # deleted from the windows mongo instance before running a fresh test.
        cmd = ["mongo", REGOLITH_MONGODB_NAME, "--eval", "db.dropDatabase()"]
        try:
            subprocess.check_call(cmd, cwd=repo)
        except CalledProcessError:
            print(
                "Mongodb likely has not been installed as a service. In order to run mongodb tests, make sure\n"
                "to install the mongodb community edition with the following link: \n"
                "https://docs.mongodb.com/manual/installation/"
            )
            yield False
            return
        cmd = ["mongostat", "--host", "localhost", "-n", "1"]
    else:
        cmd = ["mongod", "--fork", "--syslog", "--dbpath", mongodbpath]
        forked = True
    try:
        subprocess.check_call(cmd, cwd=repo)
    except CalledProcessError:
        print(
            "If using linux or mac, Mongod command failed to execute. "
            "If using windows, the status of mongo could \n not be retrieved. "
            "In order to run mongodb tests, make sure to install the mongodb community edition with "
            "\nthe following link:\n"
            "https://docs.mongodb.com/manual/installation/"
        )
        yield False
        return
    try:
        exemplars_to_mongo(REGOLITH_MONGODB_NAME)
    except ConnectionError:
        yield False
        return
    yield repo
    cmd = ["mongo", REGOLITH_MONGODB_NAME, "--eval", "db.dropDatabase()"]
    try:
        subprocess.check_call(cmd, cwd=repo)
    except CalledProcessError:
        print(
            f'Deleting the test database failed, insert "mongo {REGOLITH_MONGODB_NAME} --eval '
            f'"db.dropDatabase()"" into command line manually'
        )
    shut_down_fork(forked, repo)
    if not OUTPUT_FAKE_DB:
        rmtree(repo)


@pytest.fixture(scope="module")
def make_mixed_db():
    """A test fixture that creates and destroys a git repo in a
    temporary directory, as well as a mongo database. This will yield
    the path to the repo.

    This specific test fixture points to a repo that mixes mongo and
    filesystem backends for the assignments and abstracts test
    collections in EXEMPLARS respectively.
    """
    cwd = os.getcwd()
    forked = False
    name = "regolith_mongo_fake"
    repo = os.path.join(tempfile.gettempdir(), name)
    if os.path.exists(repo):
        rmtree(repo)
    subprocess.run(["git", "init", repo])
    os.chdir(repo)
    with open("README", "w") as f:
        f.write("testing " + name)
    mongodbpath = os.path.join(repo, "dbs")
    os.mkdir(mongodbpath)
    fspath = os.path.join(repo, "db")
    os.mkdir(fspath)
    with open("regolithrc.json", "w") as f:
        json.dump(
            {
                "groupname": "ERGS",
                "databases": [
                    {
                        "name": REGOLITH_MONGODB_NAME,
                        "url": "localhost",
                        "path": repo,
                        "public": True,
                        "local": True,
                        "backend": "mongodb",
                    },
                    {
                        "name": FS_DB_NAME,
                        "url": repo,
                        "public": True,
                        "path": "db",
                        "local": True,
                        "backend": "filesystem",
                    },
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
    if os.name == "nt":
        # If on windows, the mongod command cannot be run with the fork or syslog options.
        # Instead, it is installed as a service and the exceptions that would typically be log outputs
        # are handled by the exception handlers below. In addition, the database must always be manually
        # deleted from the windows mongo instance before running a fresh test.
        cmd = ["mongo", REGOLITH_MONGODB_NAME, "--eval", "db.dropDatabase()"]
        try:
            subprocess.check_call(cmd, cwd=repo)
        except CalledProcessError:
            print(
                "Mongod likely has not been installed as a service. In order to run mongodb tests, make sure\n"
                "to install the mongodb community edition with the following link: \n"
                "https://docs.mongodb.com/manual/installation/"
            )
            yield False
            return
        cmd = ["mongostat", "--host", "localhost", "-n", "1"]
    else:
        cmd = ["mongod", "--fork", "--syslog", "--dbpath", mongodbpath]
        forked = True
    try:
        subprocess.check_call(cmd, cwd=repo)
    except CalledProcessError:
        print(
            "If on linux/mac, Mongod command failed to execute. If on windows, the status of mongo could not be\n"
            "retrieved. In order to run mongodb tests, make sure to install the mongodb community edition with\n"
            "the following link:\n"
            "https://docs.mongodb.com/manual/installation/"
        )
        yield False
        return
    # Write one collection doc in mongo
    mongo_coll = "assignments"
    try:
        exemplars_to_mongo(REGOLITH_MONGODB_NAME, collection_list=[mongo_coll])
    except ConnectionError:
        yield False
        return
    # Write one collection doc in file system
    fs_coll = "abstracts"
    exemplars_to_fs(fspath, collection_list=[fs_coll])
    yield repo, fs_coll, mongo_coll
    cmd = ["mongo", REGOLITH_MONGODB_NAME, "--eval", "db.dropDatabase()"]
    try:
        subprocess.check_call(cmd, cwd=repo)
    except CalledProcessError:
        print(
            f'Deleting the test database failed, insert "mongo {REGOLITH_MONGODB_NAME} --eval '
            f'"db.dropDatabase()"" into command line manually'
        )
    shut_down_fork(forked, repo)
    os.chdir(cwd)
    if not OUTPUT_FAKE_DB:
        rmtree(repo)


@pytest.fixture(scope="session")
def make_bad_db():
    """A test fixutre that creates and destroys a git repo in a
    temporary directory.

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


@pytest.fixture(scope="function")
def make_fs_to_mongo_migration_db():
    """A test fixture that creates and destroys a git repo in a
    temporary directory, as well as a mongo database. This will yield
    the path to the repo.

    This specific test fixture points to a repo that contains mongo and
    filesystem backends with only the filesystem containing the
    exemplars. This is meant for use in migration testing.
    """
    yield from make_migration_db(True)


@pytest.fixture(scope="function")
def make_mongo_to_fs_backup_db():
    """A test fixture that creates and destroys a git repo in a
    temporary directory, as well as a mongo database. This will yield
    the path to the repo.

    This specific test fixture points to a repo that contains mongo and
    filesystem backends with only the filesystem containing the
    exemplars. This is meant for use in migration testing.
    """
    yield from make_migration_db(False)


def make_migration_db(fs_to_mongo_true__mongo_to_fs_false):
    cwd = os.getcwd()
    forked = False
    name = "regolith_mongo_fake"
    repo = os.path.join(tempfile.gettempdir(), name)
    if os.path.exists(repo):
        rmtree(repo)
    subprocess.run(["git", "init", repo])
    os.chdir(repo)
    with open("README", "w") as f:
        f.write("testing " + name)
    mongodbpath = os.path.join(repo, "dbs")
    os.mkdir(mongodbpath)
    fspath = os.path.join(repo, "db")
    os.mkdir(fspath)
    with open("regolithrc.json", "w") as f:
        json.dump(
            {
                "groupname": "ERGS",
                "databases": [
                    {
                        "name": ALTERNATE_REGOLITH_MONGODB_NAME,
                        "dst_url": "localhost",
                        "url": repo,
                        "path": "db",
                        "public": True,
                        "local": True,
                        "backend": "mongodb",
                    }
                ],
                "mongodbpath": mongodbpath,
            },
            f,
        )
    if os.name == "nt":
        # If on windows, the mongod command cannot be run with the fork or syslog options.
        # Instead, it is installed as a service and the exceptions that would typically be log outputs
        # are handled by the exception handlers below. In addition, the database must always be manually
        # deleted from the windows mongo instance before running a fresh test.
        cmd = ["mongo", ALTERNATE_REGOLITH_MONGODB_NAME, "--eval", "db.dropDatabase()"]
        try:
            subprocess.check_call(cmd, cwd=repo)
        except CalledProcessError:
            print(
                "Mongod likely has not been installed as a service. In order to run mongodb tests, make sure\n"
                "to install the mongodb community edition with the following link: \n"
                "https://docs.mongodb.com/manual/installation/"
            )
            yield False
            return
        cmd = ["mongostat", "--host", "localhost", "-n", "1"]
    else:
        cmd = ["mongod", "--fork", "--syslog", "--dbpath", mongodbpath]
        forked = True
    try:
        subprocess.check_call(cmd, cwd=repo)
    except CalledProcessError:
        print(
            "If on linux/mac, Mongod command failed to execute. If on windows, the status of mongo could not be\n"
            "retrieved. In order to run mongodb tests, make sure to install the mongodb community edition with\n"
            "the following link:\n"
            "https://docs.mongodb.com/manual/installation/"
        )
        yield False
        return
    if fs_to_mongo_true__mongo_to_fs_false:
        exemplars_to_fs(fspath)
    else:
        exemplars_to_mongo(ALTERNATE_REGOLITH_MONGODB_NAME)
    yield repo
    cmd = ["mongo", ALTERNATE_REGOLITH_MONGODB_NAME, "--eval", "db.dropDatabase()"]
    try:
        subprocess.check_call(cmd, cwd=repo)
    except CalledProcessError:
        print(
            f'Deleting the test database failed, insert "mongo {ALTERNATE_REGOLITH_MONGODB_NAME} --eval '
            f'"db.dropDatabase()"" into command line manually'
        )
    shut_down_fork(forked, repo)
    os.chdir(cwd)
    if not OUTPUT_FAKE_DB:
        rmtree(repo)


def shut_down_fork(forked, repo):
    if forked:
        cmd = ["mongo", "admin", "--eval", "db.shutdownServer()"]
        try:
            subprocess.check_call(cmd, cwd=repo)
        except CalledProcessError:
            print(
                'Deleting the test database failed, insert "mongo admin --eval '
                '"db.shutdownServer()"" into command line manually'
            )


def exemplars_to_fs(fspath, collection_list=None):
    exemplars_copy = deepcopy(EXEMPLARS)
    if collection_list is None:
        exemplars = exemplars_copy
    else:
        exemplars = {k: exemplars_copy[k] for k in collection_list if k in exemplars_copy}
    cwd = os.getcwd()
    os.chdir(fspath)
    for coll, example in exemplars.items():
        if isinstance(example, list):
            d = {dd["_id"]: dd for dd in example}
        else:
            d = {example["_id"]: example}
        dump_yaml("{}.yaml".format(coll), d)
    os.chdir(cwd)


def exemplars_to_mongo(mongo_db_name, collection_list=None):
    exemplars_copy = deepcopy(EXEMPLARS)
    if collection_list is None:
        exemplars = exemplars_copy
    else:
        exemplars = {k: exemplars_copy[k] for k in collection_list if k in exemplars_copy}
    client = MongoClient("localhost", serverSelectionTimeoutMS=2000)
    client.server_info()
    for col_name, example in exemplars.items():
        db = client[mongo_db_name]
        col = db[col_name]
        try:
            if isinstance(example, list):
                for doc in example:
                    doc["_id"].replace(".", "")
                col.insert_many(example)
            else:
                example["_id"].replace(".", "")
                col.insert_one(example)
        except mongo_errors.DuplicateKeyError:
            print("Duplicate key error, check exemplars for duplicates if tests fail")
        except mongo_errors.BulkWriteError:
            print("Duplicate key error, check exemplars for duplicates if tests fail")
