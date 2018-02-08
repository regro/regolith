====================
Regolith Change Log
====================

.. current developments

v0.1.9
====================

**Fixed:**

* ``all_documents`` now returns the values of an empty dict if the collection
  doesn't exist




v0.1.8
====================

**Added:**

* Database clients now merge collections across databases so records across
  public and private databases can be put together. This is in
  ``client.chained_db``.

* Blacklist for db files (eg. ``travis.yml``) the default (if no blacklist is
  specified in the ``rc`` is to blacklist ``['.travis.yml', '.travis.yaml']``
* Schemas and exemplars for the collections.
  Database entries are checked against the schema, making sure that all the
  required fields are filled and the values are the same type(s) listed in the
  schema. The schema also includes descriptions of the data to be included.
  The exemplars are examples which have all the specified fields and are
  used to check the validation.
* Docs auto generate for collections (if they were documented in the schema).


**Changed:**

* ``all_docs_from_collection`` use the ``chained_db`` to pull from all dbs at
  once. This is a breaking API change for ``rc.client.all_documents``
* App now validates incoming data against schema


**Deprecated:**

* Mongo database support is being deprecated (no ``chained_db`` support)


**Fixed:**

* Properly implemented the classlist ``replace`` operation.
* Fixed issue with classlist insertions using Mongo-style API
  (deprecated).
* Properly filter on course ids when emailing.
* ``fsclient`` dbs explicitly load 'utf-8' files, which fixes an issue on
  Windows




v0.1.7
====================

**Added:**

* ``BuilderBase`` Class for builders
* Logo to docs
* Filesystem-based client may now read from YAML files, in addition to JSON.
  Each collection can be in either JSON or YAML.


**Changed:**

* Refactored builders to use base class


**Fixed:**

* Fixed issue with CV builder not filtering grants properly.
* Fixed bug with ``super`` not being called in the HTML builder.




v0.1.6
====================

**Added:**

* Use Rever's whitespace parsing
* Fix template news




v0.1.5
====================

**Added:**

* Rever release tool
* Interactive session support
* run better release




v0.1.4
====================

**Added:**

* ``collabs`` field in db for collaborators
* ``active`` field in db for current collaborators/group members


**Changed:**

* People page only shows current members, former members on Former Members page




