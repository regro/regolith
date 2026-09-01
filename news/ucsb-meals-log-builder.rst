**Added:**

* ``meals-log`` builder, which fills the UCSB daily meals log with the meals left on
  a travel expense.  Run it as ``regolith build meals-log --people <person>``.  One
  form is written per expense that has meals on it, and a trip longer than the 19
  rows the form carries is written over as many copies as it needs.

* ``ucsb-meals-log.pdf``, the empty form, to the templates folder.  It is a fillable
  AcroForm, so the builder sets the field values rather than rendering a template,
  and the form the university issued is passed through untouched.

* ``pypdf`` to the requirements, used to fill the form.

**Changed:**

* <news item>

**Deprecated:**

* <news item>

**Removed:**

* <news item>

**Fixed:**

* <news item>

**Security:**

* <news item>
