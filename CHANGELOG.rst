====================
Regolith Change Log
====================

.. current developments

v0.6.2
====================



v0.6.1
====================



v0.6.0
====================

**Added:**

* Ability to utilize multiple backend clients (namely filesystem and mongo) for a single database
* an adder helper to add new expenses to the expenses collection
* adder helper for new reading list based on tags in the group citation database
* an adder helper to add presentations to the presentations collection
* an adder helper for adding a new projectum to the projecta collection.
   projecta are small bite-sized project quanta that typically will result in
   one manuscript.
* adder helper to add a new proposal to the proposals collection.
* adder helper that adds a new to-do task to the todos in people collection.
* Helper for listing grants
    * New function in dates.py to determine is something is current
* a builder for annual appraisals modelled on columbia SEAS appraisal
* a tool in tools in tools.py that will merge two collections, similar to chainDB but they collections are not public/private versions of the same collection but collections of different names.  Intitiall intended for proposals and grants so that when a proposal gets funded its info doesn't have to be copied over to the grant but can be dereferenced
* a convenience tool to tools.py that gets all the date items (begin_day, end_year, month, etc.) from an entry and returns them as a dict
* a bunch of bespoke filters to tools.py that return different things from different collections
* a function that takes regolith dates and returns the beginning and ending date from a document
* tests for functions in regolith.dates
* due date as command line arg for projecta adder helper
- A new builder for the experiment plan of beamtime based on the beamplan and beamtime database
 - Add pandas in the required packages
* bio_long field to people schema for longer bio's that are
   needed for cv's but not necessarily websites
* add --checklist functionality to the projecta adder that will create a checklist
   projectum for manuscript submissions.
* a new function collect_appts in tools that collects all appointments in a people database satisfying certain
      conditions or lying in a given period of time
* filter allowing user to list just current milestones in u_milestone
* publist builder now builds versions where the author is not bolded and a
   version where the acknowledgement is printed as well for DOE reporting purposes
* todo items in todo lists can now have tags added and be sorted by tags
* helper that marks a task as finished in todos of people collection.
* The --filter flag can now recursively search through a top level target attribute, which can be an object or a list, in order to more effectively search a record
* a helper for finishing projecta in the projecta collection.
* Flags to l_projecta to get projecta that finished within a date range
* New function in tools, fragment_retrieval, that returns a list of documents from a collection where the specified fragment is found in any of the given fields (similar to fuzzy_retrieval)
* a helper for listing filtered data from collections in the database.
* The get_dates function in tools.py can now take a prefix string when searching for dates
* a function grant_burn in tools.py that retrieves the burn of a grant given a collection of appointments
      for  a given interval of time
* New flag to l_projecta called --grp_by_lead that groups all projectums by their leads
* to tools a function to find all group members in a people db
* A finish argument to finish milestone and record the end datetime.
 * Multiple indices can be specified for the u_milestone helper.
* A new helper command for helpers which are like lightweight builders but do
   more than just build
* new function is_fully_appointed in tools.py (with tests in test_tools.py) that takes in a person dict and retrieves the person's appointments to check is the person is fully appointed for a given interval of time
* helper that lists all contacts corresponding to a name, institution, date, or note fragment
* milestones now handle a notes field in schema and all relevant helpers
* helper that lists all upcoming milestones from projecta
 * function to dates.py that fetches due_date from a dict and returns it as a
   datetime.date object
* a helper that lists progress by person from their projecta
* Helper that lists all the to-do tasks. Tasks are gathered from todos of people.yml and milestones.
* linkedin_url to schema of people
* a helper makeappointments that helps manage appointments on grants and study the burn of grants over time
* A validator called v_meetings that makes sure contents of previous group meetings are not empty
* A lister for the names of members of the group, either current or ever.
* The "regolith mongo-to-fs" command can now be used to port local and remote mongo backends to the filesystem
* Validation on all updates and insertion to mongo databases due to potential for lack of PR review
* get_dates function that will find years, months and days and/or dates in a document and
   return them as datetime date objects
* Add test for internalhtmlbuilder in test_builder.py
* functionality to l_projecta to find prums that either have no lead (lead is
   tbd) or are assigned to inactive people
* progress field in milestones in projecta collection
 * schema for the projecta collection
* release definition to the delivery milestone in the database
* publist builder will now build for a single group member if the ID is
   specified at the CLI
* tests for proposal and manual review builders
* All listers now support searching with the --filter and --keys flags
* reading list builder
 * function to tools that gets a reference from Crossref
* tutorial to allowed types in presentation schema
* a helper to build reading lists from a citations collection using tags
* an contact helper for adding/updating contacts to the contacts collection.
* a helper for adding/updating institutions to the institutions collection.
* An updater helper for updating log_urls of projectum
      in the projecta collection.
* a milestones helper for adding/updating milestones to the projecta collection.
* helper that updates a task in todos of people collection.
* properties to the schemas for the expenses, meeting, and projecta collections
Regolith mongo client can transfer database from filesystem and load data from mongo database. Regolith
builders can run on mongo backend.
* presentation lister now handles webinars
 * a_presentation helper now handles webinars
 * get_person_contact() a new tool in tools.py will return a person by looking
   in the people collection and the contacts collection
* 'webinar' as a boolean available. True if the presentation was a webinar.

**Changed:**

* cv now separates service and honors
* small tweaks to cv format to make it more appropriate for longer cvs as will 
   as shorter ones.
 * added presentations and former students to cv
* Beamplanbuilder includes the scan plan code in the report.

* Scanplan schemas changes from string to list of strings.

* Sample information is demonstrated in a list instead of a comma separated line.
* get_formatted_crossref_reference() in tools.py now returns None if the doi passed can't
   be found
 * internalhtmlbuilder now resolves and then prints the Journal Club DOI's
* is_current, is_before, is_after, has_started, has_finished, and is_between functions now use datetime objects
* u_contact now only requires institution when adding, but not when updating
 * u_contact can take an id as an optional argument
* get_dates now tolerates 'tbd' in a date field
* get_dates now returns None for all dates if it can't find any dates
* group_by_lead flag in l_projecta can now be used with other flags
* makeappointments helper will not look for an end-date when employment
    attribute 'permanent' is set to true
* Key value pair filter is now integrated with the other flags for listers
* l_members now prints emails of members in verbose mode
* The -v flag in l_projecta now produces a verbose output
* edited print message in is_fully_appointed function in tools.py
    * edited edge case logic in is_fully_appointed function in tools.py
    * removed superfluous help message from returned list in grant_burn function in tools.py
* merge_collections_all returns all of two collections, where items dererenced
   are merged
 * merge_collections_intersect returns just merged items that are dereferenced
 * merge_collections_superior returns all except the non-dereferenced items in
   the inferior collection.  e.g., if we are merging grants and proposals and we
   want all grants, augmented by information in the proposals that led to those
   grants, we use this.
* Cleaned code in l_projecta for more readable filtering
 * a_projectum so that it doesn't automatically prepend a year to the id of new
   projecta.
 * updated schema so it doesn't model id pattern with prepended date
* publist builder now makes a version of the publication list without the main
   author appearing in bold (_nobold), a version that is pandoc friendly (_pandoc)
   so it can be converted to MS word and other formats, and a version that also
   prints the acknowledgement statement along with the reference (in a slightly
   clunky fashion, _ackno) as well as the previously produced publication list.
* proposal review builder now accepts lists of institutions for multiple authors
* yaml-to-json now serializes datetime datetime and date objects
* reading list items are now sorted by date in reverse chronological order
* milestone lister updated so that it filters by person and based on milestone
   status

**Removed:**

* Old date functions from tools.py
* from preslist builder the method to find all group members in a people db
* old is_fully_loaded function in tools.py, which is replaced by the new is_fully_appointed function.
* removed mdy function from reimbursement builder, now using strftime() method.
* removed mdy function from coabuilder. It was not being used there.

**Fixed:**

* A common interface is being enforced on the backend clients (mongoclient.py and fsclient.py)
* modified reimbursement builder to handle new date (rather than day, month,
   year) format in expenses as well as old one
* fsclient.py dump_yaml function to ignore aliases
* test_helper.py so that it checks for changes to database collections
* bug in date_to_float removes extra zero in day float value
* cv dereferences institutions
* now using filter_presentations in preslist builder
* grants lister now returning correct dates
* bug in grp meeting builder so will build if previous Jclubs are missing
* l_members does not crash when organization not found in institutions
   collection
* bug that person in two groups doesn't iterate over their proposals correctly
   in current-pending
* Subprocess calls to mongo now printout the error message that would have gone to the stdout
* Testing mongo backend added for all helpers as well as a single doc validation tool test
* Bug in l_projecta helper that meant that specifying --current then didn't
   filter for other things
* current and pending now builds properly when there are multiple groups iterated
   over
* coabuilder now filters dates correctly
 * coabuilder finds institution when the person is a student and his/her most
   recent appointment item is in education and not employment
* get_dates now handles days, months and years expressed as strings
* dates now does not strip tbd and replace with None from all fields,
   only from fields containing date in the key
* publist will build if year in date is string, not int, in the collection
* get_dates function works with datetime objects and strings
Bugs in the old mongo client are fixed.



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




