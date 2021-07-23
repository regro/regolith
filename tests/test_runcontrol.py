import os
import copy

from regolith.runcontrol import DEFAULT_RC, load_rcfile, filter_databases, \
    connect_db
from regolith.database import connect


def test_connect_db(make_db):
    repo = make_db
    os.chdir(repo)
    rc = copy.copy(DEFAULT_RC)
    rc._update(load_rcfile("regolithrc.json"))
    filter_databases(rc)
    with connect(rc) as rc.client:
        expected_dbs = rc.client.dbs
        expected_chdb = rc.client.chained_db
    chained_db, dbs = connect_db(rc)
    for coll in chained_db.keys():
        if coll in expected_chdb:
            for k in chained_db[coll].keys():
                if k in expected_chdb[coll]:
                    assert chained_db[coll][k] == expected_chdb[coll][k]
                else:
                    assert False
        else:
            assert False
    for coll in dbs.keys():
        if coll in expected_dbs:
            for k in dbs[coll].keys():
                if k in expected_dbs[coll]:
                    assert dbs[coll][k] == expected_dbs[coll][k]
                else:
                    assert False
        else:
            assert False
