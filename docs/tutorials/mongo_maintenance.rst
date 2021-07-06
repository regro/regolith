Mongo Maintenance
=================

Enabling Maintenance Functionality
----------------------------------

| The first step to becoming a maintainer is by downloading the community edition of the mongodb server, along with the
  mongodb tools, from the mongodb website. These will allow you to run tests locally with regolith, thus allowing you to
  update regolith's mongo-interoperability with confidence. These will also allow you to run the Regolith fs-to-mongo and
  mongo-to-fs commands, as they utilize the mongodb tools that you will be downloading.

These downloads are a multistep process, so follow carefully

1. Go to https://docs.mongodb.com/manual/administration/install-community/ and download the community server as a
   service for your relevant operating system. At the time of writing, this is a link to version 4.4.6.

If you are a windows user, please see the additional notes below.

2. In order for all Regolith-Mongo functionality to work locally on windows, you must ensure that you have either
   installed the mongodb server as a service, or that you start the service before running mongo maintenance commands
   in Regolith.
3. For certain operating systems and methods of download, both the server and the tools will be downloaded
   simultaneously (macOS and Ubuntu at the time of writing). If that is not the case (windows users), be sure to also
   download the tools from the following link https://www.mongodb.com/try/download/database-tools?tck=docs_databasetools.
4. You will likely be provided an option to download "Compass". Compass is the desktop GUI application to interface
   visually with local and remote mongo servers. It doesn't hurt to have this as a maintainer, however, none of our current
   maintenance practices utilize it.
5. Windows users must go through the additional step of adding the mongo executables to their environment path variable
   manually. In order to do so, search "Path" in your windows search bar. You should be presented with an "Edit the System
   and Environment Variables" control panel link. After following this link, press "environment variables", "path" under
   user variables, "Edit..." under user variables, "new" in the resulting window, to add two new directories to the path
   variable. These directories will take the forms
   "C:\\Program Files\\MongoDB\\Server\\\<e.g. 4.4\>\\bin" and "C:\\Program Files\\MongoDB\\Tools\\\<e.g. 100\>\\bin"


Uploading Additional Collections to the Cluster
***********************************************

| When porting yaml or json files from our local filesystem to the mongo cluster, the regolithrc.json file must take a
  specific format. Follow the below steps in order to create a new regolithrc.json file and pass collections wholesale
  to mongo.

1. Create a directory called rg-db-mongo-port
2. In this directory, create the following folder structure (projecta.yml is inside of db as an example)

::

  +---db
  |       projecta.yml
  |
  \---local
          regolithrc.json

3. Structure your regolithrc.json file in the following way, with \<databaseName\> filled in with the name of the
   database on the cluster that you intend to upload the yaml files to. Note that the database name must be replaced
   both in the name and dst_url keys

::

    {"groupname": "Billinge Group",
     "databases": [
      {"name": "<databaseName>",
       "dst_url": "mongodb+srv://uname_from_config:pwd_from_config@<clusterName>.uc5ro.mongodb.net/<databaseName>?w=majority",
       "url": "..",
       "public": false,
       "path": "db",
       "local": true,
       "backend": "mongodb"}
       ]
    }

4. Add all of the collections that you would like to upload to mongo in the form of yaml or json files in the db directory
5. Ensure that your user.json file is complete as described in the "Regolith... just with MongoDB" section
6. From the local directory, activate your regolith environment (by entering "conda activate <regolithEnvName>" in the terminal)
7. Still in the local directory, now with the regolith environment active, enter the following into the terminal "regolith fs-to-mongo"

Backing Up or Downloading the Database
**************************************

| Follow the steps in the "Uploading Additional Collections to the Cluster" section, but skip step 4, and in step 7 enter
  "regolith mongo-to-fs" in the terminal instead. The db directory will be where all of the collections from your
  database land.
