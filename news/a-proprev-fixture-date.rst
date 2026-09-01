**Added:**

* ``--date`` option to the ``a_proprev`` helper, so tests can fix the date that the
  document id is built from.  It follows the convention already used by
  ``a_proposal``, ``a_grppub_readlist``, ``u_milestone`` and ``l_progressreport``.

**Changed:**

* <news item>

**Deprecated:**

* <news item>

**Removed:**

* <news item>

**Fixed:**

* The expected ``a_proprev`` output is compared again.  It sat in
  ``tests/outputs/helper/proposalReviews.yml``, where the test never looked, so it
  went stale and the helper had no output coverage.  Moved to
  ``tests/outputs/a_proprev/proposalReviews.yaml``, the name the test builds from the
  helper name and the extension the helper writes, and refreshed to the current output.

**Security:**

* <news item>
