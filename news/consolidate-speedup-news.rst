**Added:**

* Add ``REGOLITH_LOG_LEVEL``.  Set it to ``DEBUG`` to see which collections a
  command reads and which database each came from, which is the quickest way to
  find out why a command is slow.

**Changed:**

* Speed up every command, most of all those that work with todos.  Starting up
  no longer imports every builder and helper, and with them pandas, matplotlib
  and pypdf, so a command pays only for the target it was asked for.  A
  collection is read when it is first used rather than when the databases are
  opened, only from the databases that hold it, and with a faster YAML reader
  unless it is going to be written.  The todo helpers fetch the one person's
  record they need by id, and write back only the task they changed, instead of
  reading and rewriting the whole collection.  On a group database with todos on
  MongoDB Atlas, adding a task went from 21 s to about 5 s, and listing,
  updating and finishing one from about 9 s to under 4 s.
* Leave the database files untouched when a command only reads them.  Every
  command used to rewrite every collection it had loaded on the way out, and a
  git backed database was committed and pushed after a read.

**Deprecated:**

* <news item>

**Removed:**

* Remove the ``xonsh`` and ``rever`` dependencies.  Neither is needed to run
  regolith, and importing ``xonsh`` alone accounted for about a third of the
  time a command took to start.

**Fixed:**

* Fix ``f_todo`` and ``u_todo`` failing with ``OverflowError: math range error``
  for a task due, or overdue, by more than about two years, and ``l_todo``
  ordering such a task as the most urgent rather than the least.
* Fix listing the collections of a MongoDB database, and backing one up to the
  filesystem, both of which raised ``AttributeError`` on pymongo 4.
* Fix ``deploy`` and ``store`` failing to report a failed ``git`` command,
  raising ``AttributeError`` instead of the intended warning.

**Security:**

* <news item>
