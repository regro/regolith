**Added:**

* Add ``--submitted-date``, ``--status`` and ``--call-for-proposals`` options to the ``a_proposal`` helper.

**Changed:**

* ``a_proposal`` now builds the proposal team from the PI and ``--authors`` (as co-PIs), using people's full names where they are in the people collection, instead of writing an empty placeholder team member.
* ``a_proposal`` leaves out dates that were not given instead of writing ``tbd``.
* ``a_proposal`` error messages now say how to fix the problem.

**Deprecated:**

* <news item>

**Removed:**

* <news item>

**Fixed:**

* ``a_proposal`` computes the end date from ``--duration`` in calendar months, so a 36 month grant beginning 2026-09-01 ends 2029-08-31 rather than a few days later.

**Security:**

* <news item>
