build
=====

.. code-block:: bash

	usage: regolith build [-h] [--no-pdf] [--from FROM_DATE] [--to TO_DATE]
	                      [--grants GRANTS [GRANTS ...]]
	                      [--people PEOPLE [PEOPLE ...]]
	                      [--kwargs KWARGS [KWARGS ...]]
	                      build_targets [build_targets ...]

	positional arguments:
	  build_targets         targets to build. Currently valid targets are:
	                        ['annual-activity', 'beamplan', 'current-pending', 'cv', 'figure', 'formalletter', 'grade', 'grades', 'grant-report', 'html', 'internalhtml', 'postdocad', 'preslist', 'publist', 'reading-lists', 'reimb', 'recent-collabs', 'resume', 'review-man', 'review-prop']

	options:
	  -h, --help            show this help message and exit
	  --no-pdf              don't produce PDFs during the build (for builds which produce PDFs)
	  --from FROM_DATE      date in form YYYY-MM-DD.  Items will only be built if their date or end_date is equal or after this date
	  --to TO_DATE          date in form YYYY-MM-DD.  Items will only be built if their date or begin_date is equal or before this date
	  --grants GRANTS [GRANTS ...]
	                        specify a grant or a space-separated list of grants so items are built only if associated with this(these) grant(s)
	  --people PEOPLE [PEOPLE ...]
	                        specify a person or a space-separated list of people such that the build will be for only those people
	  --kwargs KWARGS [KWARGS ...]
	                        pass a specific command to build a specific task if it exists
