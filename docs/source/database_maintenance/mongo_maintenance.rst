Mongo Database Maintenance
==========================

Enabling Database Functionality
-----------------------------

| This section is for those who would like to maintain a MongoDB backend (local or remote). (note:
  if you are simply doing read-writes to an **existing remote mongo server** with **existing collections** via the
  helpers or gui, please skip)

| The first step to becoming a maintainer is by downloading the community edition of the mongodb server, along with the
  mongodb tools, from the mongodb website. These will allow you to

1. run mongo-related tests locally with Regolith, thus allowing you to update Regolith's mongo-interoperability with
   confidence,
2. run the "Regolith fs-to-mongo" command to move whole collections to your server and,
3. run the "Regolith mongo-to-fs" command to save collections from your server in the json format

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

| The second step is setting up a server (local or remote)

Setting Up a Server
-------------------

**LOCAL**

| Your local server is automatically running as a service on localhost if you have downloaded the community version of
  mongodb correctly. **Congratulations!**

| Accessing your local mongodb server **for administrative purposes** can be done simply by typing "mongo" into your
  terminal, which opens the mongodb shell. By default, you will have three databases present (admin, config, local).
  These are administrative databases that are only meant to be accessed by high access users. The immediately important
  commands are show and use. The important variables to immediately know are dbs, db, and collections. "dbs" is your
  list of databases. "db" is your current database, etc. The "use" command, followed by a string will create a database
  with the name of the provided string.

| Accessing your local mongodb server via Regolith for **non-administrative purposes such as helper or gui access** can
  be done by changing the 'url' key in your regolithrc.json file to 'localhost' and the 'backend' key to 'mongodb'

**REMOTE**

| Setting up a remote mongo server is most easily done with a DBaaS provider. Mongo itself provides a nice DBaaS
  known as Atlas, which provides plenty of free storage space for text-only collections. This process is straightforward
  and is explained on the Atlas website.

| The way to then access the remote server through Regolith is to click the "CONNECT" button on your cluster through the
  website GUI. Next, select "Connect to your application", followed by selecting python 3.6 or later options. The URL
  that you are presented with can be inserted into your regolithrc.json file under the 'URL' key.

| Note: user.json in your config folder can be utilized to fill in the url username and password by replacing them with
  'uname_from_config:pwd_from_config' in the URL, and adding your username and password to user.json as 'mongo_id' and
  'mongo_db_password'

Uploading Additional Collections to the Cluster
***********************************************

| When porting yaml or json files from our local filesystem to the mongo cluster, the regolithrc.json file must take a
  specific format. Follow the below steps in order to create a new regolithrc.json file and pass collections wholesale
  to mongo.

| Note: The database you pass the collections to does not have to exist. A new name will auto-create a new database.

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
5. Ensure that your user.json file contains a valid userID and password in the 'mongo_id' and 'mongo_db_password' keys
6. From the local directory, activate your regolith environment (by entering "conda activate <regolithEnvName>" in the terminal)
7. Still in the local directory, now with the regolith environment active, enter the following into the terminal "regolith fs-to-mongo"

Backing Up or Downloading the Database
**************************************

| Follow the steps in the "Uploading Additional Collections to the Cluster" section, but skip step 4, and in step 7 enter
  "regolith mongo-to-fs" in the terminal instead. The db directory will be where all of the collections from your
  database land.
