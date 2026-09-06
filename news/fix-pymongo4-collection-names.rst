**Added:**

* <news item>

**Changed:**

* <news item>

**Deprecated:**

* <news item>

**Removed:**

* <news item>

**Fixed:**

* ``MongoClient.collection_names`` and ``MongoClient.dump_database`` now list
  collections with ``list_collection_names``.  They called
  ``Database.collection_names``, which pymongo removed in 4.0, so listing the
  collections of a mongo database and backing one up to the filesystem both
  raised ``AttributeError``.

**Security:**

* <news item>
