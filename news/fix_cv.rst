**Added:** None

**Changed:**

* ``regolith.builders.CVBuilder`` now dereferences institutions/organizations
  for employers and education
* ``regolith.builders.CVBuilder`` deepcopies each person so we don't modify
  the records during dereference

**Deprecated:** None

**Removed:** None

**Fixed:**

* ``regolith.tools.fuzzy_retrieval`` properly handles null values
* education and employment subschemas for people are now just lists
* ``regolith.builders.BuilderBase`` uses ``latex_safe`` from ``regolith.tools``

**Security:** None
