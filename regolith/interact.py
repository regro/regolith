"""
Loads the dbs for interactive sessions
"""
from regolith.database import connect
from regolith.runcontrol import DEFAULT_RC, load_rcfile, filter_databases

rc = DEFAULT_RC
rc._update(load_rcfile("regolithrc.json"))
filter_databases(rc)

with connect(rc) as rc.client:
    dbs = rc.client.dbs
    chained_db = rc.client.chained_db
