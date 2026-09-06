**Added:**

* <news item>

**Changed:**

* ``f_todo`` sets the one task it finished, and ``a_todo`` sets the one position
  it appends, rather than writing the whole task list back.  ``u_todo`` already
  did.  Against a mongo database the whole list went over the network for a
  change to one entry of it.  A document that has no task list yet still has the
  list written, since setting a numbered field on it would store a mapping
  rather than a list.

**Deprecated:**

* <news item>

**Removed:**

* <news item>

**Fixed:**

* ``FileSystemClient.update_field`` appends when the step into a list is the
  next free position, and pads with nulls beyond it, which is what ``$set`` does
  on mongo.  It raised ``IndexError``, so the two backends disagreed about
  appending.

**Security:**

* <news item>
