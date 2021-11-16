fs-to-mongo
========
This command is used to port collections from the filesystem to either a local
or remote mongo cluster on a specific database. The following codeblock can be
utilized as the body of a regolithrc.json file in the local directory adjacent
to a db directory containing json or yaml files. This specific setup is used to
export to a remote atlas cluster (as indicated by the +srv). In order to do so,
the text encapsulated by the <> brackets must be completed for your application.

This functionality relies on the subprocess calls to a locally running mongo
instance regardless of whether or not the user is importing to a local or remote
instance. This can be downloaded from the following link:
https://www.mongodb.com/try/download/community

.. code-block:: JSON
{"groupname": "Example Group Name",
 "databases": [
    "name": "<databasename>",
    "dst_url": "mongodb+srv://<username>:<password>@<clustername>.uc5ro.mongodb.net/<databasename>?w=majority",
    "url": "..",
    "public": false,
    "path": "db",
    "local": true}
   ]
}