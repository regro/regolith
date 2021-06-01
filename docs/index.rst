.. role:: bash(code)
   :language: bash
.. role:: python(code)
   :language: python

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
Regolith creates and manages a database of people, publications, projects,
proposals & grants, courses, and more! From this database, regolith is then
able to:

* Generate a group website,
* Generate CVs and publication lists for the group members,
* Act as a grade book for your courses, and more!

Databases may be file-based (JSON and YAML) or MongoDB-based.

Regolith is developed as a `regro project <https://regro.github.io/>`_

Example Sites
=============
The following are some sample websites that are powered by regolith, even though 
building
websites is just one of the many facets of this tool:

1. `ERGS Home Page <http://www.ergs.sc.edu>`_
2. `Technical WorkShop on Fuel Cycle Simulation <http://twofcs.ergs.sc.edu>`_

Installation
============
1. Make your first database
----------------------------
The quickest way to get started is to set up your first minimal database using a 
handy cookie cutter.  These instructions use the command line and assume you know
how to use the terminal/cmd prompt

First install cookiecutter

.. code-block:: sh

    $ conda install cookiecutter

or 

.. code-block:: sh

    $ conda install cookiecutter

Next, clone the template repo from GitHub.  

.. code-block:: sh

    $ git clone git@github.com/sbillinge/regolithdb-cookiecutter

Make a note of the path to the resulting :bash:`regolithdb-cookiecutter` directory.

Next, move the directory where you want to install your very own database.  It 
recommended to create a directory off your home directory called :bash:`dbs`

.. code-block:: bash

    $ cd ~        # takes you to your home directory
    $ mkdir dbs   # creates the dbs directory if it is not already there
    $ cd dbs      # change dir to the new dbs directory

Now by running cookiecutter your starting db will be built from the template

.. code-block:: bash

    $ cookiecutter <path>/<to>/regolithdb-cookiecutter

The program will ask a series of questions and you can type responses.  Take your
time and answer the questions as accurately as possible, because you are already
entering data into your database!

The questions look like

.. code-block:: bash

    $ cookiecutter ../dev/regolithdb-cookiecutter/
    database_name [my-cv-db]:
    my_first_name [Albert]: Simon
    my_last_name [Einstein]: Billinge
    id_for_me [aeinstein]: sbillinge
    my_group_name [Einstein Group]: Billinge Group

and so on.  If you make a mistake just type CTL^C and try again.  

Type

.. code-block:: bash

    $ ls

and you should see a directory called :bash:`my-cv-db` or whatever you chose to 
call you database.

It is not too late to change answers to questions.  You can remove the 
database entirely (:bash:`$ rm my-cv-db`) and do it over. 

OK, let's go and look at our database.  change directory into it and do a directory
listing, 

.. code-block:: bash

    $ cd my-cv-db
    $ ls

or open a file
browser such as windows explorer and check out what is in there.

You will see a direcotry called :bash:`db` and a file called :bash:`regolithrc.json`.
All of the collections in your database are in the :bash:`db` directory.  The
is a bunch of information that Regolith needs to run and do its business. 
You can use the Regolith program to do a bunch of things with, and to, your
database. But you must always run Regolith from a directory that contains a
:bash:`regolithrc.json` file.  Since you are in a directory that contains one,
you can run Regolith from here, but first you have to install it....

2. install Regolith
---------------------
Regolith packages are available from conda-forge and PyPI:

**conda:**

.. code-block:: sh

    $ conda install -c conda-forge regolith

**pip:**

.. code-block:: sh

    $ pip install regolith

The Regolith code is migrating quickly these days.  If you prefer you can 
install from the GitHub repository in develop mode and get the latest changes.
In that case, clone the `GitHub repository  <https://github.com/regro/regolith>`_,
change directory to the top level directory in that cloned repository where the
:bash:`setup.py` file is.  From inside your virtual environment, type

.. code-block:: sh

    $ pip install regolith -e

which installs regolith in this environment in develop mode.

To check that your installation is working, let's have Regolith make us a
todo list from our database.  

Make sure you are in a directory that
contains a :bash:`regolithrc.json` file (which you should be if you have been 
following these instructions) and type

.. code-block:: sh

    $ regolith helper l_todos

and you should see something like 

.. code-block:: sh

    loading .\./db\todos.yml...
    dumping todos...
    usage: regolith helper [-h] [-s STATI [STATI ...]] [--short [SHORT]]
                           [-t TAGS [TAGS ...]] [-a ASSIGNED_TO]
                           [-b [ASSIGNED_BY]] [--date DATE]
                           [-f FILTER [FILTER ...]]
                           helper_target
    
    positional arguments:
      helper_target         helper target to run. Currently valid targets are:
                            ['a_expense', 'a_grppub_readlist', 'a_manurev',
                            'a_presentation', 'a_projectum', 'a_proposal',
                            'a_proprev', 'a_todo', 'f_prum', 'f_todo',
                            'l_abstract', 'l_contacts', 'l_grants', 'l_members',
                            'l_milestones', 'l_progress', 'l_projecta', 'l_todo',
                            'u_contact', 'u_institution', 'u_logurl',
                            'u_milestone', 'u_todo', 'v_meetings', 'lister',
                            'makeappointments']
    
    optional arguments:
      -h, --help            show this help message and exit
      -s STATI [STATI ...], --stati STATI [STATI ...]
                            Filter tasks with specific status from ['started',
                            'finished', 'cancelled', 'paused']. Default is
                            started.
      --short [SHORT]       Filter tasks with estimated duration <= 30 mins, but
                            if a number is specified, the duration of the filtered
                            tasks will be less than that number of minutes.
      -t TAGS [TAGS ...], --tags TAGS [TAGS ...]
                            Filter tasks by tags. Items are returned if they
                            contain any of the tags listed
      -a ASSIGNED_TO, --assigned_to ASSIGNED_TO
                            Filter tasks that are assigned to this user id.
                            Default id is saved in user.json.
      -b [ASSIGNED_BY], --assigned_by [ASSIGNED_BY]
                            Filter tasks that are assigned to other members by
                            this user id. Default id is saved in user.json.
      --date DATE           Enter a date such that the helper can calculate how
                            many days are left from that date to the due-date.
                            Default is today.
      -f FILTER [FILTER ...], --filter FILTER [FILTER ...]
                            Search this collection by giving key element pairs.
                            '-f description paper' will return tasks with
                            description containing 'paper'
    If the indices are far from being in numerical order, please renumber them by running regolith helper u_todo -r
    (index) action (days to due date|importance|expected duration (mins)|tags|assigned by)
    --------------------------------------------------------------------------------
    started:
    (1) Do all the things to set up todos in regolith (59|3|60.0||None)
    ------------------------------
    Tasks (decreasing priority going up)
    ------------------------------
    2021-07-29(59 days): (1) Do all the things to set up todos in regolith (59|3|60.0||None)
    ------------------------------
    Deadlines:
    ------------------------------

After all the help messages is your list of Todo items.  There is just one item,
:bash:`Do all the things to set up todos in regolith`. 

OK, your Regolith is working.  If it isn't working, consider joining, browsing 
and posting questions to the `regolith-users <https://groups.google.com/u/1/g/regolith-users>`_ 
Google group.

Quick(ish) Start
================
OK, let's use Regolith to build our cv.  Why not.  again, in a terminal navigate
to the top level directory of your database (where the :bash:`regolithrc.json` 
file is). and type:

.. code-block:: sh

    $ regolith build cv

Regolith will take information from the various collections in your database and
build them into your academic cv according to a pre-determined template.  The 
current template builds the cv using latex.  If your computer has latex installed
and Regolith can find it, your cv should appear as a pdf document in the directory
:bash:`my-cv-db/_build` (or more generally :bash:`<path>/<to>/<database_name>/_build`)  All your built documents will appera in the :bash:`_build`
directory.  

If not, let's have Regolith build the latex source file for the cv but without trying 
render it to PDF, 

.. code-block:: sh

    $ regolith build cv --no-pdf

The latex source is a text file and you can open it in a text editor.  You can
render it by opening a free account at http://overleaf.com starting a new blank
project, uploading the :bash:`<filename>.tex` and :bash:`<filename>.bib` files to
that project and hitting the :bash:`recompile` button.

Whether it builds on your computer or on overleaf, it should look something like

.. image:: ../_static/cv.pdf

If, for some reason, the publication list doesn't render 
correctly, try running the latex command again.  If you are going to
do much building with regolith it is definitely recommended to install latex on
your computer, such as MikTeX for windows (latex comes installed with many linux
systems.

What Next?
===========

You have not spent too much time building your database yet, but you
can already build a number of different things.  Try building your
resume (:bash:`$ regolith build resume`), your publication list 
(:bash:`$ regolith build publist`) and your presentation list
(:bash:`$ regolith build preslist`).  You can even build a web-page
for your group (:bash:`$ regolith build html`).  It will look pretty
ugly until we set it up properly with a nice template, but the conten
will be built from the databases.

To see everything you can build, type :bash:`$ regolith build --help`.
To build some of those things you will need more collections, for example,
:bash:`proposals` and :bash:`grants` collections






Tutorials
=========
.. toctree::
    :maxdepth: 1

    broker

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
     :maxdepth: 2

     commands/index