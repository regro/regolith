**Added:**

* Add the u_grant helper to update a grant's award number, account, dates, amount, status and other details. Each detail is written to the database already holding it, and a new one goes to the public or private database.
* The a_grant helper now stores a grant's public details (title, amount, currency, award number, funder, team and dates) in the database marked public in regolithrc.json and the rest, such as the account and budget, in the database marked private. Choose other databases with --public-database and --private-database.
* insert_one and update_one take partial=True for a document that is one part of a record split across databases, so that a Mongo database checks its fields without requiring the fields stored in the other part.

**Changed:**

* <news item>

**Deprecated:**

* <news item>

**Removed:**

* <news item>

**Fixed:**

* The a_grant helper now marks the seeded proposal accepted in the database holding it, not in the first database.

**Security:**

* <news item>
