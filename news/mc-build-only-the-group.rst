**Added:**

* ``regolith build --build-everything`` builds for everybody rather than only
  the people currently in the group, for the builders that leave out the
  people who have left.

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
