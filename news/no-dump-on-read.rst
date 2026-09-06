**Added:**

* <news item>

**Changed:**

* ``FileSystemClient.dump_database`` and ``ClientManager.dump_database`` take a
  ``force`` keyword that writes every loaded collection, as the pre-existing
  behavior did.

**Deprecated:**

* <news item>

**Removed:**

* <news item>

**Fixed:**

* Commands that only read the database no longer rewrite every collection file
  on the way out.  The filesystem client now tracks which collections were
  modified and dumps only those, so listers and builders leave the database
  untouched and git-backed databases are no longer auto-committed and pushed
  after a read.

**Security:**

* <news item>
