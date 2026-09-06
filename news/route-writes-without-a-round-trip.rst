**Added:**

* <news item>

**Changed:**

* <news item>

**Deprecated:**

* <news item>

**Removed:**

* <news item>

**Fixed:**

* Reading or writing one document no longer asks the server which databases
  exist.  ``ClientManager`` decided which client backed a database by calling
  ``client.keys()``, which for the mongo backend is ``list_database_names`` and
  so a round trip, once per operation.  It now reads the backend from the rc,
  which already records it.  A find followed by an update goes from five round
  trips to three.

**Security:**

* <news item>
