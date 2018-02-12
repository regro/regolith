.. raw:: html

    <link href="_static/unicodetiles.css" rel="stylesheet" type="text/css" />
    <script src="_static/unicodetiles.min.js"></script>
    <script src="_static/rg-dungeon.js"></script>
    <div style="text-align:center;">
        <div id="game"><h1>welcome to the regolith docs</h1></div>
    </div>
    <script type="text/javascript">initRgDungeon();</script>

Regolith
========
Regolith is a content management system for software & research groups.
Regolith creates and manages a database of people, publictaions, projects,
proposals & grants, courses, and more! From this database, regolith is then
able to:

* Generate a group website,
* Generate CVs and publication lists for the group members,
* Act as a grade book for your courses, and more!

Databases may be file-based (JSON and YAML) or MongoDB-based.

Regolith is developed as a `regro project <https://regro.github.io/>`_

Installation
============
Regolith packages are available from conda-forge and PyPI:

**conda:**

.. code-block:: sh

    $ conda install -c conda-forge regolith

**pip:**

.. code-block:: sh

    $ pip install regolith


Example Sites
=============
The following are some sample websites that are powered by regolith, even though building
websites is just one of the many facets of this tool:

1. `ERGS Home Page <http://www.ergs.sc.edu>`_
2. `Technical WorkShop on Fuel Cycle Simulation <http://twofcs.ergs.sc.edu>`_


Run Control
===========

.. toctree::
    :maxdepth: 1

    rc


Database Collections
====================
**Collections** are the regolith (and mongo) abstraction for *tables*.
**Entries** (or *rows*) in
a collection must follow the schema defined below. In general, the following notions
hold:

* An entry is a dictionary with string keys.
* Each entry must contain a unique identifier. This is called ``"_id"`` in JSON
  and Mongo, and is simply the top-level key in YAML.
* A collection is a list of entries that follow the same schema.

Not all regolith actions will use every collection type. It is common for regolith
projects to just use some of the collections below. For example, building a group
website will use different collections than managing students and grades in a course!
With these points in mind, feel free to dive into the databases below!

.. toctree::
    :maxdepth: 2

    collections/index


Regolith API
============
For those who want to dive deeper into the library itself.

.. toctree::
    :maxdepth: 1

    api/index


Regolith Commands
=================
Shell commmands for regolith

.. toctree::
     :maxdepth: 1

     commands/index