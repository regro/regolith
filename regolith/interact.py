"""
Loads the dbs for interactive sessions
"""
from regolith.runcontrol import DEFAULT_RC, load_rcfile, filter_databases, \
    connect_db

rc = DEFAULT_RC
rc._update(load_rcfile("regolithrc.json"))
filter_databases(rc)

chained_db, dbs = connect_db(rc)
