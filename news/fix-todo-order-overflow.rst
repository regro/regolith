**Added:**

* ``tools.get_todo_order``, which weighs a task for sorting by how long is left
  before it is due.

**Changed:**

* <news item>

**Deprecated:**

* <news item>

**Removed:**

* <news item>

**Fixed:**

* ``regolith helper f_todo`` and ``regolith helper u_todo`` no longer crash with
  ``OverflowError: math range error`` when a task is due, or overdue, by more
  than about two years.  All three todo helpers computed the sort weight as
  ``1 / (1 + exp(abs(days_to_due - 0.5)))``, which overflows once the exponent
  passes 710.  They now share ``tools.get_todo_order``, which uses the form that
  underflows to zero instead.
* ``regolith helper l_todo`` sorts a task that is due, or overdue, by more than
  about two years alongside the other distant tasks.  It caught the overflow but
  substituted infinity, which sorted such a task as the most urgent rather than
  the least.

**Security:**

* <news item>
