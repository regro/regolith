People
======
This collection describes the members of the research group.  This is normally public data.

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: string, unique identifier for the group member, required
:active: boolean, If the person is an active member, default True., optional
:aka: ['string', 'list'], list of aliases (also-known-as), useful for identifying the group member in citations or elsewhere., required
:avatar: string, URL to avatar, required
:bio: string, short biographical text, required
:collab: boolean, If the person is a collaborator, default False., optional
:education: list, This contains the educational information for the group member., required

	:type: dict, optional

		:begin_day: integer, optional
		:begin_month: ['string', 'integer'], optional
		:begin_year: integer, optional
		:degree: string, optional
		:department: string, department withinthe institution, optional
		:group: string, this employment is/was ina group in groups coll, optional
		:end_day: integer, optional
		:end_month: ['string', 'integer'], optional
		:end_year: integer, optional
		:gpa: ('float', 'string'), optional
		:institution: string, optional
		:location: string, optional
		:other: list, optional
:email: string, email address of the group member, optional
:employment: list, Employment information, similar to educational information., optional

	:type: dict, optional

		:begin_day: integer, optional
		:begin_month: ['string', 'integer'], optional
		:begin_year: integer, optional
		:department: string, optional
		:end_day: integer, optional
		:end_month: ['string', 'integer'], optional
		:end_year: integer, optional
		:group: string, this employment is/was ina group in groups coll, optional
		:location: string, optional
		:organization: string, optional
		:other: list, optional
		:position: string, optional
		:status: string, optional
:funding: list, Funding and scholarship that the group member has individually obtained in the past. **WARNING:** this is not to be confused with the **grants** collection, optional

	:type: dict, optional

		:currency: string, optional
		:duration: string, optional
		:month: ['string', 'integer'], optional
		:name: string, optional
		:value: ('float', 'integer'), optional
		:year: integer, optional
:google_scholar_url: string, URL of your Google Scholar rofile, optional
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
:name: string, Full, canonical name for the person, required
:orcid_id: string, The ORCID ID of the person, optional
:position: string, such as professor, graduate student, or scientist, optional

	Allowed values: 
		* ``''``
		* undergraduate research assistant
		* graduate research assistant
		* research assistant
		* post-doctoral scholar
		* assistant scientist
		* research scientist
		* associate scientist
		* research associate
		* ajunct professor
		* programer
		* programmer
		* visiting scientist
		* research assistant professor
		* assistant professor
		* associate professor
		* professor emeritus
		* scientist
		* engineer
		* professor
:research_focus_areas: list, summary of research projects that are ongoing. Usedin Annual appraisal for example, optional

	:type: dict, optional

		:begin_year: integer, optional
		:end_year: integer, optional
		:description: string, optional
:service: list, Service that this group member has provided, optional

	:type: dict, optional

		:description: string, optional
		:duration: string, optional
		:month: ['string', 'integer'], Use month and year if the servicedoesn't extend more than one year.Otherwise use begin_year and end_year, optional
		:name: string, optional
		:year: integer, optional
		:begin_year: integer, optional
		:end_year: integer, optional
		:other: ['string', 'list'], optional
:skills: list, Skill the group member has, optional

	:type: dict, optional

		:category: string, optional
		:level: string, optional
		:name: string, optional
:teaching: list, Courses that this group member has taught, if any, optional

	:type: dict, optional

		:course: string, optional
		:description: string, optional
		:end_month: ['string', 'integer'], optional
		:end_year: integer, optional
		:materials: string, optional
		:month: ['string', 'integer'], optional
		:organization: string, optional
		:position: string, optional
		:syllabus: string, optional
		:video: string, optional
		:website: string, optional
		:year: integer, optional
:title: string, for example, Dr., etc., optional


YAML Example
------------

.. code-block:: yaml

	scopatz:
	  aka:
	    - Scopatz
	    - Scopatz, A
	    - Scopatz, A.
	    - Scopatz, A M
	    - Anthony Michael Scopatz
	  avatar: https://avatars1.githubusercontent.com/u/320553?v=3&s=200
	  bio: Anthony Scopatz is currently an Assistant Professor
	  education:
	    - begin_year: 2008
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
	    - begin_year: 2015
	      group: ergs
	      location: Columbia, SC
	      organization: The University of South Carolina
	      other:
	        - 'Cyclus: An agent-based, discrete time nuclear fuel cycle simulator.'
	        - 'PyNE: The Nuclear Engineering Toolkit.'
	        - 'Website: http://www.ergs.sc.edu/'
	      position: Assistant Professor, Mechanical Engineering Department
	    - begin_day: 1
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
	      position: Associate Scientist, Engineering Physics Department
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
	      position: Research Scientist, Postdoctoral Scholar
	      status: PI
	  funding:
	    - name: Omega Laser User's Group Travel Award
	      value: 1100
	      year: 2013
	    - name: NIF User's Group Travel Award
	      value: 1150
	      year: 2013
	  google_scholar_url: https://scholar.google.com/citations?user=dRm8f
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
	    - name: 'Master of Ceremonies and Organizer Brown University "Chemistry: Believe
	        it or Not" public chemistry demonstration'
	      year: 2013
	    - begin_year: 2012
	      end_year: 2014
	      name: Renewable Energy Presenter and Facility Tour Guide at the NSLS "Science
	        Sunday" laboratory open house at Brookhaven National Laboratory
	  skills:
	    - category: Programming Languages
	      level: expert
	      name: Python
	    - category: Programming Languages
	      level: expert
	      name: Cython
	  teaching:
	    - course: 'EMCH 552: Intro to Nuclear Engineering'
	      description: This course is an introduction to nuclear physics.
	      month: August
	      organization: University of South Carolina
	      position: Professor
	      syllabus: https://drive.google.com/open?id=0BxUpd34yizZreDBCMEJNY2FUbnc
	      year: 2017
	    - course: 'EMCH 558/758: Reactor Power Systems'
	      description: This course covers conventional reactors.
	      month: January
	      organization: University of South Carolina
	      position: Professor
	      syllabus: https://docs.google.com/document/d/1uMAx_KFZK9ugYyF6wWtLLWgITVhaTBkAf8-PxiboYdM/edit?usp=sharing
	      year: 2017
	  title: Dr.


JSON/Mongo Example
------------------

.. code-block:: json

	{
	    "_id": "scopatz",
	    "aka": [
	        "Scopatz",
	        "Scopatz, A",
	        "Scopatz, A.",
	        "Scopatz, A M",
	        "Anthony Michael Scopatz"
	    ],
	    "avatar": "https://avatars1.githubusercontent.com/u/320553?v=3&s=200",
	    "bio": "Anthony Scopatz is currently an Assistant Professor",
	    "education": [
	        {
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
	            "begin_year": 2015,
	            "group": "ergs",
	            "location": "Columbia, SC",
	            "organization": "The University of South Carolina",
	            "other": [
	                "Cyclus: An agent-based, discrete time nuclear fuel cycle simulator.",
	                "PyNE: The Nuclear Engineering Toolkit.",
	                "Website: http://www.ergs.sc.edu/"
	            ],
	            "position": "Assistant Professor, Mechanical Engineering Department"
	        },
	        {
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
	            "position": "Associate Scientist, Engineering Physics Department"
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
	            "position": "Research Scientist, Postdoctoral Scholar",
	            "status": "PI"
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
	            "name": "Master of Ceremonies and Organizer Brown University \"Chemistry: Believe it or Not\" public chemistry demonstration",
	            "year": 2013
	        },
	        {
	            "begin_year": 2012,
	            "end_year": 2014,
	            "name": "Renewable Energy Presenter and Facility Tour Guide at the NSLS \"Science Sunday\" laboratory open house at Brookhaven National Laboratory"
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
	            "description": "This course is an introduction to nuclear physics.",
	            "month": "August",
	            "organization": "University of South Carolina",
	            "position": "Professor",
	            "syllabus": "https://drive.google.com/open?id=0BxUpd34yizZreDBCMEJNY2FUbnc",
	            "year": 2017
	        },
	        {
	            "course": "EMCH 558/758: Reactor Power Systems",
	            "description": "This course covers conventional reactors.",
	            "month": "January",
	            "organization": "University of South Carolina",
	            "position": "Professor",
	            "syllabus": "https://docs.google.com/document/d/1uMAx_KFZK9ugYyF6wWtLLWgITVhaTBkAf8-PxiboYdM/edit?usp=sharing",
	            "year": 2017
	        }
	    ],
	    "title": "Dr."
	}
