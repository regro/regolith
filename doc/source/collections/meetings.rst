Meetings
========
the group meeting.

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: string, unique identifier for the date of the group meeting, required
:actions: list, action items expected from the group members for that particular meeting week, required
:agenda: list, schedule of the current meeting, required
:buddies: list, list of pairs of group members that are selected for the buddy round robin, required
:date: ['string', 'datetime', 'date'], date of meeting in format YYYY-MM-DD, optional
:day: integer, day of the group meeting, or the day the entry was edited, optional
:journal_club: dict, Journal club presentation in group meeting, optional

	:doi: string, The doi of the journal club presentation paper.  tbd if it is not known yet, optional
	:link: string, the url to the repo, google slide location, or other web location where the presentation can be found, optional
	:presenter: string, The _id of the group member presenting, or a string describing the presenter, e.g., their full name., optional
	:title: string, The title of the talk., optional
:lead: string, person who will be leading the meeting of the current week, required
:minutes: list, meeting notes in a chronological order according to comments made by the group members, required
:month: ['string', 'integer'], month in which the meeting is taking place, required
:place: string, location where the meeting is taking place on campus, optional
:presentation: dict, indicating the title of the presentation along with the link and the presenter , optional

	:title: string, The title of the presentation.  tbd if it is not known yet, optional
	:link: string, the url to the repo, google slide location, or other web location where the presentation can be found, optional
	:presenter: string, The _id of the group member presenting or a string describing the person., optional
:scribe: string, person who will be taking notes and updating minutes accordingly, required
:time: ['string', 'integer', 'datetime'], the time of the meetingIf an integer is minutes past midnight, so 13:30 is 810 forexample., optional
:updated: ['string', 'datetime', 'date'], The datetime.date object of the most recent update, optional
:uuid: string, A uuid for the entry, optional
:year: integer, year the meeting took place, required


YAML Example
------------

.. code-block:: yaml

	grp1000-01-01:
	  actions:
	    - (Everyone) Update overdue milestones
	    - (Professor Billinge) Explore, and plan a machine learning project for DSI
	    - (Professor Billinge, Emil, Yevgeny, Songsheng) Come up with a Kaggle competition
	      for this DSI project
	    - (Emil) Set up the slack channel for the DSI project
	  agenda:
	    - Review actions
	    - Fargo is not free on any streaming platforms
	    - Review Airtable for deliverables and celebrate
	    - Mention diversity action initiative
	    - Songsheng's journal club presentation
	    - (Vivian and Zicheng) Finish rest of crystallography presentation next week
	    - Emil's 7th inning Yoga Stretch
	    - Crystallography talk
	    - Presentation
	  buddies:
	    - '   Jaylyn C. Umana,    Simon J. L. Billinge'
	    - '   Long Yang,    Emil Kjaer'
	    - '   Sani Harouna-Mayer,   Akshay Choudhry'
	    - '   Vivian Lin,    Songsheng Tao'
	    - '   Ran Gu,    Adiba Ejaz'
	    - '   Zach Thatcher,    Yevgeny Rakita'
	    - "   Zicheng 'Taylor' Liu,    Eric Shen "
	    - '   Hung Vuong,    Daniela Hikari Yano'
	    - '   Ahmed Shaaban,    Jiawei Zang'
	    - '   Berrak Ozer,    Michael Winitch'
	    - '   Shomik Ghose'
	  day: 1
	  journal_club:
	    doi: 10.1107/S2053273319005606
	    link: https://link/to/my/talk.ppt
	    presenter: sbillinge
	    title: what the paper was about and more
	  lead: sbillinge
	  minutes:
	    - Talked about eyesight and prescription lenses
	    - Professor Billinge tells everyone a Logician/Mathematician joke
	    - Mentioned pyjokes, a package in Python that lists bad jokes
	    - Jaylyn greets everyone
	    - Reviewed action items from last time
	    - Talked about fargo, and the merits (or lack thereof) of the Dakotas
	    - Celebrated finished prums
	    - Songhsheng holds journal club presentation on Machine Learning techniques
	    - Discussed Linear Classification, Gradient Descent, Perceptrons, Convolution
	      and other ML topics
	    - Discussed how we can derive scientific meaning from ML algorithms
	    - Discussed real space versus reciprocal space
	    - Finished journal club, had to postpone Akshay's presentation, and the Yoga session
	      to next week
	  month: 1
	  place: Mudd 1106
	  presentation:
	    link: 2007ac_grpmtg
	    presenter: sbillinge
	    title: PDF Distance Extraction
	  scribe: sbillinge
	  time: '0'
	  updated: '2020-07-31 23:27:50.764475'
	  uuid: 3fbee8d9-e283-48e7-948f-eecfc2a123b7
	  year: 1000
	grp2020-07-31:
	  actions:
	    - (Everyone) Update overdue milestones
	    - (Professor Billinge) Explore, and plan a machine learning project for DSI
	    - (Professor Billinge, Emil, Yevgeny, Songsheng) Come up with a Kaggle competition
	      for this DSI project
	    - (Emil) Set up the slack channel for the DSI project
	  agenda:
	    - Review actions
	    - Fargo is not free on any streaming platforms
	    - Review Airtable for deliverables and celebrate
	    - Mention diversity action initiative
	    - Songsheng's journal club presentation
	    - (Vivian and Zicheng) Finish rest of crystallography presentation next week
	    - Emil's 7th inning Yoga Stretch
	    - Crystallography talk
	    - Presentation
	  buddies:
	    - '   Jaylyn C. Umana,    Simon J. L. Billinge'
	    - '   Long Yang,    Emil Kjaer'
	    - '   Sani Harouna-Mayer,   Akshay Choudhry'
	    - '   Vivian Lin,    Songsheng Tao'
	    - '   Ran Gu,    Adiba Ejaz'
	    - '   Zach Thatcher,    Yevgeny Rakita'
	    - "   Zicheng 'Taylor' Liu,    Eric Shen "
	    - '   Hung Vuong,    Daniela Hikari Yano'
	    - '   Ahmed Shaaban,    Jiawei Zang'
	    - '   Berrak Ozer,    Michael Winitch'
	    - '   Shomik Ghose'
	  day: 1
	  journal_club:
	    doi: 10.1107/S2053273319005606
	    link: http://myslides.com/link/to/2007ac_grpmtg
	    presenter: not_a_valid_group_id
	  lead: sbillinge
	  minutes:
	    - Talked about eyesight and prescription lenses
	    - Professor Billinge tells everyone a Logician/Mathematician joke
	    - Mentioned pyjokes, a package in Python that lists bad jokes
	    - Jaylyn greets everyone
	    - Reviewed action items from last time
	    - Talked about fargo, and the merits (or lack thereof) of the Dakotas
	    - Celebrated finished prums
	    - Songhsheng holds journal club presentation on Machine Learning techniques
	    - Discussed Linear Classification, Gradient Descent, Perceptrons, Convolution
	      and other ML topics
	    - Discussed how we can derive scientific meaning from ML algorithms
	    - Discussed real space versus reciprocal space
	    - Finished journal club, had to postpone Akshay's presentation, and the Yoga session
	      to next week
	  month: 1
	  place: Mudd 1106
	  presentation:
	    link: 2007ac_grpmtg
	    presenter: not_a_valid_group_id
	    title: PDF Distance Extraction
	  scribe: sbillinge
	  time: '0'
	  updated: '2020-07-31 23:27:50.764475'
	  uuid: 3fbee8d9-e283-48e7-948f-eecfc2a123b7
	  year: 7000


JSON/Mongo Example
------------------

.. code-block:: json

	{
	    "_id": "grp1000-01-01",
	    "actions": [
	        "(Everyone) Update overdue milestones",
	        "(Professor Billinge) Explore, and plan a machine learning project for DSI",
	        "(Professor Billinge, Emil, Yevgeny, Songsheng) Come up with a Kaggle competition for this DSI project",
	        "(Emil) Set up the slack channel for the DSI project"
	    ],
	    "agenda": [
	        "Review actions",
	        "Fargo is not free on any streaming platforms",
	        "Review Airtable for deliverables and celebrate",
	        "Mention diversity action initiative",
	        "Songsheng's journal club presentation",
	        "(Vivian and Zicheng) Finish rest of crystallography presentation next week",
	        "Emil's 7th inning Yoga Stretch",
	        "Crystallography talk",
	        "Presentation"
	    ],
	    "buddies": [
	        "   Jaylyn C. Umana,    Simon J. L. Billinge",
	        "   Long Yang,    Emil Kjaer",
	        "   Sani Harouna-Mayer,   Akshay Choudhry",
	        "   Vivian Lin,    Songsheng Tao",
	        "   Ran Gu,    Adiba Ejaz",
	        "   Zach Thatcher,    Yevgeny Rakita",
	        "   Zicheng 'Taylor' Liu,    Eric Shen ",
	        "   Hung Vuong,    Daniela Hikari Yano",
	        "   Ahmed Shaaban,    Jiawei Zang",
	        "   Berrak Ozer,    Michael Winitch",
	        "   Shomik Ghose"
	    ],
	    "day": 1,
	    "journal_club": {
	        "doi": "10.1107/S2053273319005606",
	        "link": "https://link/to/my/talk.ppt",
	        "presenter": "sbillinge",
	        "title": "what the paper was about and more"
	    },
	    "lead": "sbillinge",
	    "minutes": [
	        "Talked about eyesight and prescription lenses",
	        "Professor Billinge tells everyone a Logician/Mathematician joke",
	        "Mentioned pyjokes, a package in Python that lists bad jokes",
	        "Jaylyn greets everyone",
	        "Reviewed action items from last time",
	        "Talked about fargo, and the merits (or lack thereof) of the Dakotas",
	        "Celebrated finished prums",
	        "Songhsheng holds journal club presentation on Machine Learning techniques",
	        "Discussed Linear Classification, Gradient Descent, Perceptrons, Convolution and other ML topics",
	        "Discussed how we can derive scientific meaning from ML algorithms",
	        "Discussed real space versus reciprocal space",
	        "Finished journal club, had to postpone Akshay's presentation, and the Yoga session to next week"
	    ],
	    "month": 1,
	    "place": "Mudd 1106",
	    "presentation": {
	        "link": "2007ac_grpmtg",
	        "presenter": "sbillinge",
	        "title": "PDF Distance Extraction"
	    },
	    "scribe": "sbillinge",
	    "time": "0",
	    "updated": "2020-07-31 23:27:50.764475",
	    "uuid": "3fbee8d9-e283-48e7-948f-eecfc2a123b7",
	    "year": 1000
	}
	{
	    "_id": "grp2020-07-31",
	    "actions": [
	        "(Everyone) Update overdue milestones",
	        "(Professor Billinge) Explore, and plan a machine learning project for DSI",
	        "(Professor Billinge, Emil, Yevgeny, Songsheng) Come up with a Kaggle competition for this DSI project",
	        "(Emil) Set up the slack channel for the DSI project"
	    ],
	    "agenda": [
	        "Review actions",
	        "Fargo is not free on any streaming platforms",
	        "Review Airtable for deliverables and celebrate",
	        "Mention diversity action initiative",
	        "Songsheng's journal club presentation",
	        "(Vivian and Zicheng) Finish rest of crystallography presentation next week",
	        "Emil's 7th inning Yoga Stretch",
	        "Crystallography talk",
	        "Presentation"
	    ],
	    "buddies": [
	        "   Jaylyn C. Umana,    Simon J. L. Billinge",
	        "   Long Yang,    Emil Kjaer",
	        "   Sani Harouna-Mayer,   Akshay Choudhry",
	        "   Vivian Lin,    Songsheng Tao",
	        "   Ran Gu,    Adiba Ejaz",
	        "   Zach Thatcher,    Yevgeny Rakita",
	        "   Zicheng 'Taylor' Liu,    Eric Shen ",
	        "   Hung Vuong,    Daniela Hikari Yano",
	        "   Ahmed Shaaban,    Jiawei Zang",
	        "   Berrak Ozer,    Michael Winitch",
	        "   Shomik Ghose"
	    ],
	    "day": 1,
	    "journal_club": {
	        "doi": "10.1107/S2053273319005606",
	        "link": "http://myslides.com/link/to/2007ac_grpmtg",
	        "presenter": "not_a_valid_group_id"
	    },
	    "lead": "sbillinge",
	    "minutes": [
	        "Talked about eyesight and prescription lenses",
	        "Professor Billinge tells everyone a Logician/Mathematician joke",
	        "Mentioned pyjokes, a package in Python that lists bad jokes",
	        "Jaylyn greets everyone",
	        "Reviewed action items from last time",
	        "Talked about fargo, and the merits (or lack thereof) of the Dakotas",
	        "Celebrated finished prums",
	        "Songhsheng holds journal club presentation on Machine Learning techniques",
	        "Discussed Linear Classification, Gradient Descent, Perceptrons, Convolution and other ML topics",
	        "Discussed how we can derive scientific meaning from ML algorithms",
	        "Discussed real space versus reciprocal space",
	        "Finished journal club, had to postpone Akshay's presentation, and the Yoga session to next week"
	    ],
	    "month": 1,
	    "place": "Mudd 1106",
	    "presentation": {
	        "link": "2007ac_grpmtg",
	        "presenter": "not_a_valid_group_id",
	        "title": "PDF Distance Extraction"
	    },
	    "scribe": "sbillinge",
	    "time": "0",
	    "updated": "2020-07-31 23:27:50.764475",
	    "uuid": "3fbee8d9-e283-48e7-948f-eecfc2a123b7",
	    "year": 7000
	}
