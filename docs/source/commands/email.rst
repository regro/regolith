email
=====

.. code-block:: bash

	usage: regolith email [-h] [--to TO] [--subject SUBJECT] [--body BODY]
	                      [--attach ATTACHMENTS [ATTACHMENTS ...]]
	                      [-c COURSE_IDS [COURSE_IDS ...]] [--db DB]
	                      email_target

	positional arguments:
	  email_target          targets to email, eg "test" or "grades".

	options:
	  -h, --help            show this help message and exit
	  --to TO               receiver of email
	  --subject SUBJECT     email subject line
	  --body BODY           email body, as restructured text
	  --attach ATTACHMENTS [ATTACHMENTS ...]
	                        attachments to send along as well.
	  -c COURSE_IDS [COURSE_IDS ...], --course-id COURSE_IDS [COURSE_IDS ...]
	                        course identifier that should be emailed.
	  --db DB               database name
