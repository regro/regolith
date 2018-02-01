**Added:**

* Database clients now merge collections across databases so records across
  public and private databases can be put together. This is in
  ``client.chained_db``.

* Blacklist for db files (eg. ``travis.yml``) the default (if no blacklist is
  specified in the ``rc`` is to blacklist ``['.travis.yml', '.travis.yaml']``

**Changed:**

* ``all_docs_from_collection`` use the ``chained_db`` to pull from all dbs at
  once. This is a breaking API change for ``rc.client.all_documents``

**Deprecated:**

* Mongo database support is being deprecated (no ``chained_db`` support)

**Removed:** None

**Fixed:** None

**Security:** None
