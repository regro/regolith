People
======
This collection describes the members of the research group.  This is normally public data.

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: string, unique identifier for the group member, required
:active: boolean, If the person is an active member, default true., optional
:activities: list, activities may be teaching or research things, optional

	:type: dict, optional

		:day: integer, the day the activity took place, optional
		:type: string, the type of the activity, optional

			Allowed values:
				* teaching
				* research
		:month: ['integer', 'string'], the month the activity took place, optional
		:name: string, brief statement of the activity, optional
		:other: string, longer statement of the activity, optional
		:year: integer, the year the activity took place, optional
:aka: ['string', 'list'], list of aliases (also-known-as), useful for identifying the group member in citations or elsewhere., required
:appointments: dict, begin and end date, grant loading status and notes about appointments, optional
:avatar: string, URL to avatar, required
:bio: string, short biographical text, required
:bios: ['string', 'list'], longer biographical text if needed, optional
:collab: boolean, If the person is a collaborator, default false., optional
:committees: list, Committees that are served on, optional

	:type: dict, optional

		:name: string, name of committee, or person if it is a phd committee, optional
		:day: integer, optional
		:month: ['string', 'integer'], optional
		:notes: ['string', 'list'], extra things you want to record about the thing, optional
		:year: integer, optional
		:unit: string, name of department or school etc., optional
		:type: string, type of committee, department, school, university, external, optional

			Allowed values:
				* phdoral
				* phddefense
				* phdproposal
				* promotion
		:level: string, department or school or university, or external, optional

			Allowed values:
				* department
				* school
				* university
				* external
		:group: string, this employment is/was ina group in groups coll, optional
:education: list, This contains the educational information for the group member., required

	:type: dict, optional

		:advisor: string, name or id of advisor for this degree, optional
		:begin_day: integer, optional
		:begin_month: ['string', 'integer'], optional
		:begin_year: integer, optional
		:degree: string, optional
		:department: string, department within the institution, optional
		:group: string, this employment is/was ina group in groups coll, optional
		:end_day: integer, optional
		:end_month: ['string', 'integer'], optional
		:end_year: integer, optional
		:gpa: ['float', 'string'], optional
		:institution: string, optional
		:location: string, optional
		:other: list, optional
:email: string, email address of the group member, optional
:employment: list, Employment information, similar to educational information., optional

	:type: dict, optional

		:advisor: string, name or id of advisor/mentor/manager, optional
		:begin_day: integer, optional
		:begin_month: ['string', 'integer'], optional
		:begin_year: integer, optional
		:begin_date: ['string', 'date', 'datetime'], begin date of employment in format YYYY-MM-DD, optional
		:coworkers: list, list of coworkers.  If position is editor, these are assumed to be coeditors inconflict of interest builder, optional
		:department: string, optional
		:end_day: integer, optional
		:end_year: integer, optional
		:end_date: ['string', 'date', 'datetime'], end date of employment in format YYYY-MM-DD, optional
		:group: string, this employment is/was ina group in groups coll, optional
		:location: string, optional
		:not_in_cv: boolean, set to true if you want to suppress this entry in all cv's and resumes, optional
		:organization: string, optional
		:other: list, optional
		:permanent: boolean, true if the position is open ended and has no fixed end-date, optional
		:position: string, optional

			Allowed values:
				* ``''``
				* editor
				* unknown
				* undergraduate research assistant
				* undergraduate researcher
				* intern
				* visiting student
				* research assistant
				* masters research assistant
				* masters researcher
				* graduate research assistant
				* teaching assistant
				* post-doctoral scholar
				* research fellow
				* assistant scientist
				* assistant lecturer
				* research scientist
				* lecturer
				* adjunct scientist
				* senior assistant lecturer
				* research associate
				* reader
				* ajunct professor
				* adjunct professor
				* consultant
				* programer
				* programmer
				* visiting scientist
				* research assistant professor
				* associate scientist
				* assistant professor
				* assistant physicist
				* associate professor
				* associate physicist
				* professor emeritus
				* visiting professor
				* manager
				* director
				* scientist
				* engineer
				* physicist
				* president
				* professor
				* distinguished professor
		:position_full: string, The full on title of the position.  This will be typeset if it is here, or if not Position will be used.  Position will be used for sorting and must come from a fixed list of positions, optional
		:status: string, optional

			Allowed values:
				* pi
				* adjunct
				* high-school
				* undergrad
				* ms
				* phd
				* postdoc
				* visitor-supported
				* visitor-unsupported
				* research-associate
:facilities: list, facilities may be teaching or research things, optional

	:type: dict, optional

		:begin_day: integer, the day facility, or the wish for the facility, started, optional
		:end_day: integer, the day facility started, optional
		:type: string, the type of the facility. Columbia asksfor wished-for facilities, so there are teaching-wish and research-wish fields., optional

			Allowed values:
				* teaching
				* research
				* shared
				* other
				* teaching_wish
				* research_wish
		:begin_month: ['integer', 'string'], the month the facility (or wish) started, optional
		:end_month: ['integer', 'string'], the month the faclity went away, optional
		:name: string, description of the facility, optional
		:notes: ['string', 'list'], anything else you want to jot down, optional
		:begin_year: integer, the year the facility (or wish) started, optional
		:end_year: integer, the year the facility (or wish) went away, optional
:funding: list, Funding and scholarship that the group member has individually obtained in the past. **WARNING:** this is not to be confused with the **grants** collection, optional

	:type: dict, optional

		:currency: string, optional
		:duration: string, optional
		:month: ['string', 'integer'], optional
		:name: string, optional
		:value: ['float', 'integer'], optional
		:year: integer, optional
:github_id: string, Your GitHub ID, optional
:google_scholar_url: string, URL of your Google Scholar profile, optional
:grp_mtg_active: boolean, Whether to schedule tasks at group meeting or not, optional
:hindex: list, details of hindex pulled on a certain date, optional

	:type: dict, optional

		:h: integer, the value of the h index, optional
		:h_last_five: integer, h index over past 5 years, optional
		:citations: integer, total number of citations, optional
		:citations_last_five: integer, number of citations in the past 5 years, optional
		:origin: string, where the numbers came from, optional
		:since: integer, year of first citation, optional
		:year: integer, year when the data were pulled, optional
		:month: ['string', 'integer'], month when the data were pulled, optional
		:day: integer, day when the data were pulled, optional
:home_address: dict, The person's home address, optional

	:street: string, street address, optional
	:city: string, name of home city, optional
	:state: string, name o home state, optional
	:zip: string, zip code, optional
:honors: list, Honors that have been awarded to this group member, optional

	:type: dict, optional

		:description: string, optional
		:month: ['string', 'integer'], optional
		:name: string, optional
		:year: integer, optional
:initials: string, The canonical initials for this group member, optional
:linkedin_url: string, The URL of this person's LinkedIn account, optional
:membership: list, Professional organizations this member is a part of, optional

	:type: dict, optional

		:begin_month: ['string', 'integer'], optional
		:begin_year: integer, optional
		:description: string, optional
		:end_month: ['string', 'integer'], optional
		:end_year: integer, optional
		:organization: string, optional
		:position: string, optional
		:website: string, optional
:miscellaneous: dict, Place to put weird things needed for special reporta, optional

	:metrics_for_success: list, How do I want to be judged, optional
:name: string, Full, canonical name for the person, required
:office: string, The person's office, optional
:orcid_id: string, The ORCID ID of the person, optional
:position: string, such as professor, graduate student, or scientist, optional

	Allowed values:
		* ``''``
		* editor
		* unknown
		* undergraduate research assistant
		* undergraduate researcher
		* intern
		* visiting student
		* research assistant
		* masters research assistant
		* masters researcher
		* graduate research assistant
		* teaching assistant
		* post-doctoral scholar
		* research fellow
		* assistant scientist
		* assistant lecturer
		* research scientist
		* lecturer
		* adjunct scientist
		* senior assistant lecturer
		* research associate
		* reader
		* ajunct professor
		* adjunct professor
		* consultant
		* programer
		* programmer
		* visiting scientist
		* research assistant professor
		* associate scientist
		* assistant professor
		* assistant physicist
		* associate professor
		* associate physicist
		* professor emeritus
		* visiting professor
		* manager
		* director
		* scientist
		* engineer
		* physicist
		* president
		* professor
		* distinguished professor
:position_full: string, The full on title of the position.  This will be typeset if it is here, or if not Position will be used.  Position will be used for sorting and must come from a fixed list of positions, optional
:publicity: list, summary of publicity that person has received, optional

	:type: dict, optional

		:type: string, optional

			Allowed values:
				* online
				* article
		:topic: string, The short sentence of what the publicity was about, optional
		:title: string, The title of the piece, optional
		:date: ['string', 'date'], the date of the service, optional
		:day: integer, The day the piece appeared, optional
		:month: ['string', 'integer'], The month the piece appeared, optional
		:publication: string, The place where the publicity was placed, optional
		:text: string, The text of the publicity, optional
		:url: string, The URL where the piece may be found, optional
		:year: integer, The year the piece appeared, optional
		:grant: string, The identifier of the grant associated with the piece, optional
:research_focus_areas: list, summary of research projects that are ongoing. Usedin Annual appraisal for example, optional

	:type: dict, optional

		:begin_year: integer, optional
		:end_year: integer, optional
		:description: string, optional
:research_summary: string, Brief summary of overarching research goals, optional
:service: list, Service that this group member has provided, optional

	:type: dict, optional

		:date: ['string', 'date'], the date of the service, optional
		:begin_date: ['string', 'date'], the begin date, optional
		:end_date: ['string', 'date'], the end date, optional
		:description: string, optional
		:duration: string, optional
		:month: ['string', 'integer'], Use month and year if the servicedoesn't extend more than one year.Otherwise use begin_year and end_year, optional
		:name: string, optional
		:role: string, the role played in the activity, e.g., co-chair, optional
		:notes: ['string', 'list'], optional
		:year: integer, optional
		:begin_year: integer, optional
		:begin_day: integer, optional
		:begin_month: ['string', 'integer'], Use month and year if the servicedoesn't extend more than one year.Otherwise use begin_year/month and end_year/month, optional
		:end_year: integer, optional
		:end_month: ['string', 'integer'], Use month and year if the servicedoesn't extend more than one year.Otherwise use begin_year and end_year, optional
		:end_day: integer, optional
		:other: ['string', 'list'], optional
		:type: string, profession, department, school, university, optional

			Allowed values:
				* profession
				* university
				* school
				* department
:skills: list, Skill the group member has, optional

	:type: dict, optional

		:category: string, optional
		:level: string, optional
		:name: string, optional
:teaching: list, Courses that this group member has taught, if any, optional

	:type: dict, optional

		:course: string, optional
		:courseid: string, optional
		:description: string, optional
		:end_month: ['string', 'integer'], optional
		:end_year: integer, optional
		:enrollment: ['integer', 'string'], optional
		:evaluation: dict, optional

			:response_rate: number, optional
			:amount_learned: number, optional
			:appropriateness_workload: number, optional
			:course_overall: number, optional
			:fairness_grading: number, optional
			:organization: number, optional
			:classroom_delivery: number, optional
			:approachability: number, optional
			:instructor_overall: number, optional
			:comments: list, student comments, optional
		:materials: string, optional
		:month: ['string', 'integer'], optional
		:organization: string, optional
		:position: string, optional
		:semester: string, optional
		:syllabus: string, optional
		:video: string, optional
		:website: string, optional
		:year: integer, optional
:title: string, for example, Dr., etc., optional


YAML Example
------------

.. code-block:: yaml

	abeing:
	  active: false
	  aka:
	    - being
	    - human
	    - person
	  avatar: https://xkcd.com/1221/
	  bio: Abstract Being is an exemplar human existence
	  education:
	    - begin_year: 2010
	      degree: bachelors
	      institution: University of Laughs
	  employment:
	    - begin_date: '2015-06-01'
	      end_date: '2015-08-31'
	      group: bg
	      organization: columbiau
	      position: intern
	    - begin_date: '2020-01-01'
	      end_date: '2030-12-31'
	      group: agroup
	      organization: usouthcarolina
	      position: intern
	    - begin_date: '2010-06-01'
	      end_date: '2012-08-31'
	      group: ergs
	      organization: columbiau
	      position: intern
	    - begin_date: '2017-06-01'
	      end_date: '2019-08-31'
	      group: bg
	      organization: columbiau
	      position: intern
	  name: Abstract Being
	  position: intern
	sbillinge:
	  active: true
	  activities:
	    - name: course development
	      other: Developed a new course for Materials Science
	      type: teaching
	      year: 2018
	  aka:
	    - Billinge
	  avatar: https://avatars1.githubusercontent.com/u/320553?v=3&s=200
	  bio: Simon teaches and does research
	  committees:
	    - level: department
	      name: Same Old
	      notes: something
	      type: phddefense
	      unit: Materials Science
	      year: 2018
	  education:
	    - advisor: scopatz
	      begin_year: 2008
	      degree: Ph.D. Mechanical Engineering, Nuclear and Radiation Engineering Program
	      department: apam
	      end_year: 2011
	      group: ergs
	      institution: The University of Texas at Austin
	      location: Austin, TX
	      other:
	        - 'Adviser: Erich A. Schneider'
	        - 'Dissertation: Essential Physics for Fuel Cycle Modeling & Analysis'
	  email: sb2896@columbia.edu
	  employment:
	    - advisor: scopatz
	      begin_year: 2015
	      group: ergs
	      location: Columbia, SC
	      organization: The University of South Carolina
	      other:
	        - 'Cyclus: An agent-based, discrete time nuclear fuel cycle simulator.'
	        - 'PyNE: The Nuclear Engineering Toolkit.'
	        - 'Website: http://www.ergs.sc.edu/'
	      position: assistant professor
	      status: phd
	  facilities:
	    - begin_year: 2015
	      name: Shared {Habanero} compute cluster
	      type: other
	    - begin_year: 2015
	      name: Shared access to wet lab
	      type: research_wish
	    - begin_year: 2017
	      name: Courseworks2
	      type: teaching
	    - begin_year: 2019
	      name: nothing right now
	      type: teaching_wish
	    - begin_year: 2008
	      name: I don't have one
	      type: research
	  funding:
	    - name: Omega Laser User's Group Travel Award
	      value: 1100
	      year: 2013
	    - name: NIF User's Group Travel Award
	      value: 1150
	      year: 2013
	  google_scholar_url: https://scholar.google.com/citations?user=dRm8f
	  grp_mtg_active: true
	  hindex:
	    - citations: 17890
	      citations_last_five: 8817
	      day: 12
	      h: 65
	      h_last_five: 43
	      month: May
	      origin: Google Scholar
	      since: 1991
	      year: 2019
	  home_address:
	    city: The big apple
	    state: plasma
	    street: 123 Wallabe Ln
	    zip: '007'
	  initials: SJLB
	  linkedin_url: https://scholar.google.com/citations?hl=en&user=PAJ
	  membership:
	    - begin_year: 2006
	      organization: American Nuclear Society
	      position: Member
	  miscellaneous:
	    metrics_for_success:
	      - publications(quality, quantity)
	      - invite talks
	      - funding
	      - citations
	  name: Simon J. L. Billinge
	  office: 1105 Seely W. Mudd Building (inner office)
	  orcid_id: 0000-0002-9432-4248
	  position: professor
	  publicity:
	    - date: '2019-07-24'
	      day: 24
	      grant: bnlldrd18
	      month: Jul
	      publication: Brookhaven National Laboratory Web Story
	      title: An awesome project and well worth the money
	      topic: LDRD Provenance project
	      type: online
	      url: http://www.google.com
	      year: 2019
	  research_focus_areas:
	    - begin_year: 2010
	      description: software applied to materials engineering and life
	  service:
	    - month: August
	      name: 'Master of Ceremonies and Organizer Brown University Chemistry: Believe
	        it or Not public chemistry demonstration'
	      type: profession
	      year: 2017
	    - begin_date: '2018-01-01'
	      end_date: '2018-01-01'
	      name: Applied Physics program committee
	      type: department
	    - date: '2017-06-01'
	      name: Ad hoc tenure committee
	      notes: Albert Einstein
	      type: school
	    - month: 12
	      name: Co-organizer JUAMI
	      other:
	        - great way to meet people
	      role: co-organizer
	      type: profession
	      year: 2017
	  skills:
	    - category: Programming Languages
	      level: expert
	      name: Python
	  teaching:
	    - course: 'MSAE-3010: Introduction to Materials Science'
	      courseid: f16-3010
	      description: This course is an introduction to nuclear physics.
	      enrollment: 18
	      evaluation:
	        amount_learned: 4.57
	        approachability: 4.86
	        appropriateness_workload: 4.29
	        classroom_delivery: 4.29
	        comments:
	          - Great teacher but disorganized
	          - Wears pink pants.  Why?
	        course_overall: 4.43
	        fairness_grading: 4.57
	        instructor_overall: 4.43
	        organization: 4.0
	        response_rate: 58.33
	      month: August
	      organization: Columbia University
	      position: professor
	      semester: Fall
	      syllabus: https://drive.google.com/open?id=0BxUpd34yizZreDBCMEJNY2FUbnc
	      year: 2016
	    - course: 'MSAE-3010: Introduction to Materials Science'
	      courseid: f17-3010
	      description: This course is an introduction to nuclear physics.
	      enrollment: 18
	      evaluation:
	        amount_learned: 4.57
	        approachability: 4.86
	        appropriateness_workload: 4.29
	        classroom_delivery: 4.29
	        comments:
	          - Great teacher but disorganized
	          - Wears pink pants.  Why?
	        course_overall: 4.43
	        fairness_grading: 4.57
	        instructor_overall: 4.43
	        organization: 4.0
	        response_rate: 58.33
	      month: August
	      organization: Columbia University
	      position: professor
	      semester: Fall
	      syllabus: https://drive.google.com/open?id=0BxUpd34yizZreDBCMEJNY2FUbnc
	      year: 2017
	    - course: 'MSAE-3010: Introduction to Materials Science'
	      courseid: s18-3010
	      description: This course is an introduction to nuclear physics.
	      enrollment: 18
	      evaluation:
	        amount_learned: 4.57
	        approachability: 4.86
	        appropriateness_workload: 4.29
	        classroom_delivery: 4.29
	        comments:
	          - Great teacher but disorganized
	          - Wears pink pants.  Why?
	        course_overall: 4.43
	        fairness_grading: 4.57
	        instructor_overall: 4.43
	        organization: 4.0
	        response_rate: 58.33
	      month: Jan
	      organization: Columbia University
	      position: professor
	      semester: Spring
	      syllabus: https://drive.google.com/open?id=0BxUpd34yizZreDBCMEJNY2FUbnc
	      year: 2018
	    - course: 'MSAE-3010: Introduction to Materials Science'
	      courseid: s17-3010
	      description: This course is an introduction to nuclear physics.
	      enrollment: 18
	      evaluation:
	        amount_learned: 4.57
	        approachability: 4.86
	        appropriateness_workload: 4.29
	        classroom_delivery: 4.29
	        comments:
	          - Great teacher but disorganized
	          - Wears pink pants.  Why?
	        course_overall: 4.43
	        fairness_grading: 4.57
	        instructor_overall: 4.43
	        organization: 4.0
	        response_rate: 58.33
	      month: Jan
	      organization: Columbia University
	      position: professor
	      semester: Spring
	      syllabus: https://drive.google.com/open?id=0BxUpd34yizZreDBCMEJNY2FUbnc
	      year: 2017
	    - course: 'MSAE-3010: Introduction to Materials Science'
	      courseid: s19-3010
	      description: This course is an introduction to nuclear physics.
	      enrollment: 18
	      month: Jan
	      organization: Columbia University
	      position: professor
	      semester: Spring
	      syllabus: https://drive.google.com/open?id=0BxUpd34yizZreDBCMEJNY2FUbnc
	      year: 2019
	    - course: 'MSAE-3010: Introduction to Materials Science'
	      courseid: f18-3010
	      description: This course is an introduction to nuclear physics.
	      enrollment: 18
	      month: August
	      organization: Columbia University
	      position: professor
	      semester: Fall
	      syllabus: https://drive.google.com/open?id=0BxUpd34yizZreDBCMEJNY2FUbnc
	      year: 2018
	    - course: 'MSAE-3010: Introduction to Materials Science'
	      courseid: f19-3010
	      description: This course is an introduction to nuclear physics.
	      month: August
	      organization: Columbia University
	      position: professor
	      semester: Fall
	      syllabus: https://drive.google.com/open?id=0BxUpd34yizZreDBCMEJNY2FUbnc
	      year: 2019
	  title: Dr.
	scopatz:
	  aka:
	    - Scopatz
	    - Scopatz, A
	    - Scopatz, A.
	    - Scopatz, A M
	    - Anthony Michael Scopatz
	  appointments:
	    f19:
	      begin_day: 1
	      begin_month: 2
	      begin_year: 2019
	      end_day: 31
	      end_month: 3
	      end_year: 2019
	      grant: dmref15
	      loading: 0.75
	      notes:
	        - forgetmenot
	      status: finalized
	      type: pd
	    s20:
	      begin_date: '2020-01-01'
	      end_date: '2020-05-15'
	      grant: sym
	      loading: 1.0
	      notes:
	        - fully appointed
	        - outdated grant
	      status: finalized
	      type: pd
	    ss20:
	      begin_date: '2020-06-01'
	      end_date: '2020-08-31'
	      grant: abc42
	      loading: 0.8
	      notes: []
	      status: proposed
	      type: ss
	    ss21:
	      begin_date: '2020-09-01'
	      end_date: '2021-08-31'
	      grant: future_grant
	      loading: 1.0
	      notes: []
	      status: proposed
	      type: ss
	  avatar: https://avatars1.githubusercontent.com/u/320553?v=3&s=200
	  bio: Anthony Scopatz is currently an Assistant Professor
	  bios:
	    - Anthony Scopatz is currently an Assistant Professor but will go on to do great
	      things
	  committees:
	    - day: 1
	      level: department
	      month: 3
	      name: Heather Stanford
	      type: phdoral
	      unit: apam
	      year: 2020
	    - day: 1
	      level: school
	      month: 3
	      name: Heather Stanford
	      type: promotion
	      unit: seas
	      year: 2020
	    - day: 1
	      level: external
	      month: 3
	      name: Heather Stanford
	      notes: something else to remember about it, not published
	      type: phddefense
	      unit: U Denmark
	      year: 2020
	    - day: 1
	      level: university
	      month: 3
	      name: Heather Stanford
	      type: promotion
	      unit: columbiau
	      year: 2020
	  education:
	    - advisor: scopatz
	      begin_year: 2008
	      degree: Ph.D. Mechanical Engineering, Nuclear and Radiation Engineering Program
	      department: apam
	      end_year: 2011
	      group: ergs
	      institution: The University of Texas at Austin
	      location: Austin, TX
	      other:
	        - 'Adviser: Erich A. Schneider'
	        - 'Dissertation: Essential Physics for Fuel Cycle Modeling & Analysis'
	    - begin_year: 2006
	      degree: M.S.E. Mechanical Engineering, Nuclear and Radiation Engineering Program
	      end_year: 2007
	      institution: The University of Texas at Austin
	      location: Austin, TX
	      other:
	        - 'Adviser: Erich A. Schneider'
	        - 'Thesis: Recyclable Uranium Options under the Global Nuclear Energy Partnership'
	    - begin_day: 1
	      begin_month: Sep
	      begin_year: 2002
	      degree: B.S. Physics
	      end_day: 20
	      end_month: 5
	      end_year: 2006
	      institution: University of California, Santa Barbara
	      location: Santa Barbara, CA
	      other:
	        - Graduated with a Major in Physics and a Minor in Mathematics
	    - begin_year: 2008
	      degree: ongoing
	      department: earth
	      group: life
	      institution: solar system
	      location: land, mostly
	  email: scopatz@cec.sc.edu
	  employment:
	    - advisor: scopatz
	      begin_year: 2015
	      coworkers:
	        - afriend
	      group: ergs
	      location: Columbia, SC
	      organization: The University of South Carolina
	      other:
	        - 'Cyclus: An agent-based, discrete time nuclear fuel cycle simulator.'
	        - 'PyNE: The Nuclear Engineering Toolkit.'
	        - 'Website: http://www.ergs.sc.edu/'
	      permanent: true
	      position: assistant professor
	      position_full: Assistant Professor, Mechanical Engineering Department
	      status: ms
	    - advisor: scopatz
	      begin_day: 1
	      begin_month: Jun
	      begin_year: 2013
	      department: Physics
	      end_day: 15
	      end_month: 3
	      end_year: 2015
	      location: Madison, WI
	      organization: CNERG, The University of Wisconsin-Madison
	      other:
	        - 'Cyclus: An agent-based, discrete time nuclear fuel cycle simulator.'
	        - 'PyNE: The Nuclear Engineering Toolkit.'
	        - 'Website: https://cnerg.github.io/'
	      position: associate scientist
	      position_full: Associate Scientist, Engineering Physics Department
	      status: undergrad
	    - begin_day: 1
	      begin_month: Nov
	      begin_year: 2011
	      end_month: May
	      end_year: 2013
	      location: Chicago, IL
	      organization: The FLASH Center, The University of Chicago
	      other:
	        - 'NIF: Simulation of magnetic field generation from neutral plasmas using
	          FLASH.'
	        - 'CosmoB: Simulation of magnetic field generation from neutral plasmas using
	          FLASH.'
	        - 'FLASH4: High-energy density physics capabilities and utilities.'
	        - 'Simulated Diagnostics: Schlieren, shadowgraphy, Langmuir probes, etc. from
	          FLASH.'
	        - 'OpacPlot: HDF5-based equation of state and opacity file format.'
	        - 'Website: http://flash.uchicago.edu/site/'
	      position: post-doctoral scholar
	      position_full: Research Scientist, Postdoctoral Scholar
	      status: pi
	    - begin_date: '2000-01-01'
	      end_date: '2001-12-31'
	      location: Chicago, IL
	      not_in_cv: true
	      organization: Google
	      other: []
	      position: janitor
	  funding:
	    - name: Omega Laser User's Group Travel Award
	      value: 1100
	      year: 2013
	    - name: NIF User's Group Travel Award
	      value: 1150
	      year: 2013
	  github_id: ascopatz
	  google_scholar_url: https://scholar.google.com/citations?user=dRm8f
	  hindex:
	    - citations: 19837
	      citations_last_five: 9419
	      day: 19
	      h: 25
	      h_last_five: 46
	      month: 2
	      origin: Google Scholar
	      since: 1991
	      year: 2020
	  home_address:
	    city: The big apple
	    state: plasma
	    street: 123 Wallabe Ln
	    zip: '007'
	  initials: AMS
	  membership:
	    - begin_year: 2006
	      organization: American Nuclear Society
	      position: Member
	    - begin_year: 2013
	      organization: Python Software Foundation
	      position: Fellow
	  name: Anthony Scopatz
	  orcid_id: 0000-0002-9432-4248
	  position: professor
	  research_focus_areas:
	    - begin_year: 2010
	      description: software applied to nuclear engineering and life
	  service:
	    - month: 3
	      name: International Steering Committee
	      notes:
	        - something
	      role: chair
	      type: profession
	      year: 2020
	    - begin_year: 2018
	      end_year: 2021
	      name: National Steering Committee
	      notes: something
	      type: profession
	  skills:
	    - category: Programming Languages
	      level: expert
	      name: Python
	    - category: Programming Languages
	      level: expert
	      name: Cython
	  teaching:
	    - course: 'EMCH 552: Intro to Nuclear Engineering'
	      courseid: EMCH 552
	      description: This course is an introduction to nuclear physics.
	      enrollment: tbd
	      month: August
	      organization: University of South Carolina
	      position: professor
	      semester: Spring
	      syllabus: https://drive.google.com/open?id=0BxUpd34yizZreDBCMEJNY2FUbnc
	      year: 2017
	    - course: 'EMCH 558/758: Reactor Power Systems'
	      courseid: EMCH 558
	      description: This course covers conventional reactors.
	      enrollment: 28
	      evaluation:
	        amount_learned: 3.5
	        approachability: 4.3
	        appropriateness_workload: 3.15
	        classroom_delivery: 4
	        comments:
	          - super duper
	          - dandy
	        course_overall: 3.67
	        fairness_grading: 3.54
	        instructor_overall: 3.5
	        organization: 3.25
	        response_rate: 66.76
	      month: January
	      organization: University of South Carolina
	      position: professor
	      syllabus: https://docs.google.com/document/d/1uMAx_KFZK9ugYyF6wWtLLWgITVhaTBkAf8-PxiboYdM/edit?usp=sharing
	      year: 2017
	  title: Dr.


JSON/Mongo Example
------------------

.. code-block:: json

	{
	    "_id": "abeing",
	    "active": false,
	    "aka": [
	        "being",
	        "human",
	        "person"
	    ],
	    "avatar": "https://xkcd.com/1221/",
	    "bio": "Abstract Being is an exemplar human existence",
	    "education": [
	        {
	            "begin_year": 2010,
	            "degree": "bachelors",
	            "institution": "University of Laughs"
	        }
	    ],
	    "employment": [
	        {
	            "begin_date": "2015-06-01",
	            "end_date": "2015-08-31",
	            "group": "bg",
	            "organization": "columbiau",
	            "position": "intern"
	        },
	        {
	            "begin_date": "2020-01-01",
	            "end_date": "2030-12-31",
	            "group": "agroup",
	            "organization": "usouthcarolina",
	            "position": "intern"
	        },
	        {
	            "begin_date": "2010-06-01",
	            "end_date": "2012-08-31",
	            "group": "ergs",
	            "organization": "columbiau",
	            "position": "intern"
	        },
	        {
	            "begin_date": "2017-06-01",
	            "end_date": "2019-08-31",
	            "group": "bg",
	            "organization": "columbiau",
	            "position": "intern"
	        }
	    ],
	    "name": "Abstract Being",
	    "position": "intern"
	}
	{
	    "_id": "sbillinge",
	    "active": true,
	    "activities": [
	        {
	            "name": "course development",
	            "other": "Developed a new course for Materials Science",
	            "type": "teaching",
	            "year": 2018
	        }
	    ],
	    "aka": [
	        "Billinge"
	    ],
	    "avatar": "https://avatars1.githubusercontent.com/u/320553?v=3&s=200",
	    "bio": "Simon teaches and does research",
	    "committees": [
	        {
	            "level": "department",
	            "name": "Same Old",
	            "notes": "something",
	            "type": "phddefense",
	            "unit": "Materials Science",
	            "year": 2018
	        }
	    ],
	    "education": [
	        {
	            "advisor": "scopatz",
	            "begin_year": 2008,
	            "degree": "Ph.D. Mechanical Engineering, Nuclear and Radiation Engineering Program",
	            "department": "apam",
	            "end_year": 2011,
	            "group": "ergs",
	            "institution": "The University of Texas at Austin",
	            "location": "Austin, TX",
	            "other": [
	                "Adviser: Erich A. Schneider",
	                "Dissertation: Essential Physics for Fuel Cycle Modeling & Analysis"
	            ]
	        }
	    ],
	    "email": "sb2896@columbia.edu",
	    "employment": [
	        {
	            "advisor": "scopatz",
	            "begin_year": 2015,
	            "group": "ergs",
	            "location": "Columbia, SC",
	            "organization": "The University of South Carolina",
	            "other": [
	                "Cyclus: An agent-based, discrete time nuclear fuel cycle simulator.",
	                "PyNE: The Nuclear Engineering Toolkit.",
	                "Website: http://www.ergs.sc.edu/"
	            ],
	            "position": "assistant professor",
	            "status": "phd"
	        }
	    ],
	    "facilities": [
	        {
	            "begin_year": 2015,
	            "name": "Shared {Habanero} compute cluster",
	            "type": "other"
	        },
	        {
	            "begin_year": 2015,
	            "name": "Shared access to wet lab",
	            "type": "research_wish"
	        },
	        {
	            "begin_year": 2017,
	            "name": "Courseworks2",
	            "type": "teaching"
	        },
	        {
	            "begin_year": 2019,
	            "name": "nothing right now",
	            "type": "teaching_wish"
	        },
	        {
	            "begin_year": 2008,
	            "name": "I don't have one",
	            "type": "research"
	        }
	    ],
	    "funding": [
	        {
	            "name": "Omega Laser User's Group Travel Award",
	            "value": 1100,
	            "year": 2013
	        },
	        {
	            "name": "NIF User's Group Travel Award",
	            "value": 1150,
	            "year": 2013
	        }
	    ],
	    "google_scholar_url": "https://scholar.google.com/citations?user=dRm8f",
	    "grp_mtg_active": true,
	    "hindex": [
	        {
	            "citations": 17890,
	            "citations_last_five": 8817,
	            "day": 12,
	            "h": 65,
	            "h_last_five": 43,
	            "month": "May",
	            "origin": "Google Scholar",
	            "since": 1991,
	            "year": 2019
	        }
	    ],
	    "home_address": {
	        "city": "The big apple",
	        "state": "plasma",
	        "street": "123 Wallabe Ln",
	        "zip": "007"
	    },
	    "initials": "SJLB",
	    "linkedin_url": "https://scholar.google.com/citations?hl=en&user=PAJ",
	    "membership": [
	        {
	            "begin_year": 2006,
	            "organization": "American Nuclear Society",
	            "position": "Member"
	        }
	    ],
	    "miscellaneous": {
	        "metrics_for_success": [
	            "publications(quality, quantity)",
	            "invite talks",
	            "funding",
	            "citations"
	        ]
	    },
	    "name": "Simon J. L. Billinge",
	    "office": "1105 Seely W. Mudd Building (inner office)",
	    "orcid_id": "0000-0002-9432-4248",
	    "position": "professor",
	    "publicity": [
	        {
	            "date": "2019-07-24",
	            "day": 24,
	            "grant": "bnlldrd18",
	            "month": "Jul",
	            "publication": "Brookhaven National Laboratory Web Story",
	            "title": "An awesome project and well worth the money",
	            "topic": "LDRD Provenance project",
	            "type": "online",
	            "url": "http://www.google.com",
	            "year": 2019
	        }
	    ],
	    "research_focus_areas": [
	        {
	            "begin_year": 2010,
	            "description": "software applied to materials engineering and life"
	        }
	    ],
	    "service": [
	        {
	            "month": "August",
	            "name": "Master of Ceremonies and Organizer Brown University Chemistry: Believe it or Not public chemistry demonstration",
	            "type": "profession",
	            "year": 2017
	        },
	        {
	            "begin_date": "2018-01-01",
	            "end_date": "2018-01-01",
	            "name": "Applied Physics program committee",
	            "type": "department"
	        },
	        {
	            "date": "2017-06-01",
	            "name": "Ad hoc tenure committee",
	            "notes": "Albert Einstein",
	            "type": "school"
	        },
	        {
	            "month": 12,
	            "name": "Co-organizer JUAMI",
	            "other": [
	                "great way to meet people"
	            ],
	            "role": "co-organizer",
	            "type": "profession",
	            "year": 2017
	        }
	    ],
	    "skills": [
	        {
	            "category": "Programming Languages",
	            "level": "expert",
	            "name": "Python"
	        }
	    ],
	    "teaching": [
	        {
	            "course": "MSAE-3010: Introduction to Materials Science",
	            "courseid": "f16-3010",
	            "description": "This course is an introduction to nuclear physics.",
	            "enrollment": 18,
	            "evaluation": {
	                "amount_learned": 4.57,
	                "approachability": 4.86,
	                "appropriateness_workload": 4.29,
	                "classroom_delivery": 4.29,
	                "comments": [
	                    "Great teacher but disorganized",
	                    "Wears pink pants.  Why?"
	                ],
	                "course_overall": 4.43,
	                "fairness_grading": 4.57,
	                "instructor_overall": 4.43,
	                "organization": 4.0,
	                "response_rate": 58.33
	            },
	            "month": "August",
	            "organization": "Columbia University",
	            "position": "professor",
	            "semester": "Fall",
	            "syllabus": "https://drive.google.com/open?id=0BxUpd34yizZreDBCMEJNY2FUbnc",
	            "year": 2016
	        },
	        {
	            "course": "MSAE-3010: Introduction to Materials Science",
	            "courseid": "f17-3010",
	            "description": "This course is an introduction to nuclear physics.",
	            "enrollment": 18,
	            "evaluation": {
	                "amount_learned": 4.57,
	                "approachability": 4.86,
	                "appropriateness_workload": 4.29,
	                "classroom_delivery": 4.29,
	                "comments": [
	                    "Great teacher but disorganized",
	                    "Wears pink pants.  Why?"
	                ],
	                "course_overall": 4.43,
	                "fairness_grading": 4.57,
	                "instructor_overall": 4.43,
	                "organization": 4.0,
	                "response_rate": 58.33
	            },
	            "month": "August",
	            "organization": "Columbia University",
	            "position": "professor",
	            "semester": "Fall",
	            "syllabus": "https://drive.google.com/open?id=0BxUpd34yizZreDBCMEJNY2FUbnc",
	            "year": 2017
	        },
	        {
	            "course": "MSAE-3010: Introduction to Materials Science",
	            "courseid": "s18-3010",
	            "description": "This course is an introduction to nuclear physics.",
	            "enrollment": 18,
	            "evaluation": {
	                "amount_learned": 4.57,
	                "approachability": 4.86,
	                "appropriateness_workload": 4.29,
	                "classroom_delivery": 4.29,
	                "comments": [
	                    "Great teacher but disorganized",
	                    "Wears pink pants.  Why?"
	                ],
	                "course_overall": 4.43,
	                "fairness_grading": 4.57,
	                "instructor_overall": 4.43,
	                "organization": 4.0,
	                "response_rate": 58.33
	            },
	            "month": "Jan",
	            "organization": "Columbia University",
	            "position": "professor",
	            "semester": "Spring",
	            "syllabus": "https://drive.google.com/open?id=0BxUpd34yizZreDBCMEJNY2FUbnc",
	            "year": 2018
	        },
	        {
	            "course": "MSAE-3010: Introduction to Materials Science",
	            "courseid": "s17-3010",
	            "description": "This course is an introduction to nuclear physics.",
	            "enrollment": 18,
	            "evaluation": {
	                "amount_learned": 4.57,
	                "approachability": 4.86,
	                "appropriateness_workload": 4.29,
	                "classroom_delivery": 4.29,
	                "comments": [
	                    "Great teacher but disorganized",
	                    "Wears pink pants.  Why?"
	                ],
	                "course_overall": 4.43,
	                "fairness_grading": 4.57,
	                "instructor_overall": 4.43,
	                "organization": 4.0,
	                "response_rate": 58.33
	            },
	            "month": "Jan",
	            "organization": "Columbia University",
	            "position": "professor",
	            "semester": "Spring",
	            "syllabus": "https://drive.google.com/open?id=0BxUpd34yizZreDBCMEJNY2FUbnc",
	            "year": 2017
	        },
	        {
	            "course": "MSAE-3010: Introduction to Materials Science",
	            "courseid": "s19-3010",
	            "description": "This course is an introduction to nuclear physics.",
	            "enrollment": 18,
	            "month": "Jan",
	            "organization": "Columbia University",
	            "position": "professor",
	            "semester": "Spring",
	            "syllabus": "https://drive.google.com/open?id=0BxUpd34yizZreDBCMEJNY2FUbnc",
	            "year": 2019
	        },
	        {
	            "course": "MSAE-3010: Introduction to Materials Science",
	            "courseid": "f18-3010",
	            "description": "This course is an introduction to nuclear physics.",
	            "enrollment": 18,
	            "month": "August",
	            "organization": "Columbia University",
	            "position": "professor",
	            "semester": "Fall",
	            "syllabus": "https://drive.google.com/open?id=0BxUpd34yizZreDBCMEJNY2FUbnc",
	            "year": 2018
	        },
	        {
	            "course": "MSAE-3010: Introduction to Materials Science",
	            "courseid": "f19-3010",
	            "description": "This course is an introduction to nuclear physics.",
	            "month": "August",
	            "organization": "Columbia University",
	            "position": "professor",
	            "semester": "Fall",
	            "syllabus": "https://drive.google.com/open?id=0BxUpd34yizZreDBCMEJNY2FUbnc",
	            "year": 2019
	        }
	    ],
	    "title": "Dr."
	}
	{
	    "_id": "scopatz",
	    "aka": [
	        "Scopatz",
	        "Scopatz, A",
	        "Scopatz, A.",
	        "Scopatz, A M",
	        "Anthony Michael Scopatz"
	    ],
	    "appointments": {
	        "f19": {
	            "begin_day": 1,
	            "begin_month": 2,
	            "begin_year": 2019,
	            "end_day": 31,
	            "end_month": 3,
	            "end_year": 2019,
	            "grant": "dmref15",
	            "loading": 0.75,
	            "notes": [
	                "forgetmenot"
	            ],
	            "status": "finalized",
	            "type": "pd"
	        },
	        "s20": {
	            "begin_date": "2020-01-01",
	            "end_date": "2020-05-15",
	            "grant": "sym",
	            "loading": 1.0,
	            "notes": [
	                "fully appointed",
	                "outdated grant"
	            ],
	            "status": "finalized",
	            "type": "pd"
	        },
	        "ss20": {
	            "begin_date": "2020-06-01",
	            "end_date": "2020-08-31",
	            "grant": "abc42",
	            "loading": 0.8,
	            "notes": [],
	            "status": "proposed",
	            "type": "ss"
	        },
	        "ss21": {
	            "begin_date": "2020-09-01",
	            "end_date": "2021-08-31",
	            "grant": "future_grant",
	            "loading": 1.0,
	            "notes": [],
	            "status": "proposed",
	            "type": "ss"
	        }
	    },
	    "avatar": "https://avatars1.githubusercontent.com/u/320553?v=3&s=200",
	    "bio": "Anthony Scopatz is currently an Assistant Professor",
	    "bios": [
	        "Anthony Scopatz is currently an Assistant Professor but will go on to do great things"
	    ],
	    "committees": [
	        {
	            "day": 1,
	            "level": "department",
	            "month": 3,
	            "name": "Heather Stanford",
	            "type": "phdoral",
	            "unit": "apam",
	            "year": 2020
	        },
	        {
	            "day": 1,
	            "level": "school",
	            "month": 3,
	            "name": "Heather Stanford",
	            "type": "promotion",
	            "unit": "seas",
	            "year": 2020
	        },
	        {
	            "day": 1,
	            "level": "external",
	            "month": 3,
	            "name": "Heather Stanford",
	            "notes": "something else to remember about it, not published",
	            "type": "phddefense",
	            "unit": "U Denmark",
	            "year": 2020
	        },
	        {
	            "day": 1,
	            "level": "university",
	            "month": 3,
	            "name": "Heather Stanford",
	            "type": "promotion",
	            "unit": "columbiau",
	            "year": 2020
	        }
	    ],
	    "education": [
	        {
	            "advisor": "scopatz",
	            "begin_year": 2008,
	            "degree": "Ph.D. Mechanical Engineering, Nuclear and Radiation Engineering Program",
	            "department": "apam",
	            "end_year": 2011,
	            "group": "ergs",
	            "institution": "The University of Texas at Austin",
	            "location": "Austin, TX",
	            "other": [
	                "Adviser: Erich A. Schneider",
	                "Dissertation: Essential Physics for Fuel Cycle Modeling & Analysis"
	            ]
	        },
	        {
	            "begin_year": 2006,
	            "degree": "M.S.E. Mechanical Engineering, Nuclear and Radiation Engineering Program",
	            "end_year": 2007,
	            "institution": "The University of Texas at Austin",
	            "location": "Austin, TX",
	            "other": [
	                "Adviser: Erich A. Schneider",
	                "Thesis: Recyclable Uranium Options under the Global Nuclear Energy Partnership"
	            ]
	        },
	        {
	            "begin_day": 1,
	            "begin_month": "Sep",
	            "begin_year": 2002,
	            "degree": "B.S. Physics",
	            "end_day": 20,
	            "end_month": 5,
	            "end_year": 2006,
	            "institution": "University of California, Santa Barbara",
	            "location": "Santa Barbara, CA",
	            "other": [
	                "Graduated with a Major in Physics and a Minor in Mathematics"
	            ]
	        },
	        {
	            "begin_year": 2008,
	            "degree": "ongoing",
	            "department": "earth",
	            "group": "life",
	            "institution": "solar system",
	            "location": "land, mostly"
	        }
	    ],
	    "email": "scopatz@cec.sc.edu",
	    "employment": [
	        {
	            "advisor": "scopatz",
	            "begin_year": 2015,
	            "coworkers": [
	                "afriend"
	            ],
	            "group": "ergs",
	            "location": "Columbia, SC",
	            "organization": "The University of South Carolina",
	            "other": [
	                "Cyclus: An agent-based, discrete time nuclear fuel cycle simulator.",
	                "PyNE: The Nuclear Engineering Toolkit.",
	                "Website: http://www.ergs.sc.edu/"
	            ],
	            "permanent": true,
	            "position": "assistant professor",
	            "position_full": "Assistant Professor, Mechanical Engineering Department",
	            "status": "ms"
	        },
	        {
	            "advisor": "scopatz",
	            "begin_day": 1,
	            "begin_month": "Jun",
	            "begin_year": 2013,
	            "department": "Physics",
	            "end_day": 15,
	            "end_month": 3,
	            "end_year": 2015,
	            "location": "Madison, WI",
	            "organization": "CNERG, The University of Wisconsin-Madison",
	            "other": [
	                "Cyclus: An agent-based, discrete time nuclear fuel cycle simulator.",
	                "PyNE: The Nuclear Engineering Toolkit.",
	                "Website: https://cnerg.github.io/"
	            ],
	            "position": "associate scientist",
	            "position_full": "Associate Scientist, Engineering Physics Department",
	            "status": "undergrad"
	        },
	        {
	            "begin_day": 1,
	            "begin_month": "Nov",
	            "begin_year": 2011,
	            "end_month": "May",
	            "end_year": 2013,
	            "location": "Chicago, IL",
	            "organization": "The FLASH Center, The University of Chicago",
	            "other": [
	                "NIF: Simulation of magnetic field generation from neutral plasmas using FLASH.",
	                "CosmoB: Simulation of magnetic field generation from neutral plasmas using FLASH.",
	                "FLASH4: High-energy density physics capabilities and utilities.",
	                "Simulated Diagnostics: Schlieren, shadowgraphy, Langmuir probes, etc. from FLASH.",
	                "OpacPlot: HDF5-based equation of state and opacity file format.",
	                "Website: http://flash.uchicago.edu/site/"
	            ],
	            "position": "post-doctoral scholar",
	            "position_full": "Research Scientist, Postdoctoral Scholar",
	            "status": "pi"
	        },
	        {
	            "begin_date": "2000-01-01",
	            "end_date": "2001-12-31",
	            "location": "Chicago, IL",
	            "not_in_cv": true,
	            "organization": "Google",
	            "other": [],
	            "position": "janitor"
	        }
	    ],
	    "funding": [
	        {
	            "name": "Omega Laser User's Group Travel Award",
	            "value": 1100,
	            "year": 2013
	        },
	        {
	            "name": "NIF User's Group Travel Award",
	            "value": 1150,
	            "year": 2013
	        }
	    ],
	    "github_id": "ascopatz",
	    "google_scholar_url": "https://scholar.google.com/citations?user=dRm8f",
	    "hindex": [
	        {
	            "citations": 19837,
	            "citations_last_five": 9419,
	            "day": 19,
	            "h": 25,
	            "h_last_five": 46,
	            "month": 2,
	            "origin": "Google Scholar",
	            "since": 1991,
	            "year": 2020
	        }
	    ],
	    "home_address": {
	        "city": "The big apple",
	        "state": "plasma",
	        "street": "123 Wallabe Ln",
	        "zip": "007"
	    },
	    "initials": "AMS",
	    "membership": [
	        {
	            "begin_year": 2006,
	            "organization": "American Nuclear Society",
	            "position": "Member"
	        },
	        {
	            "begin_year": 2013,
	            "organization": "Python Software Foundation",
	            "position": "Fellow"
	        }
	    ],
	    "name": "Anthony Scopatz",
	    "orcid_id": "0000-0002-9432-4248",
	    "position": "professor",
	    "research_focus_areas": [
	        {
	            "begin_year": 2010,
	            "description": "software applied to nuclear engineering and life"
	        }
	    ],
	    "service": [
	        {
	            "month": 3,
	            "name": "International Steering Committee",
	            "notes": [
	                "something"
	            ],
	            "role": "chair",
	            "type": "profession",
	            "year": 2020
	        },
	        {
	            "begin_year": 2018,
	            "end_year": 2021,
	            "name": "National Steering Committee",
	            "notes": "something",
	            "type": "profession"
	        }
	    ],
	    "skills": [
	        {
	            "category": "Programming Languages",
	            "level": "expert",
	            "name": "Python"
	        },
	        {
	            "category": "Programming Languages",
	            "level": "expert",
	            "name": "Cython"
	        }
	    ],
	    "teaching": [
	        {
	            "course": "EMCH 552: Intro to Nuclear Engineering",
	            "courseid": "EMCH 552",
	            "description": "This course is an introduction to nuclear physics.",
	            "enrollment": "tbd",
	            "month": "August",
	            "organization": "University of South Carolina",
	            "position": "professor",
	            "semester": "Spring",
	            "syllabus": "https://drive.google.com/open?id=0BxUpd34yizZreDBCMEJNY2FUbnc",
	            "year": 2017
	        },
	        {
	            "course": "EMCH 558/758: Reactor Power Systems",
	            "courseid": "EMCH 558",
	            "description": "This course covers conventional reactors.",
	            "enrollment": 28,
	            "evaluation": {
	                "amount_learned": 3.5,
	                "approachability": 4.3,
	                "appropriateness_workload": 3.15,
	                "classroom_delivery": 4,
	                "comments": [
	                    "super duper",
	                    "dandy"
	                ],
	                "course_overall": 3.67,
	                "fairness_grading": 3.54,
	                "instructor_overall": 3.5,
	                "organization": 3.25,
	                "response_rate": 66.76
	            },
	            "month": "January",
	            "organization": "University of South Carolina",
	            "position": "professor",
	            "syllabus": "https://docs.google.com/document/d/1uMAx_KFZK9ugYyF6wWtLLWgITVhaTBkAf8-PxiboYdM/edit?usp=sharing",
	            "year": 2017
	        }
	    ],
	    "title": "Dr."
	}
