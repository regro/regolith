People
======
This collection describes the members of the research group.  This is normally public
data.

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

	:end_month: string, optional
	:gpa: ('float', 'string'), optional
	:begin_month: string, optional
	:location: string, optional
	:begin_year: integer, optional
	:other: string, optional
	:degree: string, optional
	:end_year: integer, optional
	:institution: string, optional
:email: string, email address of the group member, optional
:employment: list, Employment information, similar to educational information., required

	:end_month: string, optional
	:position: string, optional
	:begin_month: string, optional
	:location: string, optional
	:begin_year: integer, optional
	:other: string, optional
	:end_year: integer, optional
	:organization: string, optional
:funding: list, Funding and scholarship that the group member has individually obtained in the past. **WARNING:** this is not to be confused with the **grants** collection, optional

	:year: integer, optional
	:name: string, optional
	:duration: string, optional
	:currency: string, optional
	:value: ('float', 'integer'), optional
	:month: string, optional
:honors: list, Honors that have been awarded to this group member, optional

	:name: string, optional
	:year: integer, optional
	:description: string, optional
	:month: string, optional
:membership: list, Profesional organizations this member is a part of, optional

	:end_month: string, optional
	:description: string, optional
	:begin_month: string, optional
	:begin_year: integer, optional
	:position: string, optional
	:website: string, optional
	:end_year: integer, optional
	:organization: string, optional
:name: string, Full, canonical name for the person, required
:position: string, such as professor, graduate student, or scientist, required
:service: list, Service that this group member has provided, optional

	:name: string, optional
	:year: integer, optional
	:description: string, optional
	:month: string, optional
	:duration: string, optional
:skills: list, Skill the group member has, optional

	:name: string, optional
	:category: string, optional
	:level: string, optional
:teaching: list, Courses that this group member has taught, if any, optional

	:description: string, optional
	:end_year: integer, optional
	:website: string, optional
	:position: string, optional
	:end_month: string, optional
	:video: string, optional
	:year: integer, optional
	:course: string, optional
	:month: string, optional
	:syllabus: string, optional
	:materials: string, optional
	:organization: string, optional
:title: string, for example, Dr., etc., optional


YAML Example
------------

.. code-block:: yaml

	scopatz:
	  membership:
	    - begin_year: 2006
	      position: Member
	      organization: American Nuclear Society
	    - begin_year: 2013
	      position: Fellow
	      organization: Python Software Foundation
	  aka:
	    - Scopatz
	    - Scopatz, A
	    - Scopatz, A.
	    - Scopatz, A M
	    - Anthony Michael Scopatz
	  avatar: https://avatars1.githubusercontent.com/u/320553?v=3&s=200
	  education:
	    - begin_year: 2008
	      location: Austin, TX
	      other:
	        - 'Adviser: Erich A. Schneider'
	        - 'Dissertation: Essential Physics for Fuel Cycle Modeling & Analysis'
	      degree: Ph.D. Mechanical Engineering, Nuclear and Radiation Engineering Program
	      end_year: 2011
	      institution: The University of Texas at Austin
	    - begin_year: 2006
	      location: Austin, TX
	      other:
	        - 'Adviser: Erich A. Schneider'
	        - 'Thesis: Recyclable Uranium Options under the Global Nuclear Energy Partnership'
	      degree: M.S.E. Mechanical Engineering, Nuclear and Radiation Engineering Program
	      end_year: 2007
	      institution: The University of Texas at Austin
	    - begin_year: 2002
	      location: Santa Barbara, CA
	      other:
	        - Graduated with a Major in Physics and a Minor in Mathematics
	      degree: B.S. Physics
	      end_year: 2006
	      institution: University of California, Santa Barbara
	  position: professor
	  email: scopatz@cec.sc.edu
	  employment:
	    - begin_year: 2015
	      other:
	        - 'Cyclus: An agent-based, discrete time nuclear fuel cycle simulator.'
	        - 'PyNE: The Nuclear Engineering Toolkit.'
	        - 'Website: http://www.ergs.sc.edu/'
	      position: Assistant Professor, Mechanical Engineering Department
	      organization: The University of South Carolina
	      location: Columbia, SC
	    - end_year: 2015
	      begin_year: 2013
	      location: Madison, WI
	      other:
	        - 'Cyclus: An agent-based, discrete time nuclear fuel cycle simulator.'
	        - 'PyNE: The Nuclear Engineering Toolkit.'
	        - 'Website: https://cnerg.github.io/'
	      position: Associate Scientist, Engineering Physics Department
	      organization: CNERG, The University of Wisconsin-Madison
	    - end_month: May
	      end_year: 2013
	      begin_month: Nov
	      begin_year: 2011
	      location: Chicago, IL
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
	      organization: The FLASH Center, The University of Chicago
	  skills:
	    - level: expert
	      category: Programming Languages
	      name: Python
	    - level: expert
	      category: Programming Languages
	      name: Cython
	  teaching:
	    - year: 2017
	      description: This course is an introduction to nuclear physics.
	      month: August
	      organization: University of South Carolina
	      syllabus: https://drive.google.com/open?id=0BxUpd34yizZreDBCMEJNY2FUbnc
	      position: Professor
	      course: 'EMCH 552: Intro to Nuclear Engineering'
	    - year: 2017
	      description: This course covers conventional reactors.
	      month: January
	      organization: University of South Carolina
	      syllabus: https://docs.google.com/document/d/1uMAx_KFZK9ugYyF6wWtLLWgITVhaTBkAf8-PxiboYdM/edit?usp=sharing
	      position: Professor
	      course: 'EMCH 558/758: Reactor Power Systems'
	  bio: Anthony Scopatz is currently an Assistant Professor
	  title: Dr.
	  name: Anthony Scopatz
	  funding:
	    - name: Omega Laser User's Group Travel Award
	      year: 2013
	      value: 1100
	    - name: NIF User's Group Travel Award
	      year: 2013
	      value: 1150


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
	            "end_year": 2011,
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
	            "begin_year": 2002,
	            "degree": "B.S. Physics",
	            "end_year": 2006,
	            "institution": "University of California, Santa Barbara",
	            "location": "Santa Barbara, CA",
	            "other": [
	                "Graduated with a Major in Physics and a Minor in Mathematics"
	            ]
	        }
	    ],
	    "email": "scopatz@cec.sc.edu",
	    "employment": [
	        {
	            "begin_year": 2015,
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
	            "begin_year": 2013,
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
	            "position": "Research Scientist, Postdoctoral Scholar"
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
	    "position": "professor",
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
