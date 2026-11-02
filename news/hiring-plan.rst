**Added:**

* Add the l_hiringplan helper to work out how many students and postdocs the grants can support. It tries every number of new students and postdocs up to --students-most and --postdocs-most against the grants' budgets, the appointments already made and the current group members, and suggests the most hires that the new funding expected keeps up with, month by month. New funding is pending proposals times --success-rate, plus --new-funding-per-year for proposals not yet written. Unspent months carry forward within a grant, and federal grants are assumed to get a one-year no-cost extension, used only when nothing else can pay. --plan shows any plan year by year.
* Add hiring_plan.py with the calculations behind l_hiringplan.

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
