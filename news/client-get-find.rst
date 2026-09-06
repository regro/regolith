**Added:**

* ``get(collname, _id)`` and ``find(collname, filter)`` on the database clients.
  ``ClientManager`` asks each database for the documents it holds and chains only
  those, so a mongo backend answers an id lookup from its index and a filtered
  query on the server instead of returning the whole collection.  The filesystem
  client gains the same two methods, and ``find_one`` now looks an id up rather
  than scanning.

**Changed:**

* <news item>

**Deprecated:**

* <news item>

**Removed:**

* <news item>

**Fixed:**

* <news item>

**Security:**

* <news item>
