People
============
This collection describes the members of the research group.  This is normally public
data.

Schema
------
The following lists key names mapped to its type and meaning for each entry.

:_id: str, unique identifier for the group member
:name: str, Full, canonical name for the person
:title: str, for example, Dr., etc.
:position: str, such as professor, graduate student, or scientist
:email: str, email address of the group member, optional.
:aka: list of str,  list of aliases (also-known-as), useful for identifying
    the group member in citations or elsewhere.
:avatar: str, URL to avatar
:bio: str, short biographical text
:active: bool, If the person is an active member, default True.
:collab: bool, If the person is a collaborator, default False.
:education: list of dictionaries, This contains the educational information for
    the group member.  These dicts have the following form:

    .. code-block:: python

        [{"institution": str,
          "location": str,
          "degree": str,
          "begin_year": int,
          "begin_month": str, # optional
          "end_year": int,
          "end_month": str,  # optional
          "gpa": float or str, # optional
          "other": [str], # list of strings of other pieces of information
          },
          ...
          ]

:employment: list of dicts, Employment information, similar to educational information.
    These dicts have the following form:

    .. code-block:: python

        [{"organization": str,
          "location": str,
          "position": str,
          "begin_year": int,
          "begin_month": str, # optional
          "end_year": int,
          "end_month": str,  # optional
          "other": [str], # list of strings of other pieces of information
          },
          ...
          ]

:funding: list of dicts, Funding and scholarship that the group member has
    individually obtained in the past (optional). **WARNING:** this is not to be confused
    with the **grants** collection, that may refee back to group members.
    These dicts have the following form:

    .. code-block:: python

        [{"name": str,
          "value": float,
          "currency": str, # optional, defaults to "$"
          "year": int,
          "month": str, # optional
          "duration": str or int, # optional length of award
          },
          ...
          ]

:service: list of dicts, Service that this group member has provided (optional).
    These dicts have the following form:

    .. code-block:: python

        [{"name": str,
          "description": str, # optional
          "year": int,
          "month": str, # optional
          "duration": str or int, # optional length of service
          },
          ...
          ]

:honors: list of dicts, Honors that have been awarded to this group member (optional).
    These dicts have the following form:

    .. code-block:: python

        [{"name": str,
          "description": str, # optional
          "year": int,
          "month": str, # optional
          },
          ...
          ]

:teaching: list of dicts, Courses that this group member has taught, if any (optional).
    These dicts have the following form:

    .. code-block:: python

        [{"course": str,  # name of the course
          "organization": str,
          "position": str,
          "year": int,
          "month": str, # optional
          "end_year": int, # optional
          "end_month": str,  # optional
          "description": str, # optional
          "website": str,  # optional URL
          "syllabus": str,  # optional URL
          "video": str,  # optional URL
          "materials": str,  # optional URL
          },
          ...
          ]

:membership: list of dicts, Profesional organizations this member is a part of (optional).
    These dicts have the following form:

    .. code-block:: python

        [{"organization": str,
          "position": str,
          "description": str, # optional
          "begin_year": int,
          "begin_month": str, # optional
          "end_year": int, # optional
          "end_month": str,  # optional
          "website": str,  # optional URL
          },
          ...
          ]

:skills: list of dicts, Skill the group member has (optional)
    These dicts have the following form:

    .. code-block:: python

        [{"name": str,
          "category": str,
          "level": str
          },
          ...
          ]



YAML Example
------------

.. code-block:: yaml

    scopatz:
      name: Anthony Scopatz
      position: professor
      title: Dr.
      email: scopatz@cec.sc.edu
      aka:
        - Scopatz, A. M.
        - Scopatz, Anthony
        - Scopatz, Anthony M
        - Scopatz, Anthony M.
        - A. M. Scopatz
        - Anthony M Scopatz
        - Anthony M. Scopatz
        - Anthony Michael Scopatz
      avatar: https://avatars1.githubusercontent.com/u/320553?v=3&s=200
      bio: Anthony Scopatz is currently an Assistant Professor at the University of South
        Carolina in the Nuclear Engineering program in the Mechanical Engineering Department.
        He is a computational physicist and long time Python developer. Anthony holds
        his BS in Physics from UC, Santa Barbara and a Ph.D. in Mechanical / Nuclear Engineering
        from UT Austin. A former Enthought employee, he spent his post-doctoral studies
        at the FLASH Center at the University of Chicago in the Astrophysics Department.
        Then he became a Staff Scientist at the University of Wisconsin-Maidson in Engineering
        Physics. Anthony's research interests revolve around essential physics modeling
        of the nuclear fuel cycle, and information theory & entropy. Anthony is proudly
        a fellow of the Python Software Foundation and has published and spoken at numerous
        conferences on a variety of science & software development topics.
      education:
        - begin_year: 2008
          degree: Ph.D. Mechanical Engineering, Nuclear and Radiation Engineering Program
          end_year: 2011
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
        - begin_year: 2002
          degree: B.S. Physics
          end_year: 2006
          institution: University of California, Santa Barbara
          location: Santa Barbara, CA
          other:
            - Graduated with a Major in Physics and a Minor in Mathematics
      employment:
        - begin_year: 2015
          location: Columbia, SC
          organization: The University of South Carolina
          other:
            - 'Cyclus: An agent-based, discrete time nuclear fuel cycle simulator.'
            - 'PyNE: The Nuclear Engineering Toolkit.'
            - 'Website: http://www.ergs.sc.edu/'
          position: Assistant Professor, Mechanical Engineering Department
        - begin_year: 2013
          end_year: 2015
          location: Madison, WI
          organization: CNERG, The University of Wisconsin-Madison
          other:
            - 'Cyclus: An agent-based, discrete time nuclear fuel cycle simulator.'
            - 'PyNE: The Nuclear Engineering Toolkit.'
            - 'Website: https://cnerg.github.io/'
          position: Associate Scientist, Engineering Physics Department
        - begin_month: Nov
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
          position: Research Scientist, Postdoctoral Scholar, Astronomy & Astrophysics
            Dept.
        - begin_month: May
          begin_year: 2010
          end_month: October
          end_year: 2011
          location: Austin, TX
          organization: Enthought, Inc.
          other:
            - 'PlotTool: Time series data visualization for J.P. Morgan Chase.'
            - 'PivotTable: Data cube configuration, management, and visualization for
              J.P. Morgan Chase.'
            - 'WIPP-PA: Waste Isolation Pilot Project Performance Assessment tool for
              Sandia Nat’l Labs.'
            - 'EasyGuide2: Dental implant imaging software for Keystone Dental.'
          position: Scientific Software Developer
        - begin_year: 2002
          end_year: 2005
          location: Santa Barbara, CA
          organization: University of California, Santa Barbara
          other:
            - Terahertz Continuous Wave Spectroscopy
            - Studied the effect of Terahertz waves on biomacromolecules in water.
          position: Undergraduate Research Assistant
        - begin_month: June
          begin_year: 2004
          end_month: August
          end_year: 2004
          location: Los Alamos, NM
          organization: Los Alamos National Laboratory
          other:
            - Terahertz Pump-Probe Spectroscopy
            - Looked at the effect of Terahertz waves on Erbium-Arsenide on a Gallium-Arsenide
              substrate.
          position: Summer Internship/Visiting Scientist
      funding:
        - name: Omega Laser User's Group Travel Award
          value: 1100
          year: 2013
        - name: NIF User's Group Travel Award
          value: 1150
          year: 2013
        - name: Innovations in Fuel Cycle Research, 2nd place Systems Engineering and
            Analysis
          value: 2500
          year: 2010
        - name: 'MCNPX Bug #100'
          value: 20
          year: 2009
      membership:
        - begin_year: 2006
          organization: American Nuclear Society
          position: Member
        - begin_year: 2013
          organization: Python Software Foundation
          position: Fellow
        - begin_year: 2011
          end_year: 2014
          organization: NumFOCUS
          position: Founding Treasurer & Board Member
          website: http://numfocus.org
      service:
        - name: SciPy 2014 Communications Chair
          year: 2014
        - name: SciPy 2013 Communications Chair
          year: 2013
        - name: SciPy 2012 Open Spaces Chair
          year: 2012
        - name: SciPy 2011 Chair of Python & Core Technologies Track
          year: 2011
        - name: PyCon 2010 Program Committee Member
          year: 2010
        - name: Peer Reviewer for Nuclear Engineering & Design (NED-D-09-00256)
          year: 2009
      skills:
        - category: Programming Languages
          level: expert
          name: Python
        - category: Programming Languages
          level: expert
          name: Cython
        - category: Programming Languages
          level: expert
          name: C
        - category: Programming Languages
          level: expert
          name: C++
        - category: Programming Languages
          level: expert
          name: Bash
        - category: Specialized Software
          level: expert
          name: Linux
        - category: Specialized Software
          level: intermediate
          name: MongoDB
      teaching:
        - course: 'EMCH 552: Intro to Nuclear Engineering'
          description: This course is an introduction to nuclear physics and engineering,
            covering the important underlying science and mathematics to nuclear power
            generation. Unlike previous sememsters, this course was taught in a flipped
            style.
          month: August
          organization: University of South Carolina
          position: Professor
          syllabus: https://drive.google.com/open?id=0BxUpd34yizZreDBCMEJNY2FUbnc
          year: 2017
        - course: 'EMCH 558/758: Reactor Power Systems'
          description: This course covers conventional Pressurized Water Reactors (PWR)
            and Boiling Water Reactors (BWR) system energy designs for transport, containment,
            and accident prevention and mitigation. Near term, developmental, and proposed
            enhanced capability reactor system designs. Cross listed as an undergraduate
            and graduate course.
          month: January
          organization: University of South Carolina
          position: Professor
          syllabus: https://docs.google.com/document/d/1uMAx_KFZK9ugYyF6wWtLLWgITVhaTBkAf8-PxiboYdM/edit?usp=sharing
          year: 2017


JSON/Mongo Example
------------------

.. code-block:: json

    {"_id": "scopatz",
     "name": "Anthony Scopatz",
     "position": "professor",
     "title": "Dr.",
     "aka": ["Scopatz", "Scopatz, A", "Scopatz, A.", "Scopatz, A M", "Anthony Michael Scopatz"],
     "avatar": "https://avatars1.githubusercontent.com/u/320553?v=3&s=200",
     "email": "scopatz@cec.sc.edu",
     "bio": "Anthony Scopatz is currently an Assistant Professor",
     "education": [{"begin_year": 2008,
                    "degree": "Ph.D. Mechanical Engineering, Nuclear and Radiation Engineering Program",
                    "end_year": 2011,
                    "institution": "The University of Texas at Austin",
                    "location": "Austin, TX",
                    "other": ["Adviser: Erich A. Schneider",
                              "Dissertation: Essential Physics for Fuel Cycle Modeling & Analysis"]},
                   {"begin_year": 2006,
                    "degree": "M.S.E. Mechanical Engineering, Nuclear and Radiation Engineering Program",
                    "end_year": 2007,
                    "institution": "The University of Texas at Austin",
                    "location": "Austin, TX",
                    "other": ["Adviser: Erich A. Schneider",
                              "Thesis: Recyclable Uranium Options under the Global Nuclear Energy Partnership"]},
                   {"begin_year": 2002,
                    "degree": "B.S. Physics",
                    "end_year": 2006,
                    "institution": "University of California, Santa Barbara",
                    "location": "Santa Barbara, CA",
                    "other": ["Graduated with a Major in Physics and a Minor in Mathematics"]}],
     "employment": [{"begin_year": 2015,
                     "location": "Columbia, SC",
                     "organization": "The University of South Carolina",
                     "other": ["Cyclus: An agent-based, discrete time nuclear fuel cycle simulator.",
                               "PyNE: The Nuclear Engineering Toolkit.",
                               "Website: http://www.ergs.sc.edu/"],
                     "position": "Assistant Professor, Mechanical Engineering Department"},
                    {"begin_year": 2013,
                     "end_year": 2015,
                     "location": "Madison, WI",
                     "organization": "CNERG, The University of Wisconsin-Madison",
                     "other": ["Cyclus: An agent-based, discrete time nuclear fuel cycle simulator.",
                               "PyNE: The Nuclear Engineering Toolkit.",
                               "Website: https://cnerg.github.io/"],
                     "position": "Associate Scientist, Engineering Physics Department"},
                    {"begin_month": "Nov",
                     "begin_year": 2011,
                     "end_month": "May",
                     "end_year": 2013,
                     "location": "Chicago, IL",
                     "organization": "The FLASH Center, The University of Chicago",
                     "other": ["NIF: Simulation of magnetic field generation from neutral plasmas using FLASH.", "CosmoB: Simulation of magnetic field generation from neutral plasmas using FLASH.",
                               "FLASH4: High-energy density physics capabilities and utilities.",
                               "Simulated Diagnostics: Schlieren, shadowgraphy, Langmuir probes, etc. from FLASH.",
                               "OpacPlot: HDF5-based equation of state and opacity file format.",
                               "Website: http://flash.uchicago.edu/site/"],
                     "position": "Research Scientist, Postdoctoral Scholar"}],
    "funding": [{"name": "Omega Laser User's Group Travel Award",
                 "value": 1100,
                 "year": 2013},
                {"name": "NIF User's Group Travel Award",
                 "value": 1150,
                 "year": 2013}],
    "membership": [{"begin_year": 2006,
                    "organization": "American Nuclear Society",
                    "position": "Member"},
                   {"begin_year": 2013,
                    "organization": "Python Software Foundation",
                    "position": "Fellow"}],
    "skills": [{"category": "Programming Languages",
                "level": "expert",
                "name": "Python"},
               {"category": "Programming Languages",
                "level": "expert",
                "name": "Cython"}],
    "teaching": [{"course": "EMCH 552: Intro to Nuclear Engineering",
                  "description": "This course is an introduction to nuclear physics.",
                  "month": "August",
                  "organization": "University of South Carolina",
                  "position": "Professor",
                  "syllabus": "https://drive.google.com/open?id=0BxUpd34yizZreDBCMEJNY2FUbnc",
                  "year": 2017},
                 {"course": "EMCH 558/758: Reactor Power Systems",
                  "description": "This course covers conventional reactors.",
                  "month": "January",
                  "organization": "University of South Carolina",
                  "position": "Professor",
                  "syllabus": "https://docs.google.com/document/d/1uMAx_KFZK9ugYyF6wWtLLWgITVhaTBkAf8-PxiboYdM/edit?usp=sharing",
                  "year": 2017}]
    }
