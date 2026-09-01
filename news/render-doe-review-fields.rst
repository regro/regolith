**Added:**

* ``doe_appropriateness_data_management_plan`` and ``doe_other`` to the exemplar DOE
  proposal review, so the new sections of the report are covered by the tests.

**Changed:**

* <news item>

**Deprecated:**

* <news item>

**Removed:**

* <news item>

**Fixed:**

* The proposal review report now prints the reviewer's answers on the data management
  and sharing plan and their other comments.  ``a_proprev`` has been prompting for both
  since the DOE prompt update, but ``propreport.txt`` never rendered them, so the
  answers were collected and silently dropped.  Reviews written before those fields
  existed are read with a default, and the NSF report is unchanged.

**Security:**

* <news item>
