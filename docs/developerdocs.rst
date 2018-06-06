Contributor Docs
================
Here we will give tips and tricks for working with regolith to build
reports and other useful things.

* The basic git workflow
* building builders

Basic Git Workflow
==================
Git is a pain, but awesomely powerful.  There is a lot of git
dccumentation on the web, so plenty to go and read and we don't
have to reproduce it here.  But these are steps and the commands that
you will follow for working with regolith and regolith databases.

The basic workflow is that there exists:
 1. Archival, pristine, clean, authoritative, curated form of the
database/code.  This is the main repository on GitHub.  For the code it is
regro/regolith, for the databases it will be <your-group-name>/rg-db-group
and so on (there will also be rg-db-private and rg-db-public dbs). Things
are only allowed into this place if they are checked and double-checked
and then approved.  Let's call this the motherlode.
 1. Your online copy of this repo.  This is called your Fork.  It will
be on GitHub but it will have a name like <your_GitHub_username>/regolith
or <your_GitHub_username>/rg-db-group.  You make this repo, and
permanently link it to the motherlode, by clicking the `Fork` button on
the motherlode website on GitHub.  You can do anything here because you
own it.  You can't break anything on the motherlode so don't worry.
 1. Your local copy of the repo.  This is on your local computer and
is your sandbox.  It is where you do all your work.  This is linked
to your Fork on GitHub so when you have changes that you like and
want to have a backed-up and archived remotely you can push them up
to your Fork and they will be sitting there in the cloud.

OK, that's the basic structure of things.  Now, you can "take" someone's
(open source) code (yes you are allowed) and put it on your computer and
start messing around with it, and sometimes we do that.  But the
complicated structure of things we set up is so that we don't just have
1000 versions of the code sitting on 1000 people's hard drive, all
different from each other, but when we do something good, we have the
opportunity to share it back to the community so that they can use that
neat thing you just did.  The way this works is that you push your nice
modification (let's call it your shiny jewel) up to your Fork, and then
you can send a request to the keepers-of-the-motherlode to pull your
shiny jewel into the motherlode so that everyone in the community can
then use it.  This is called a Pull Request or PR.  Then there is a
process of discussion and commentary that takes place.  You will be
asked to make changes to your code, and do things to ensure that it
meets the standards of code quality of the stuff in the motherlode,
and this goes on for some time until everyone is happy, then your
shiny jewel is pulled into the motherlode, and you just made your
(first?) contribution to the community supported open source stack.
Congrats!
