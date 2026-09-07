**Added:**

* ``regolith build --all`` builds everything a target has rather than the part
  of it that is current, for the builders that narrow by default.  It reads
  the same way as ``--all`` on the listers.

**Changed:**

* <news item>

**Deprecated:**

* <news item>

**Removed:**

* <news item>

**Fixed:**

* Somebody whose people record does not say whether they are active counts as
  active, which is what the schema says the field defaults to.  They were
  being treated as having left the group, so their projects were reported as
  orphaned.

**Security:**

* <news item>
