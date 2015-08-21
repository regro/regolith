"""Implementation of commands for command line."""
import json

from regolith.tools import string_types

def add_cmd(rc):
    """Adds documents to a collection in a database."""
    db = rc.client[rc.db]
    coll = db[rc.coll]
    docs = [json.loads(doc) if isinstance(doc, string_types) else doc
            for doc in rc.documents]
    coll.insert_many(docs)
