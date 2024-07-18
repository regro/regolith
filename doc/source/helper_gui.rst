helper_gui
==========
Regolith helpers can add to, list from, or update existing collections in your databases. While helpers can be accessed through command line/terminal, the Helper gui is a more comfortable and accessible way to use them.

As with regular regolith, `helper_gui`  must be run from a directory containing a regolithrc.json file and it will use the config parameters it finds in there.  To use the gui, navigate to such a directory and type `regolith_helper`, e.g.,

.. code-block:: sh

    $ cd path/to/database/local
    $ helper_gui

Layout
======

.. image:: https://github.com/regro/regolith/blob/master/docs/helper_gui_images/layout.png
    :alt: Layout image
    :width: 600
    :align: center

The sidebar on the left hand side contains the available helpers, and the right hand side contains the required and optional arguments for each of the helpers.

Examples
========

There are three main types of helpers:

* Adders (start with a_),
* Listers (start with l_, ‘lister’ is included),
* Updaters (start with u_),

Other helpers are:

* Finishers (start with f_),
* Validators (start with v_),

As well as a few specialized ones such as
*makeappointments*


Here we pick representative helpers and discuss how to use the gui for each one.

The gui is pretty self explanatory in general.

* First select the helper that you want to use in the left hand column.
* Fields then appear on the right of the gui with all of the required and optional arguments for the selected helper.
* After filling in the required fields, as well as any desired optional fields, press start.
* The helper will then be run in the same way as it would if run from the command line.
* The output from the helper will appear in the status field
* To run another helper hit `Edit` and start over
* To rerun the same helper with the same inputs, hit `restart`
* You can leave the helper gui running indefinitely and use it whenever you want.  However, to close it hit `close` or click the red X.

l_members
---------

l_members will list group members from the people collection.   l_members doesn’t have any required fields, and if no optional arguments are selected, it will list all the group members in the database regardless of status.

.. image:: https://github.com/regro/regolith/blob/master/docs/helper_gui_images/l_members.png
    :alt: l_members image
    :width: 600
    :align: center

A short description is given for each entry.    The other optional arguments are quite self explanatory.

The *Verbose*  radio button in all the helpers will give more information in the output.

All helpers also have the **filter** and **keys** fields that allow filtering for a particular value on any top level field.  If the filter is satisfied the helper will return the value of the keys given in the keys field.  If the **keys** field is left blank just the id’s of the documents that satisfy the filter are returned.

For example,  to get the honors of all the people that contain "Andrew" in the "name" fields you would put `name Andrew` in the filter field and `honors` in the filter field.   Multiple filters can be specified and use the AND logic, so typing `aka andrew bio columbia` will find all people with andrew in the list of aka’s who also have Columbia somewhere in their bio.

Putting `name avatar` in the keys field will return the values of the `name` and the `avatar` field for the documents that satisfy the filter.   The filter field must contain pairs of words (for `key value`) but as in the example, multiple pairs may be specified.


a_projectum
-----------

This helper will add a new projectum (i.e., mini-project) to the projecta collection.

.. image:: https://github.com/regro/regolith/blob/master/docs/helper_gui_images/a_projectum.png
    :alt: a_projectum image
    :width: 600
    :align: center

The required fields are name and lead.

The `description` is a string and does not need to be enclosed in quotes in the gui (it does need to be in quotes on the command line).

For entries that take a list of entries, simply type in entries separated by spaces.  You may use quotation marks if a list entry  contains spaces.  The `collaborators` and `group_members` fields take IDs for entries linked to people that can be found in the `contacts` and `people` collections, respectively, e.g., sbillinge.

For due-date you may type it in ISO format (e.g. 2021-07-23) or select the data using the built int date selector.

A special kind of projectum is a paper submission checklist and selecting this radio button will generate one of these and add it to the collection.

u_logurl
--------

u_logurl can be used to update the log url for any projectum in the projecta collection.

.. image:: https://github.com/regro/regolith/blob/master/docs/helper_gui_images/u_logurl.png
    :alt: u_logurl image
    :width: 600
    :align: center


database field
==============

For adders and updaters, the helper needs to know which database the new/updated entry should be added to.  If the *database* field is left blank, the first database in the regolithrc.json file will be selected.  However, the name of any database that is in the regolithrc.json can be entered in this *database* field.  For example, if you run the helper gui from a database called rg-db-private, which contains private information visible only to yourself, but you want to update an entry and have it visible to the entire world, and you have a public database called `rg-db-public` listed in the regolithrc.json, then you would type `rg-db-public` (or whatever is in the name field of the desired database in regolithrc.json).

The *date* field is rarely used, as a default of today’s date is taken.  The contents of this field is generally used for testing.

Workflow
=======
This u_milestone helper exemplifies an important pattern in a number of the helpers.  The workflow goes as follows:

#. Type a fragment of the projectum id that you remember

    .. image:: https://github.com/regro/regolith/blob/master/docs/helper_gui_images/workflow1.png
        :alt: workflow1 image
        :width: 400
#. Hit start
#. The helper will return a list of all projecta that contain that fragment

    .. image:: https://github.com/regro/regolith/blob/master/docs/helper_gui_images/workflow3.png
        :alt: workflow3 image
        :width: 400
#. Note the full id of in your target projectum
#. Click edit to get back to the front page
#. Now knowing the full id of your target projectum, type it in the projectum_id field

    .. image:: https://github.com/regro/regolith/blob/master/docs/helper_gui_images/workflow6.png
        :alt: workflow6 image
        :width: 400
#. Click start again
#. The helper will return a numbered list of all milestones in for that projectum

    .. image:: https://github.com/regro/regolith/blob/master/docs/helper_gui_images/workflow8.png
        :alt: workflow8 image
        :width: 400
#. Without changing the entry in the id field, add the number in the list of your target milestone
#. Add any edits you would like to make to the milestone via the other fields

    .. image:: https://github.com/regro/regolith/blob/master/docs/helper_gui_images/workflow10.png
        :alt: workflow10 image
        :width: 400
#. Click start again
#. The correct entry will get updated and a message returned that verifies success

    .. image:: https://github.com/regro/regolith/blob/master/docs/helper_gui_images/workflow12.png
        :alt: workflow12 image
        :width: 400
Note that unless you specify the right database in the *database* field the update will be inserted in the default database which may, or may not, contain the rest of the projectum information.  This can be confusing until you get the hang of it.
