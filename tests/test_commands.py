import copy
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from regolith import commands
from regolith.database import connect
from regolith.dates import convert_doc_iso_to_date
from regolith.main import main
from regolith.mongoclient import load_mongo_col
from regolith.runcontrol import DEFAULT_RC, load_rcfile

# from regolith.tests.conftest import ALTERNATE_REGOLITH_MONGODB_NAME, FS_DB_NAME
# comment this out because pytest automatically imports conftest


BILLINGE_TEST = False  # special tests for Billinge group, switch it to False before push to remote


@pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
def test_fs_to_mongo(make_db, make_mongodb):
    if make_mongodb is False:
        pytest.skip("Skipping, Mongoclient failed to start")
    if BILLINGE_TEST:
        repo = str(Path(__file__).parent.parent.parent.joinpath("rg-db-group", "local"))
    else:
        repo = make_db
    cp1 = subprocess.run(["regolith", "fs-to-mongo"], cwd=repo)
    assert cp1.returncode == 0


def test_fs_to_mongo_python(make_fs_to_mongo_migration_db, make_mongodb):
    if make_mongodb is False:
        pytest.skip("Mongoclient failed to start")
    if BILLINGE_TEST:
        repo = str(Path(__file__).parent.parent.parent.joinpath("rg-db-group", "local"))
    else:
        repo = make_fs_to_mongo_migration_db
    os.chdir(repo)
    try:
        main(["fs-to-mongo"])
    except Exception as e:
        print(e)
        assert False
    else:
        assert True
    replace_rc_dbs(repo)
    os.chdir(repo)
    rc = copy.copy(DEFAULT_RC)
    rc._update(load_rcfile("regolithrc.json"))
    with connect(rc) as rc.client:
        fs_db = rc.client[FS_DB_NAME]
        mongo_db = rc.client[ALTERNATE_REGOLITH_MONGODB_NAME]
        for coll in fs_db.keys():
            original_fs_collection = fs_db[coll]
            migrated_mongo_collection = load_mongo_col(mongo_db[coll])
            for k, v in migrated_mongo_collection.items():
                migrated_mongo_collection[k] = convert_doc_iso_to_date(v)
            for k, v in original_fs_collection.items():
                original_fs_collection[k] = convert_doc_iso_to_date(v)
            assert original_fs_collection == migrated_mongo_collection


def test_mongo_to_fs_python(make_mongo_to_fs_backup_db, make_mongodb):
    if make_mongodb is False:
        pytest.skip("Mongoclient failed to start")
    repo = make_mongo_to_fs_backup_db
    os.chdir(repo)
    try:
        main(["mongo-to-fs"])
    except Exception as e:
        print(e)
        assert False
    else:
        assert True
    replace_rc_dbs(repo)
    os.chdir(repo)
    rc = copy.copy(DEFAULT_RC)
    rc._update(load_rcfile("regolithrc.json"))
    with connect(rc) as rc.client:
        fs_db = rc.client[FS_DB_NAME]
        mongo_db = rc.client[ALTERNATE_REGOLITH_MONGODB_NAME]
        for coll in mongo_db.list_collection_names():
            migrated_fs_collection = fs_db[coll]
            original_mongo_collection = load_mongo_col(mongo_db[coll])
            assert migrated_fs_collection == original_mongo_collection


def replace_rc_dbs(repo):
    cwd = os.getcwd()
    os.chdir(repo)
    with open("regolithrc.json", "r+") as f:
        data = json.load(f)
        data["databases"] = [
            {
                "name": FS_DB_NAME,
                "url": repo,
                "public": True,
                "path": "db",
                "local": True,
                "backend": "filesystem",
            },
            {
                "name": ALTERNATE_REGOLITH_MONGODB_NAME,
                "url": "localhost",
                "path": repo,
                "public": True,
                "local": True,
                "backend": "mongodb",
            },
        ]
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()
    os.chdir(cwd)


CITATIONS_BIB = """@article{meurer2016sympy,
 author = {Meurer, Aaron and Smith, Christopher P and van der Walt, Stefan},
 editor = {Scopatz, Anthony},
 title = {SymPy: Symbolic
          computing in Python},
 journal = {PeerJ Computer Science},
 year = {2017}
}

@misc{a_dataset,
 author = {Billinge, Simon J. L.},
 title = {A dataset},
 year = {2026}
}
"""


def test_ingesting_citations_reads_a_bib_file(tmp_path, monkeypatch):
    # Test reading a bibtex file into the citations collection.  Nothing
    # covered this, and the reader is the half of bibtexparser that regolith
    # does not write with, so a change of version could break it in silence
    # until somebody ingested a file
    path = tmp_path / "refs.bib"
    path.write_text(CITATIONS_BIB, encoding="utf-8")
    written = {}

    class FakeClient:
        def update_one(self, db, coll, filter, doc, upsert=False):
            written[filter["_id"]] = doc

    rc = SimpleNamespace(filename=str(path), db="test", coll="citations", client=FakeClient())
    commands._ingest_citations(rc)

    assert sorted(written) == ["a_dataset", "meurer2016sympy"]
    article = written["meurer2016sympy"]
    # the entry type is a field of the record rather than the entry
    assert article["entrytype"] == "article"
    # every name field is a list, one "Last, First" to an author, however the
    # file wrote them
    assert article["author"] == ["Meurer, Aaron", "Smith, Christopher P", "van der Walt, Stefan"]
    assert article["editor"] == ["Scopatz, Anthony"]
    # a title wrapped over two lines in the file is one line in the record
    assert article["title"] == "SymPy: Symbolic computing in Python"
    # an entry type bibtex does not standardise is read like any other
    assert written["a_dataset"]["entrytype"] == "misc"
