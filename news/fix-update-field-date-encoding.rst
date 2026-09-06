**Added:**

* <news item>

**Changed:**

* <news item>

**Deprecated:**

* <news item>

**Removed:**

* <news item>

**Fixed:**

* ``f_todo``, ``u_todo`` and ``a_todo`` no longer fail against a mongo database
  with ``bson.errors.InvalidDocument: cannot encode object: datetime.date`` when
  the task they write carries a date.  ``update_field`` sent the value to the
  server without the cleanup that turns a ``datetime.date`` into the iso string
  regolith stores, which ``update_one`` has always done.

**Security:**

* <news item>
