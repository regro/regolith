**Added:**

* ``regolith.lazy.LazyRegistry``, a mapping that imports each entry the first
  time it is used.  ``BUILDERS`` and ``HELPERS`` hold import paths rather than
  classes, so a command imports only the target it was asked for.
* ``regolith.dbpaths`` and ``regolith.common`` hold the
  few things the database layer needed from ``regolith.tools``, so the clients no
  longer import the rest of it.  ``regolith.tools`` re-exports them.

**Changed:**

* Starting up no longer imports pandas, matplotlib, pypdf, habanero or the
  google api client.  Listing every builder and helper pulled all of them in,
  even for ``regolith --version``, which touches no database.  ``import
  regolith.main`` drops from about 816 ms to about 90 ms, and ``regolith
  --version`` from about 980 ms to about 280 ms.

**Deprecated:**

* <news item>

**Removed:**

* <news item>

**Fixed:**

* <news item>

**Security:**

* <news item>
