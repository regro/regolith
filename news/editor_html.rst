**Added:**

* Optional ``static_source`` key in the rc for the html build.k

**Changed:**

* institution dereference is done by ``regolith.tools.dereference_institution`` function
* HTML pages dereference institutions
* ``person.html`` allows for authors or editors and hides publications in details
* ``root_index.html`` allows for banner to be speced in ``groups`` collection

**Deprecated:** None

**Removed:** None

**Fixed:**

* Properly handle authors and editors set in ``regolith.tools.filter_publications``

**Security:** None
