====================
Regolith Change Log
====================

.. current developments

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
- add needed_dbs statement for quicker building
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
* bug so that needed_dbs results in only selected collections to be opened
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

* ``open`` uses explict 'utf-8' bindings (for windows users)
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
* Fixed bug in grad builder when the total wieght is zero.
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

* ``CVBuilder`` and ``ResumeBuilder`` builders now inheret from ``LatexBuilderBase``


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




