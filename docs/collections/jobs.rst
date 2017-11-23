Jobs
============
This collection describes the research group jobs. This is normally public data.


Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: str or number, unique job identifier
:title: str, Job title
:description: str, long description of the position
:open: bool, flag for whether the job is currently open or not.
:contact: str, contact information for how to apply
:positions: list of strings, positions such as "Graduate Student", "Post-doctoral Scholar",
:background_fields: list of str, previous disciplines, e.g. Nuclear Engineering or Computer Science
:year: int, year job posted
:month: str, month the job was posted
:day: int, day the job was posted
:start_date: str, expected start date or "ASAP" or similar
:expertise: str, Current skills applicatns should have
:compensation: list of str, list of compensations for the position.


YAML Example
------------

.. code-block:: yaml

    '0004':
      background_fields:
        - Data Science
        - Data Engineering
        - Computer Engineering
        - Computer Science
        - Applied Mathematics
        - Physics
        - Nuclear Engineering
        - Mechanical Engineering
        - Or similar
      compensation:
        - Salary and compensation will be based on prior work experience.
      contact: Please send CV or resume to Prof. Scopatz at scopatzATcec.sc.edu.
      day: 1
      description: <p>We are seeking a dedicated individual to help to aid in the maintenance
        of open source scientific computing projects. This includes duties such as:</p><ul><li>Release
        management</li><li>Continuous integration</li><li>Help with testing</li><li>Code
        review</li><li>and more!</li></ul><p>Representative projects of interest include:</p><ul><li><a
        href="http://fuelcycle.org/">Cyclus</a></li><li><a href="http://pyne.io/">PyNE</a></li><li>and
        others.</li></ul><p>This position will likely make you the most loved person on
        these projects.</p>
      expertise: <p>Applicable software development skills include knowledge of:</p><ul><li>At
        least one programming language, preferred languages include:<ul><li>Python</li><li>Haskell</li><li>C++</li></ul></li><li>git
        or hg, or other version control system</li><li>Test-driven development</li><li>Other
        software development best practices.</li></ul><p>Potentially useful other software
        development skills include:</p><ul><li>Shell (Bash, Fish, Xonsh)</li></ul>
      month: July
      open: false
      positions:
        - Scientific Software Developer
        - Programmer
      start_date: ASAP
      title: Open Source Scientific Software Maintainer
      year: 2015


JSON/Mongo Example
------------------

.. code-block:: json

    {"_id": "0004",
     "background_fields": ["Data Science",
                           "Data Engineering",
                           "Computer Engineering",
                           "Computer Science",
                           "Applied Mathematics",
                           "Physics",
                           "Nuclear Engineering",
                           "Mechanical Engineering",
                           "Or similar"],
     "compensation": ["Salary and compensation will be based on prior work experience."],
     "contact": "Please send CV or resume to Prof. Scopatz at scopatzATcec.sc.edu.",
     "day": 1,
     "description": "<p>We are seeking a dedicated individual to help to aid in ...",
     "month": "July",
     "open": false,
     "positions": ["Scientific Software Developer", "Programmer"],
     "start_date": "ASAP",
     "title": "Open Source Scientific Software Maintainer",
     "year": 2015}
