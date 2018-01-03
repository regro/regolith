**Added:**

* Schemas and exemplars for the collections.
  Database entries are checked against the schema, making sure that all the
  required fields are filled and the values are the same type(s) listed in the
  schema. The schema also includes descriptions of the data to be included.
  The exemplars are examples which have all the specified fields and are
  used to check the validation.
* Docs auto generate for collections (if they were documented in the schema).

**Changed:**

* App now validates incoming data against schema

**Deprecated:** None

**Removed:** None

**Fixed:** None

**Security:** None
