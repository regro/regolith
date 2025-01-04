import copy
import os

from regolith.database import connect
from regolith.runcontrol import DEFAULT_RC, connect_db, filter_databases, load_rcfile


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
    assert chained_db == expected_chdb
    assert dbs == expected_dbs
