**Added:**

* <news item>

**Changed:**

* The makeappointments helper now includes every grant still running on or after the projection date, not only grants with appointments, so a current grant no one is appointed on yet shows as unspent and is plotted.
* The makeappointments helper now plots only grants that end on or after the projection date, unless --verbose is given; before, grants that ended up to two years earlier were plotted too.

**Deprecated:**

* <news item>

**Removed:**

* <news item>

**Fixed:**

* The makeappointments helper now finds a grant whatever case an appointment names its id or alias in, and lists appointments on grants it cannot find, grants with no budget or no dates, and grants whose budget does not span the grant, instead of stopping at the first.

**Security:**

* <news item>
