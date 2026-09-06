**Added:**

* ``ClientManager.collection_sources`` reports which databases hold a collection,
  and ``load_collection`` reads one collection on demand.  The clients gain
  ``available_collections`` and ``load_collection`` alongside them.

**Changed:**

* Collections are read when they are first asked for rather than when the
  databases are opened.  ``open_dbs`` now builds only a source map, from one
  directory listing per filesystem database and one ``list_collection_names``
  per mongo database, reading no documents; ``rc.client.chained_db`` chains each
  collection on first access.  A command that declares no ``needed_colls``, or
  that declares more than it uses, no longer pays for the collections it never
  touches.
* ``dump_database(force=True)`` writes every *loaded* collection rather than
  every collection, since unread collections cannot have been modified.

**Deprecated:**

* <news item>

**Removed:**

* <news item>

**Fixed:**

* <news item>

**Security:**

* <news item>
