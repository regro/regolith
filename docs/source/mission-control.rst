---------------
Mission Control
---------------

Mission control is a way of running a research group from a document rather
than from a form. Each person has one markdown file, laid out to follow a
meeting: what are your projects, what did we agree for this period, what did
you plan for this week. People type into it; regolith reads it back into the
database and writes it out again. Nobody has to learn the command line to use
it, and nothing anybody types is lost to a build.

The database is the source of truth. The document is a view of it that can be
read back, so the same projects and goals feed the listers and the reports.

The three collections
=====================

Three collections hold it, one per level:

``mc_projects``
    Something somebody is responsible for, with a lead, a deliverable and the
    grants that pay for it. The top level.

``mc_goals``
    Something to accomplish in a period, belonging to a project. What the
    milestones of a projectum used to be.

``mc_tasks``
    Something actionable in a week, belonging to a goal. A task that belongs to
    no goal is a todo, which is a separate thing and stays separate.

The numbering people already use says which is which: project ``1``, its goal
``1.2``, that goal's task ``1.2.1``.

The document
============

One file per person, named for their first name, plus ``unassigned.md`` for the
projects nobody leads yet. They are written to ``mission_control_dir`` from the
run control, which is usually a shared folder such as Box so that the files can
be opened from anywhere.

.. code-block:: markdown

    # Mission control — Pei Liu

    ## Projects

    1. **Nanoparticle structure from the PDF**  ^pl-nanoparticle-pdf

       deliverable: submit the paper to Acta Cryst A

       with: sbillinge, ascopatz

       Recovering nanoparticle structure from the atomic pair distribution
       function.

    2. **Automated Rietveld refinement**  ^pl-automated-rietveld

    ## Goals — 2026fall

    - 1.1  Draft the methods section  ^a8s8ec
    - 1.2  Get the fits converging on the test set  ^dab3ap  (carried since 2026summer)
    - 2.1  ~~Benchmark against GSAS-II~~  ^i57pvc  (finished 2026-09-11)

    ## Week of 2026-09-14

    - [ ] 1.2.1  Re-run the fits with the new background model  ^66e5ty
      - [x] ~~Check the Qmax cutoff~~  ^4mynvu
      - [ ] Re-integrate the images  ^bfvvj6
    - [x] 1.1.1  ~~Send Simon the convergence plot~~  ^uxah3a

    ## On-deck

    - 2.2  Port the solver to the GPU  ^gpu111

    ## Wishlist

    - A tutorial notebook  ^tut222
      - [ ] Pick a dataset  ^pk3n2d

    ## Archive

    - ~~The 2019 result, reproduced~~  (finished 2026-06-30)  ^pl-reproduce-2019

    ### Goals — 2026summer

    - 1.2  ~~Get the fits converging on the test set~~  ^dab3ap  (→ rolled to 2026fall)

Reading it top to bottom:

**Projects** are numbered, bold, one per line. The indented lines under a
project are optional: ``deliverable:`` says what it produces, ``with:`` lists
who is on it, and any other prose is what the project is about, for the
project report.

**Goals** are a bulleted list under ``## Goals — <period>``. The number in
front says which project a goal is of: ``2.1`` is the first goal of project
``2``. A period is a year and a name, ``2026fall``; the names and dates are the
group's own, set by ``mission_control_periods``. A goal that was set in an
earlier period says so in the note at the end.

**Weeks** hold the tasks, one section per week, most recent first, with a box
in front of each. The number says which goal a task is of: ``1.2.1`` is the
first task of goal ``1.2``. A task indented under another is a piece of it and
carries no number.

**On-deck** and **Wishlist** hold goals that are not this period's work. A goal
here need not have a number yet: it is an idea that nobody has made a project
of. A breakdown can be written under it, indented, with boxes.

**Archive** is written from the database and not read back. Finished projects
are one struck line each, and under them the goals of each past period, struck
through if they finished or rolled on.

What you type, and what regolith types
======================================

The rule that makes the round trip safe is that no field is written by both
sides. The document owns the words, the boxes, the strikes, the dates and
which section a thing is in. The database owns the ids, who leads a project,
who is on it, and which grants pay for it.

You type:

- **Words.** Change the text of anything, add a line anywhere a list is, write
  a paragraph under a project.
- **A tick** ``[x]`` or **a strike** ``~~like this~~`` to finish something.
  Either does it; the strike is believed when they disagree, since the box is
  the one that gets forgotten. A struck project is finished, and goes to the
  archive on the next build with everything under it.
- **A move.** Drag a goal from Goals to On-deck to hold it, and back to take it
  up again. Move a task to another week to roll it. Reorder lines to say what
  matters most: a build keeps the order you chose.
- **A new line.** A goal needs a number saying which project it is of, and a
  task at the top level needs one saying which goal. A sub task is just
  indented under its task. A project needs its number and its name in bold.
  Nothing else: the id is minted when the document is read.
- **A deletion.** Take a line out and its record is marked ``dropped``. Nothing
  is ever deleted from the database, so an accident costs nothing that the
  next build cannot put back.

Regolith types:

- **The ids**, the ``^a8s8ec`` after each line. Leave them alone; they are what
  tells a line from every other line, and they are rewritten by every build. A
  line that has lost its id is matched by its text, so a paste that dropped one
  is usually recovered, but do not count on it.
- **The numbers**, which are positional and rewritten by every build. Moving a
  project renumbers everything under it.
- **The notes** at the end of a line, ``(carried since …)``, ``(finished …)``
  and ``(→ rolled to …)``.

A long line is broken to fit an editor when it is written, with the rest
indented two further, and joined back up when it is read. You can write a
paragraph the same way.

The round trip
==============

.. code-block:: bash

    regolith build mission-control      # write everybody's document
    #   ... the meeting: people type into their files ...
    regolith helper u-mcsync            # read the documents back
    regolith build mission-control      # write them out again, numbered and stamped

``build mission-control`` writes a document for each person in the group, and
``unassigned.md``. It **will not write over a document that says anything the
database does not have yet**: it leaves the file alone and names the lines,
because writing would lose them. Run the sync, then build again. A line still
named after a sync is one the database cannot hold as it is — a goal under no
project, a task under no goal — so put it under one or take it out. The copy
a build did write over is kept in ``<builddir>/mission-control-previous/``.

``--all`` writes for everybody who ever led a project, and ``--people`` names
whoever should be written whatever their standing. ``mission_control_also_build``
in the run control does the same for the people who keep coming round, such as
a graduate still collaborating.

``helper u-mcsync`` reads every document in the folder and writes what changed,
then says so: ``pei.md: wrote 12, 2 of them new, dropped 1``. It refuses, and
says why, when a document

- cannot be read at all, naming the line it gave up on;
- has lost more than a third of what it held, which is more like damage than
  editing (``--force`` applies it anyway);
- has stopped looking like a mission control document, its headings and
  bullets gone, which is what an editor does when it saves markdown as plain
  text. ``--force`` does not apply here; put the file back from its history.

``--dry-run`` says what would be written without writing it.

The command line
================

Everything a document shows is typed into the document. The helpers are for
what it does not show, and for the moment in a conversation when writing
something down should cost nothing.

``regolith helper a-mcproject "<name>" [--lead <id>]``
    Add a project. A name is all that is required; ``--lead`` says whose it is,
    and without it the project goes to ``unassigned.md`` until somebody moves
    it into their document. A goal and a task are seeded under it, saying
    ``tbd``, so the document comes out with headings to type over.

``regolith helper u-mcproject <id> --status active --grants dmref15 --pi <id>``
    Set the fields a document never shows: the status, the grants, the
    principal investigator, the lead, the links and the notes.

``regolith helper f-mcproject <id>``
    Finish a project and every open goal and task under it, as of today or
    ``--end-date``. Finishing a goal or a task on its own is done in the
    document, by striking it through.

``regolith helper l-mcprojects [--orphans] [--lead <id>] [--grant <id>]``
    List the projects. ``--orphans`` lists the work nobody is doing: projects
    with no lead, and projects led by somebody who has left the group.
    ``--grp-by-lead`` groups them, ``-k`` picks the fields to print.

``regolith helper l-mcgoals [--period 2026fall] [--carried] [--held]``
    List the goals, grouped under their projects, for this period by default.
    ``--carried`` shows only the ones that have rolled from an earlier period
    and since when.

Settings
========

Four run control settings, all optional, described under :doc:`rc`:
``mission_control_dir``, ``mission_control_periods``,
``mission_control_also_build`` and ``mission_control_keep_finished_days``.

When something goes wrong
=========================

Records are never deleted, only marked ``dropped``, so recovery is a matter of
setting a status back. A document that was damaged can be put back from the
shared folder's version history or from ``<builddir>/mission-control-previous/``,
and then read again. And the database is always right: if in doubt, build.
