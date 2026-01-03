"""Loads the dbs for interactive sessions."""

from regolith.runcontrol import DEFAULT_RC, connect_db, filter_databases, load_rcfile

rc = DEFAULT_RC
rc._update(load_rcfile("regolithrc.json"))
filter_databases(rc)

chained_db, dbs = connect_db(rc)
