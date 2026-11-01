**Added:**

* Add ``has_dates`` to ``dates.py`` to tell whether a document carries any date information, in ISO or legacy form.

**Changed:**

* Sort keys in ``sorters.py``, the facilities, patents, licenses and awards filters in ``tools.py``, and the most-recent-organization lookup in ``coabuilder.py`` now read dates through ``get_dates``, so ISO ``begin_date``/``end_date``/``date`` values work everywhere the legacy ``begin_year``/``end_month`` style did. The legacy style still works.

**Deprecated:**

* <news item>

**Removed:**

* <news item>

**Fixed:**

* Fix ``awards`` crashing on honors with a ``begin_year``, and ``filter_licenses`` crashing when no ``since`` date is given.

**Security:**

* <news item>
