**Added:**

* ``meals-log`` builder, which fills the UCSB daily meals log with the meals left on
  a travel expense.  ``regolith build meals-log`` builds the expenses of the
  ``default_user_id`` that have still to be submitted, ``--people <person>`` builds
  for somebody else, and ``--kwargs _id:<id>`` builds one named expense whatever its
  status and whoever its payee.  One form is written per expense that has meals on
  it, and a trip longer than the 19 rows the form carries is written over as many
  copies as it needs.

* ``ucsb-meals-log.pdf``, the empty form, to the templates folder.  It is a fillable
  AcroForm, so the builder sets the field values rather than rendering a template,
  and the form the university issued is passed through untouched.

* ``pypdf`` to the requirements, used to fill the form.

**Changed:**

* The mean dinner rate is now 42.50 USD and incidentals 5.00 USD, down from 55.00 and
  10.00.  The four means now sum to 84.50, which keeps a day inside the 92 USD limit
  about nine times in ten.

**Deprecated:**

* <news item>

**Removed:**

* <news item>

**Fixed:**

* <news item>

**Security:**

* <news item>
