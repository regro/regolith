**Added:**

* <news item>

**Changed:**

* <news item>

**Deprecated:**

* <news item>

**Removed:**

* <news item>

**Fixed:**

* A write to a database none of whose collections had been read yet was dropped
  without a word.  ``ClientManager`` asks each client whether it backs a database
  before routing ``insert_one``, ``insert_many``, ``update_one``, ``delete_one``
  or ``find_one`` to it, and ``FileSystemClient.keys`` named only the databases
  it had already read a collection from.  Since collections became lazy this was
  none of them at the point a command started.  It named a database only because
  every helper happened to read a collection before writing.

**Security:**

* <news item>
