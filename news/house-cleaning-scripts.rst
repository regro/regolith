**Added:**

* ``python -m regolith`` runs regolith.

**Changed:**

* ``helper_connect`` is now ``helper-connect``, and the profiling commands are
  ``profile-regolith`` and ``profile-helper-gui``.  ``helper_connect`` still
  works and says where it went.

**Deprecated:**

* <news item>

**Removed:**

* <news item>

**Fixed:**

* The Windows launchers start something.  Every ``.bat`` ran ``python -m``
  against its own file name, and none of those was an importable module, so
  none of them worked.
* ``profile-regolith`` and ``profile-helper-gui`` profile what their names
  say.  Both called ``main()`` without importing one, and neither had ever
  run.

**Security:**

* <news item>
