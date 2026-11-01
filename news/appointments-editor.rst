**Added:**

* Add the u_appointments helper to plan and update a group member's appointments. Without options it prints their appointments from today with alerts; --edit opens them in your text editor with the gaps until their funded position ends filled quarter by quarter on future_grant; --file reads them from a YAML file, for the helper GUI. They are stored in the private database.
* Appointments can be paid by outside funding, such as a fellowship or a TA, with outside_funding in place of a grant, and with a loading so a quarter can be split between outside funding and a grant.
* Add appointments.py with the checks behind u_appointments: gaps, more than full time, appointments past a grant's end, grants running out of money, unknown grants, and positions with no end date.

**Changed:**

* The makeappointments and l_currentappointments helpers now recognise appointments paid by outside funding.

**Deprecated:**

* <news item>

**Removed:**

* <news item>

**Fixed:**

* The makeappointments helper now checks from the projection date on. Before, it reported gaps, outdated and depleted appointments, and underspent grants from the beginning of time, whatever date was given.

**Security:**

* <news item>
