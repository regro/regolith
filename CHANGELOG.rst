=============
Release notes
=============

.. current developments

0.9.1
=====

**Fixed:**

* incorrectly named test for fs_to_mongo
* Rearrange Regolith package to new Billingegroup package standards
* all py files linted with black
* change name and then fix tests for function that formats awards and honors



0.9.0
=====

**Added:**

* new helper_connect app added that will connect the databases then return back a prompt to input helper commands for
  faster response
* funds_available to grants schema
* In annual activity, grants are automatically considered as projects unless specified otherwise

**Changed:**

* Grants lister helper now lists funding available when it is available
* exemplars moved to a json file
* lists of commands now imported from commands.py

**Fixed:**

* Open source title not printed when there are no OSS projects in activity builder
* gooey install moved to new pip.txt file in requirements since it doesn't install the correct version from conda-forge



v0.8.2
====================



v0.8.1
====================



v0.8.0
====================

**Added:**

* the option to specify a different database for the expense and presentation
  items when running a_presentation.
* scripts (profile_regolith and profile_helper_gui) that run regolith and helper_gui with the python cProfiler. Used for debugging and code development.
* universally unique IDs added to all tasks, and now listed by todo lister
* milestone lister now prints the uuids of the milestones
* additional tests for c+p, annual-activity and grant-report builders
* repo_info_complete in tools to check the existence of remote repositories before operating on them
 * token_info_complete in tools to check for the existence of the user's private API authentication token
 * create_repo in tools to create a repository in a given remote repository
 * functionality to presentation helper that creates a repo by calling on create_repo function in tools when no_talk_repo box is not checked
 * no_repo box/option added to presentation helper gui
* no_in_cv option for employment entries that they don't appear in cv's and resumes
* get_appointments() function
* effort reporting report shows each person's loadings by grant by month over a fixed period
* new functionality that allows general kwargs to be passed to builders from the command line
* Builder for building formal letters with To/From/Subject etc. fields
* presentation_url field to presentation in presentations
 * functionality to presentation adder to allow the presentation url to be added
* publist can be built specifying a facility where the measurements were made
* supplementary_info_urls field to citations and projecta
* u_milesone now x's out all the unfinished todo items when it "finishes" a milestone
* u_milestone uses "--milestone_uuid" option to select which milestone to update
* all milestones now have uuids
* Add the command "regolith --version" to print the version number.

**Changed:**

* default milestone added by a_projectum is now more useful. It duplicates the kickoff meeting
* added empty notes field and currency type USD to template expenses in
  a_expenses and a_presentation

* None
* Better debugging in get_dates() when date information is missing by printing the id of the offending document
* Order of tests in helper_tests so all the updaters are at the end
* grants lister prints in columns and is grouped by the unit that administers the grant
* amounts in attestations are limited to 2-sig-figs
* Order of CLI args in u_milestone for greater ease of use
* prum finisher now adds end-dates to all milestones.  If they have an end-date
   it leaves the date as is, otherwise it adds the prum end-date
* Abstract lister now outputs the meeting name and basic information about the meeting of the presentation
* Abstract lister now lists in date order
* grant report builder updated to run without needing to specify report
  beginning and ending dates.  Default dates are taken as being the start
  date of the grant and today's date if not specified at runtime.
* prum lister now lists paused projecta as well as current as default behavior.
   selecting --current gives just active prums
 * prum lister now appends the prum status even in non-verbose mode
* Template prum now has better advice for how to fill it when made by a_projectum
* reading list builder now builds reading lists from the citations database by
   using the tags field for each paper
 * tests of tex and html files now compare outputs line by line
   and ignore variables paths that have proven to be unstable
* Standardized CLI option names by replacing the underscore with a hyphen in the
   following: --end_date, --begin_-date, --submitted_date, --no_cal, --due_date,
   --group_members, --other_agencies, --months_academic, --months_summer,
   --assigned_to, --assigned_by, --loc_inst, --kv_filter, --return_fields,
   --helper_help, --school_aka, --school_name, --school-id, --dept_aka, --dept_name,
   --dept_id, --estimated_duration.
* Reformatted printing of todos to make the order clearer
* "--projectum_id" has been changed from a required arg to an optional arg
* u_milestone uses "--projectum_id" option to add a new milestone to a prum
* Updater helpers now only open the specified database, not all the databases in rc.databases.  If they don't find the collection in that database they will report a failure to update.

**Deprecated:**

* None


**Removed:**

* None
* todo lister no longer lists milestones from projecta.  this will be handled differently moving forward
* the u_milestone functionality that lists a prum's milestones has been removed
* "--index", "--verbose", and "--current" optional args have been removed

**Fixed:**

* load all collections bug introduced accidentally when working on mongo backend
* None
* monthly loadings now handles edge cases better
* broken error message for missing institution in dereference_institution function
* dereference_institutions will always return a department now
* fixed typo in postdoc advisee getter
 * date handling for end-dates of current students/postdocs
* updated to raw strings places where they should be to propagate escaped special
   characters, e.g., latex_safe
 * fixed formatting UserWarnings in makeappointments helper
* remove bug that wrong list item taken from calendar.daterange() was being
   used in l_currentappointments helper
* manuscript review new correctly prints freewrite field
* prum lister now correctly finds due_date
* bug in adder that builds reading lists from tags in citations making duplicate entries
* Changed how the reading-list builder fetches the references from Crossref so that it only fetches each needed reference once.
* xonsh input_hooks now explicitly has execer=None instead of blank parens to satisfy xonsh deprecation warning
* publist builder now produces bib files before filtering so we don't accidentally build a publist with an incomplete
  bib file


**Security:**

* None




v0.5.1
====================

**Added:**

* code to give more feedback to the user when the builder fails due to a database error
- regolith classlist can now read csv files in Columbia University format
 - classlist register now checks whether a given file actually exists
- merge_collections to tools.py.  merges two collections
- tests for manuscript review builder
* function for finding gaps and overlaps in lists of date-ranges
* utf8 support in all current latex builder templates
- function to dates that returns months as strings with leading zero where required
 - function to dates that returns days as strings with leading zero where required
* ability to build publists with specified date ranges and filtered by grant
 * tbd is now a valid month, returning 1 as an integer
 * begin and end day now allowed in employment and education

**Changed:**

* unsegregated expense can now tolerate "tbd".  This allows users to put a
   placeholder entry when the exact amount is not known, and then find it easily
   later.  Code flags all tbd entries at build time, but doesn't crash.
- removed remote.rc logic from database.xsh
- current and pending builder extended to build c+p from merged proposal and grants collections
 - added filter for cppflag so you can have current grants that don't appear in the current and pending form by setting cppflag to false in the db
- add needed_colls statement for quicker building
- moved has_started, has_finished and is_current to tools.py
* Load only dbs needed for builder, if builder declares which dbs it needs
* reimbursement builder requires a person to be specified on the command line
   to run due to the extreme slowness of openpyxl
- User supplied schemas now handles new keys in regolith validate.

**Fixed:**

* valueschema -> valuesrules in schema as valueschema deprecated in cerberus
- cpbuilder does name comparison on fuzzy-searched name for standardization
 - cpbuilder includes initials when it is a multi-pi grant
 - filter_grants in tools.py bug fixed that incorrectly reassigns team members
 - updated docstring on filter_grants to make it clearer
- fix indenting of the editor eyes only block
* import from collections.abc not collections
* months can now be expressed as ints or strings as per the schema
* fix bug introduced in Jinja2 v2.11 that doesn't recognize conditional text
   in the import
* bug so that needed_colls results in only selected collections to be opened
* publist will now build even if person email and employment are missing



v0.5.0
====================

**Added:**

* builders can now take --from and --to command-line args to specify date range
* added banner to groups schema, which is an image for website banner
None

* Google profile URL to people schema
* Research Focus Areas to people schema
* status to employment which will be selected from a list for sorting on the
  website
* filters in ``regolith.tools`` that return true if a given date is since or before or
   between other dates
* Add phone and address to CV and Resume if available
- builder for post-doc ad
- a builder for proposal reviews.  Currently tuned for doe-bes and nsf-dmr
- builder for writing referee reports on manuscripts
* Make bib for entire group
- contacts to schema.py, a lighter type of person

**Changed:**

- builder now takes grant from grant field in expense and not by recursing
   into project
 - if payee is direct_billed, builder will not build a reimbursement form
* ``all_documents`` now defaults to a deepcopy to prevent unintended mutation
* institutions schema to add street and make conditionals work better
* All months can now be integers or strings in the schemas
* Make a ``.bat`` file in scripts, which should help on windows
* now builds just accepted talks by default, not declined or pending
- proposals schema in schema.py to include fields for building current and
   pending report forms
* Use ``xonsh.lib.os.rmtree`` in ``conftest.py`` rather that building our own.
  The xonsh version is expected to do a better job on windows.

**Removed:**

None
 - MTN: removed unused block from fuzzy_logic
 - MTN: nicer handling of non-list objects in fuzzy_logic

**Fixed:**

- BUG: total amount now reproduces correctly in grants section
 - BUG: account numbers not showing up in built reimbursement form
* Made the example current grant go to 2025 rather than 2018
* FIX: tests to run on windows OS by removing
   removed directory paths
* Makes sure some URLs in CV builder are also latex safe.
* correct spacing after date when it is a single day event
* Don't want to use latex_safe when we need the latex formatting
* Cast to string on way into ``latex_safe``
- BUG: ints now handled the same as strings (appended) in fuzzy_logic
 - BUG: now passes gtx as a list to fuzzy_logic not as a generator



v0.4.0
====================

**Added:**

* Optional ``static_source`` key in the rc for the html build.


**Changed:**

* institution dereference is done by ``regolith.tools.dereference_institution`` function
* HTML pages dereference institutions
* ``person.html`` allows for authors or editors and hides publications in details
* ``root_index.html`` allows for banner to be speced in ``groups`` collection
* ``regolith.builders.CVBuilder`` now dereferences institutions/organizations
  for employers and education
* ``regolith.builders.CVBuilder`` deepcopies each person so we don't modify
  the records during dereference
* ``regolith.tools.latex_safe`` wraps URLs in ``\url{}``
* ``regolith.builders.basebuilder.LatexBuilderBase`` runs ``pdflatex`` last
  if running on windows, rather than ``latex`` then ``dvipdf``
* Order yaml collections by key before dump for deterministic changes in collection order (make git more sane)


**Fixed:**

* Properly handle authors and editors set in ``regolith.tools.filter_publications``
* ``regolith.tools.fuzzy_retrieval`` properly handles null values
* education and employment subschemas for people are now just lists
* ``regolith.builders.BuilderBase`` uses ``latex_safe`` from ``regolith.tools``
* wrap `dbdir` in `@()` so xonsh does the right thing




v0.3.1
====================

**Added:**

* Schema for expenses tracking
* builder for Columbia reimbursement forms


**Changed:**

* ``open`` uses explicit 'utf-8' bindings (for windows users)
* Allow education to be ongoing
* Allow begin and end years for service
* Make employment optional


**Fixed:**

* Build presentation PDFs when running in normal operation
* ``regolith.database.load_git_database`` checks branch gracefully
* ``regolith.tools.document_by_value`` doesn't splay address incorrectly




v0.3.0
====================

**Added:**

* option for fuzzy_retrieval to be case insensitive
* ``regolith.broker.Broker`` for interfacing with dbs and stores from python
* ``regolith.builders.figurebuilder`` for including files from the store in
  tex documents
* ``regolith.database.open_dbs`` to open the databases without closing
* ``validate`` takes in optional ``--collection`` kwarg to restrict
  validation to a single collection
* ORCID ID in people schema
* Added presentations schema and exemplar

* Added institutions schema and exemplar

* Added presentation list builder
* number_suffix function to tools, returns the suffice to turn numbers into adjectives
* Method to find all group members from a given group
* a stylers.py module
* a function that puts strings into sentence case but preserving capitalization
  of text in braces
* User configuration file handling for adding keys to the ``regolithrc.json``
  globally


**Changed:**

* added aka to groups schema
* Docs for collections fully auto generate (don't need to edit the index)

* ``zip`` and ``state`` only apply to ``USA`` institutions
* added group item in people schema
* ``KeyError`` for ``ChainDB`` now prints the offending key
None

* preslist now includes end-dates when meeting is longer than one day
* Builder for making presentation lists now builds lists for all group members
* Departments and schools in institutions are now dictionaries
* Preslist builder now puts titles in sentence case
* Use ``xonsh`` standard lib subprocess and os


**Fixed:**

* ``validate`` exits with error code 1 if there are bad records
* Preslist crash when institution had no department

* Departments and schools in institutions now use valueschema so they can have
  unknown keys but validated values




v0.2.0
====================

**Added:**

* ``CPBuilder`` for building current and pending support reports

* ``initials`` field to ``people`` document

* ``person_months_academic``, ``person_months_summer``, and ``scope`` to
  ``grant`` document

* ``fuzzy_retrieval`` tool for getting documents based off of multiple
  potential fields (eg. ``name`` and ``aka`` for searching people)
* Tests for the exemplars
* Group collection for tracking research group information

* ``document_by_value`` tool for getting a document by it's value

* ``bibtexparser`` to test deps
* Builder integration tests

* Option for not making PDFs during the build process
  (for PDF building builders)
* Added presentations schema and exemplar
* Second exemplars for ``grants`` and ``proposals``
* ``bootstrap_builders`` for generating the outputs to test the builders
  against
* publist tex file to tests


**Changed:**

* moved builders into ``builders`` folder
* ``group`` collection to ``groups`` collection
* Use the position sorter to enumerate the possible positions in the schema
* ``base.html`` and ``index.html`` for webpages are auto-generated (if not
  present)

* test against ``html`` in addition to other builders


**Fixed:**

* Pin to cerberus 1.1 in requirements. 1.2 causing testing problems.
* Fixed error that anded authors and editors
* Error in ``setup.py`` which caused builders to not be found

* Error in ``BaseBuilder`` which caused it to look in the wrong spot for
  templates
* Fixed bug in grad builder when the total weight is zero.
* Actually use ``ChainedDB`` when working with the DBs

* Error in ``ChainedDB`` which caused bad keys to return with ``None``




v0.1.11
====================

**Fixed:**

* Local DBs were not being loaded properly




v0.1.10
====================

**Added:**

* Regolith commands can run using a local db rather than a remote
* ``LatexBuilderBase`` a base class for building latex documents
* Users can override keys in each collection's schema via the RC
* Command for validating the combined database ``regolith validate``


**Changed:**

* ``CVBuilder`` and ``ResumeBuilder`` builders now inherit from ``LatexBuilderBase``


**Fixed:**

* Use get syntax with ``filter_publications`` in case author not in dict
* If a collection is not in the schema it is auto valid




v0.1.9
====================

**Fixed:**

* ``all_documents`` now returns the values of an empty dict if the collection
  doesn't exist




v0.1.8
====================

**Added:**

* Database clients now merge collections across databases so records across
  public and private databases can be put together. This is in
  ``client.chained_db``.

* Blacklist for db files (eg. ``travis.yml``) the default (if no blacklist is
  specified in the ``rc`` is to blacklist ``['.travis.yml', '.travis.yaml']``
* Schemas and exemplars for the collections.
  Database entries are checked against the schema, making sure that all the
  required fields are filled and the values are the same type(s) listed in the
  schema. The schema also includes descriptions of the data to be included.
  The exemplars are examples which have all the specified fields and are
  used to check the validation.
* Docs auto generate for collections (if they were documented in the schema).


**Changed:**

* ``all_docs_from_collection`` use the ``chained_db`` to pull from all dbs at
  once. This is a breaking API change for ``rc.client.all_documents``
* App now validates incoming data against schema


**Deprecated:**

* Mongo database support is being deprecated (no ``chained_db`` support)


**Fixed:**

* Properly implemented the classlist ``replace`` operation.
* Fixed issue with classlist insertions using Mongo-style API
  (deprecated).
* Properly filter on course ids when emailing.
* ``fsclient`` dbs explicitly load 'utf-8' files, which fixes an issue on
  Windows




v0.1.7
====================

**Added:**

* ``BuilderBase`` Class for builders
* Logo to docs
* Filesystem-based client may now read from YAML files, in addition to JSON.
  Each collection can be in either JSON or YAML.


**Changed:**

* Refactored builders to use base class


**Fixed:**

* Fixed issue with CV builder not filtering grants properly.
* Fixed bug with ``super`` not being called in the HTML builder.




v0.1.6
====================

**Added:**

* Use Rever's whitespace parsing
* Fix template news




v0.1.5
====================

**Added:**

* Rever release tool
* Interactive session support
* run better release




v0.1.4
====================

**Added:**

* ``collabs`` field in db for collaborators
* ``active`` field in db for current collaborators/group members


**Changed:**

* People page only shows current members, former members on Former Members page
