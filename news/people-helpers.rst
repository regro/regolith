**Added:**

* Add the a_person helper to add a group member, with their position in the group and the date they are expected to leave, to the public database.
* Add the a_service helper to add a service entry to a person, by default yourself, in the public database or with --private in the private one. Each entry is given a uuid.
* Add the u_person helper to update a person: simple details as options, --end-date to set when their current position in the group ends, and --edit to change a list such as employment, education or service in your text editor, grouped by the database each part is stored in, so entries can be moved between public and private.
* Add person_records.py with the shared code for finding and writing a person's record across databases.

**Changed:**

* Allow outreach as a service type, which the activity log builder already reports.

**Deprecated:**

* <news item>

**Removed:**

* <news item>

**Fixed:**

* <news item>

**Security:**

* <news item>
