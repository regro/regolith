**Added:**

* <news item>

**Changed:**

* Database directory and file paths in ``tools.dbdirname``, ``tools.dbpathname``,
  ``fsclient.py``, ``mongoclient.py`` and ``database.xsh`` are now composed with
  ``pathlib.Path`` instead of ``os.path`` string joins.

**Deprecated:**

* <news item>

**Removed:**

* <news item>

**Fixed:**

* ``OSError: [Errno 22] Invalid argument`` when dumping collections on Windows under
  python 3.14.  A posix-style ``url`` or ``path`` in ``regolithrc.json`` was joined as a
  string, producing a filename such as ``..\../rg-db-private/db\people.yml`` that mixes
  ``/`` and ``\`` separators.

**Security:**

* <news item>
