.. _commands:

=================
Regolith Commands
=================
Shell commands for regolith

.. code-block:: bash

	usage: regolith [-h] [--version]
	                {helper,rc,add,ingest,store,app,grade,build,deploy,email,classlist,json-to-yaml,yaml-to-json,mongo-to-fs,fs-to-mongo,validate}
	                ...

	options:
	  -h, --help            show this help message and exit
	  --version

	cmd:
	  {helper,rc,add,ingest,store,app,grade,build,deploy,email,classlist,json-to-yaml,yaml-to-json,mongo-to-fs,fs-to-mongo,validate}
	    helper              runs an available helper target
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
	    mongo-to-fs         Backup database from mongodb to filesystem as json.
	                        The database will be imported to the destination
	                        specified by the 'database':'dst_url' key. For this to
	                        work, ensure that the database is included in the
	                        dst_url, and that local is set to true.
	    fs-to-mongo         Import database from filesystem to mongodb. By
	                        default, the database will be import to the local
	                        mongodb. The database can also be imported to the
	                        destination specified by the 'database':'dst_url' key.
	                        For this to work, ensure that the database is included
	                        in the dst_url, and that local is set to true.
	    validate            Validates db



.. toctree::
    :maxdepth: 1

    add
    app
    build
    classlist
    deploy
    email
    fs-to-mongo
    grade
    helper
    ingest
    json-to-yaml
    mongo-to-fs
    rc
    store
    validate
    yaml-to-json
