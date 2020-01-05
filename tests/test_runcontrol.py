import json
import os
import sys
from io import StringIO

from regolith.main import main
from regolith.runcontrol import DEFAULT_RC, load_rcfile, filter_databases, \
    connect_db


def test_connect_db(make_db):
    rc = DEFAULT_RC
    rc._update(load_rcfile("regolithrc.json"))
    filter_databases(rc)
    expected_chdb = rc.client.chained_db
    expected_dbs = rc.client.dbs

    chained_db, dbs = connect_db(rc)
    assert chained_db == expected_chdb
    assert dbs == expected_dbs

