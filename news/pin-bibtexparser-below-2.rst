**Added:**

* <news item>

**Changed:**

* <news item>

**Deprecated:**

* <news item>

**Removed:**

* <news item>

**Fixed:**

* The CV, resume, publist and annual-activity builders write their ``.bib``
  file again.  bibtexparser 2 dropped the modules regolith writes bibtex with,
  and the requirements did not pin a version, so a fresh install silently
  produced documents with no bibliography.  A bibliography that cannot be
  written now says so rather than going missing quietly.

**Security:**

* <news item>
