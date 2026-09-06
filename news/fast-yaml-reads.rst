**Added:**

* <news item>

**Changed:**

* A collection is read with ruamel's safe loader, which is around nine times
  faster than the round trip loader regolith used for everything.  A collection
  that is about to be written is read again with the round trip loader, so the
  comments and formatting of the file it came from still survive being written
  back.  Reading a 100 kB collection drops from about 0.18 s to about 0.02 s, and
  ``regolith helper l_todo`` on a 5.7 MB database from about 1.40 s to about
  0.52 s.

**Deprecated:**

* <news item>

**Removed:**

* <news item>

**Fixed:**

* <news item>

**Security:**

* <news item>
