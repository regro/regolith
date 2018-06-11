.. _commands:

=================
Regolith Commands
=================
Shell commands for regolith

.. code-block:: bash

	usage: regolith [-h]
	                {rc,add,ingest,store,app,grade,build,deploy,email,classlist,json-to-yaml,yaml-to-json,validate}
	                ...

	optional arguments:
	  -h, --help            show this help message and exit

	cmd:
	  {rc,add,ingest,store,app,grade,build,deploy,email,classlist,json-to-yaml,yaml-to-json,validate}
	    rc                  prints run control
	    add                 adds a record to a database and collection
	    ingest              ingest many records from a foreign resource into a
	                        database
	    store               stores a file into the appropriate storage location.
	    app                 starts up a flask app for inspecting and modifying
	                        regolith data.
	    grade               starts up a flask app for adding grades to the
	                        database.
	    build               builds various available targets
	    deploy              deploys what was built by regolith
	    email               automates emailing
	    classlist           updates classlist information from file
	    json-to-yaml        Converts files from JSON to YAML
	    yaml-to-json        Converts files from YAML to JSON
	    validate            Validates db



.. toctree::
    :maxdepth: 1

    add
    app
    build
    classlist
    deploy
    email
    grade
    ingest
    json-to-yaml
    rc
    store
    validate
    yaml-to-json