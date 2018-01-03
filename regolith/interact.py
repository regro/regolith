"""
Loads the dbs for interactive sessions
"""
from regolith.main import DEFAULT_RC, load_rcfile, filter_databases
from regolith.database import CLIENTS, load_database, dump_database
from regolith.tools import all_docs_from_collection

rc = DEFAULT_RC
rc._update(load_rcfile('regolithrc.json'))
filter_databases(rc)

client = CLIENTS[rc.backend](rc)
for db in rc.databases:
    print(db)
    load_database(db, client, rc)

col = {}
db_names = set([db['name'] for db in rc.databases])
mega_db = client.mega_dball_docs_from_collection

