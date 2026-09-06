**Added:**

* <news item>

**Changed:**

* ``l_todo``, ``u_todo`` and ``f_todo`` fetch the one person's document they need
  by id instead of reading the whole ``todos`` collection and searching it.  On a
  mongo backend that is an indexed query in place of downloading every person's
  todos, which dominated the time these helpers took.
* ``u_todo`` and ``f_todo`` no longer gather the ``todos`` collection into the
  template context, which nothing read, and ``l_todo`` gathers only the two
  collections it goes through in full.

**Deprecated:**

* <news item>

**Removed:**

* <news item>

**Fixed:**

* <news item>

**Security:**

* <news item>
