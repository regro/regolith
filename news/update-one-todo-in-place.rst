**Added:**

* ``update_field`` on the database clients, which sets one field of one document
  and leaves the rest of it alone.  The field is named by a path, so
  ``"todos.3"`` is the fourth entry of the ``todos`` list.

**Changed:**

* ``u_todo`` sets the one task it changed rather than writing the whole task
  list back.  Against a mongo database the whole list was sent every time, and
  it was the largest single cost of the update: 1.4 s of a 6.4 s run on a
  production database.  Renumbering with ``-r`` still writes the list, since it
  changes every entry.

**Deprecated:**

* <news item>

**Removed:**

* <news item>

**Fixed:**

* <news item>

**Security:**

* <news item>
