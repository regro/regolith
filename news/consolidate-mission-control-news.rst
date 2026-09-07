**Added:**

* **Mission control**, a way of running a group from a document rather than a
  form.  Each person has a markdown file they type into — their projects, the
  goals of the period, the tasks of the week — and regolith reads it back into
  the collections and writes it out again.  Nobody has to learn the command
  line to use it, and nothing anybody types is lost to a build.

  * ``regolith build mission-control`` writes a document per person, and one
    for the projects nobody leads.  It writes for the people currently in the
    group; ``--all`` writes for everybody, and ``--people`` names whoever
    should be written whatever their standing.
  * ``regolith helper mc-sync`` reads the documents back.  A line typed with
    no id is given one, a line taken out marks its record dropped rather than
    deleting it, and a document that has lost most of what it held, or that
    has stopped looking like a mission control document at all, is left alone
    and says why.
  * ``regolith helper a-mcproject`` writes a project down in the moment it is
    mentioned: a name is all that is required, and what nobody has said yet
    says ``tbd``.  It seeds a goal and a task so the document has the headings
    and numbering to type over.
  * ``regolith helper u-mcproject`` sets any field of a project by id, for what
    the document does not show — the grant, the principal investigator, the
    status — and for changing the same field of several projects at once.
  * ``regolith helper l-mcprojects`` and ``l-mcgoals`` replace ``l_projecta``
    and ``l_milestones``.  ``--orphans`` lists the work nobody is doing:
    projects with no lead, and projects led by somebody who has left.
  * Three collections hold it: ``mc_projects``, ``mc_goals`` and ``mc_tasks``.
    A goal belongs to a project, a task to a goal, and anything hanging off
    neither is a todo, which is a separate thing and stays separate.

* Three runcontrol settings, all optional: ``mission_control_dir``, where the
  documents are written; ``mission_control_periods``, what the periods of the
  year are called and when each starts, semesters by default; and
  ``mission_control_keep_finished_days``, how long a finished project stays in
  the document, a year by default.

**Changed:**

* <news item>

**Deprecated:**

* <news item>

**Removed:**

* <news item>

**Fixed:**

* <news item>

**Security:**

* <news item>
