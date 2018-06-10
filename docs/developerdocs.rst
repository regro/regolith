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
(open source) code (yes you are allowed, but read the license (yes, read it))
and put it on your computer and
start messing around with it, and sometimes we do that.  But the
complicated structure of repos we set up is so that we don't just have
1000 versions of the code sitting on 1000 people's hard drives, all
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

This is how we do the regolith code, but it is also how you can maintain
good, clean databases, for your group.  So let's learn the steps.  Remember,
git is a pain (so the steps will seem complicated) but you can quickly get
used to it.  It is dealing with a complicated problem (many people working on
the same code base) which is why it has to be complicated.  But it is awesomely
powerful.  Believe me.  I ran a group software development projcet before
git and github was invented and it was a massive headache.

OK, let's go:

1. create an issue to fix:  On the motherlode GitHub website, click on "issues"
and then the "New Issue" button, give it a meaningful title and enough info
in the main section to capture the problem.  It is often good to mention what
the expected/desired behavior is and what the current behavior is.
1. Decide to fix an issue.  It could be the one you created, or help out by
fixing someone else's issue.
1. Make sure your local repo is up to date with the latest motherlode (remember,
other people are also working on the motherlode)

.. code-block:: sh

    $ git checkout master
    $ git rebase upstream master --ff-only

The first step is to ensure that you are updating your local master branch
(more on branches soon).  The second rebase command is a special way of merging
two branches.  Here you are merging your local master with the master branch
on the motherlode.  The ``--ff-only`` only lets this happen if there are no
conflicts.  If you have been following the steps in this document your local
master should never be conflicted with upstream master (because we are going
to be good about using branches)
1. OK, we will assume that the rebase worked so your local master is now the
same as the motherlode master.  Now you will create a branch to fix the issue
you want to fix.  Use one branch for each fix, however tiny it is.  You will
see why later.  Give the branch a name that is lower-case, maybe with underscores
between words, that succinctly captures the issue you fixing.  Let's say the
issue was "Fix typo in PI name" then:

.. code-block:: sh

    $ git checkout -b fix_pi_typo

The ``-b <branch_name>`` creates a new branch with name ``<branch_name>``
Your local repo is now on on the ``fix_pi_typo`` branch.  this should be clearly
indicated at the command line in your terminal.  Let's talk a bit about branches.
One branch per fix, but you can have many branches (and many fixes) on the go
at any time.  Each time you checkout a branch, all the files and directories on
your computer magically change to the way they looked the last time you worked
on that branch.  That can freak you out to begin with, because where did the other
files go that I still don't want to use?  Don't worry, you will get them back
when you check out that previous branch.
1. Now work on fixing that typo.  Open the right file (let's say its
``group.yml``), find the typo, fix it,
save the file and come back to the command line.

.. code-block:: sh

    $ git status
    $ git add group.yml
    $ git commit -m "FIX: fixing pi name typo"

git status is your friend.  It shows the status of the git repo (your local in
this case).   The other commands are explained in many places so you can read
about them.  BUT, make the commit comment good. It is one of the best ways of
finding stuff later from your commit history.  The ``FIX:`` is borrowed from
the famous Numpy standards.  Other tags are ``ENH`` for a new feature (enhancement),
``DOC`` for documentation fixes and so on.
1. We are satisfied with our fix.  Just to check we may want to run our test
suite and make sure that nothing is broken.  Move to the head directory of the
repo (this would be the regolith or rg-db-group folder) and type

.. code-block:: sh

    $ py.test

if you are using pytest test-rig (regolith is).   If your fix broke anything
then fix things up and recommit (or run the tests before committing, even better).
1. things are passing tests, so let's push this branch back up to our fork

.. code-block:: sh

    $ git fetch
    $ git rebase upstream master --ff-only
    $ git push -u origin fix_pi_typo

The first command just goes and checks all the repos our branch is linked to
on remote computers and checks if there are any updates.  The second command
grabs any changes that have happened to the motherlode
master branch.  hopefully there were no changes, or there are no conflicts between
any changes and changes you have made locally (this is more likely if your
branch has only small, localized changes, and hasn't been sitting around for a
long time!).  The ``-u`` in the second command links your local ``fix_pi_typo``
branch to a branch with the same name on your Fork.  If you type the -u this
linkage will be permanent and the next push can just be typed as ``git push``.

The --ff-only is important.  It kills the rebase if there are ny conflicts
because the upstream master and your local branch have diverged in a that can't
be reconciled without your intervention.  In this case we have assumed that
the rebase worked and so we push our nice shiny
jewels to our fork with the ``git push`` command so that we can issue a pull
request and share them with the world.  We will cover hte later the case that
the rebase fails.

Let's review where we are.  On the motherlode there is a master branch that
contains the motherlode code.  All the code there is polished and checked, but
multiple people are contributing code to it.  There is also a "master" branch
on our fork,
which is actually the version of the motherlode masterbranch when we forked it,
maybe months ago, and not the same as the current version there.
There is also a "master" branch on our local copy of the repo,
which, as it happens, is also the months old version.  Then we have a ``fix_pi_typo`` branch
on our local computer which contains a copy of the current version of the
motherlode masterbranch (because we fetched and then rebased our branch onto it).
This branch also has our new shiny jewels that haven't been shared with the
world yet, only we know about it right now.  Finally, because we pushed with
the ``-u``, there is a ``fix_pi_typo`` branch on our Fork on GitHub, which,
currently, is up to date with our local ``fix_pi_typo``.  Now, to complete the
loop, we want our shiny jewels to be loaded into the mothelode.  In this case,
we don't want to create a ``fix_pi_typo`` on the motherlode, we want to merge
our shiny jewels into the motherlode ``master`` branch so when the next lucky
person who downloads that code base, just like we did, will have our shiny jewels
along with the rest.

So let's create our PR, our pull-request, and reveal our work to the world.
[instructions here]

When the PR is created, the keepers-of-the-motherlode are notified by GitHub
that a PR has been issued and they go and review the code.  They might say
"oh my gosh, there was a typo in the pi name?  How embarrassing!".  But they
notice that in the database entry there is a missing comma, so they post a
comment to that effect, and you get notified that your PR was reviewed.  You
need to fix that comment.  In the mean-time you have been working on other things,
or just to make sure in any case, the first thing you do is to checkout your
fix branch.

.. code-block:: sh

    $ git checkout fix_pi_typo

Then you open the group.yml file in your editor and add that comma, you save
the file and exit, then

.. code-block:: sh

    $ git status
    $ git commit -am "FIX: adding missing comma to pi entry"
    $ git push

You didn't need the git status, but it is always a good sanity check


