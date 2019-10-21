"""Database schemas, examples, and tools"""
from cerberus import Validator

from .sorters import POSITION_LEVELS

SORTED_POSITION = sorted(POSITION_LEVELS.keys(), key=POSITION_LEVELS.get)

EXEMPLARS = {
    'abstracts': {'_id': 'Mouginot.Model',
                  'coauthors': 'P.P.H. Wilson',
                  'email': 'mouginot@wisc.edu',
                  'firstname': 'Baptiste',
                  'institution': 'University of Wisconsin-Madison',
                  'lastname': 'Mouginot',
                  'references': '[1] B. MOUGINOT, “cyCLASS: CLASS '
                                'models for Cyclus,”, Figshare, '
                                'https://dx.doi.org/10.6084/'
                                'm9.figshare.3468671.v2 (2016).',
                  'text': 'The CLASS team has developed high '
                          'quality predictors based on pre-trained '
                          'neural network...',
                  'timestamp': '5/5/2017 13:15:59',
                  'title': 'Model Performance Analysis'},
    'assignments': {'_id': 'hw01-rx-power',
                    'category': 'homework',
                    'courses': ['EMCH-558-2016-S',
                                'EMCH-758-2016-S'],
                    'points': [1, 2, 3],
                    'questions': ['1-9', '1-10', '1-12']},
    'blog': {'_id': 'my-vision',
             'author': 'Anthony Scopatz',
             'day': 18,
             'month': 'September',
             'original': 'https://scopatz.com/my-vision/',
             'post': 'I would like see things move forward. Deep, I know!',
             'title': 'My Vision',
             'year': 2015},
    'citations': {'_id': 'meurer2016sympy',
                  'author': ['Meurer, Aaron',
                             'Smith, Christopher P',
                             'Paprocki, Mateusz',
                             "{\\v{C}}ert{\\'\\i}k, Ond{\\v{r}}ej",
                             'Rocklin, Matthew',
                             'Kumar, AMiT',
                             'Ivanov, Sergiu',
                             'Moore, Jason K',
                             'Singh, Sartaj',
                             'Rathnayake, Thilina',
                             'Sean Vig',
                             'Brian E Granger',
                             'Richard P Muller',
                             'Francesco Bonazzi',
                             'Harsh Gupta',
                             'Shivam Vats',
                             'Fredrik Johansson',
                             'Fabian Pedregosa',
                             'Matthew J Curry',
                             'Ashutosh Saboo',
                             'Isuru Fernando',
                             'Sumith Kulal',
                             'Robert Cimrman',
                             'Anthony Scopatz'],
                  'entrytype': 'article',
                  'journal': 'PeerJ Computer Science',
                  'month': 'Jan',
                  'pages': 'e103',
                  'publisher': 'PeerJ Inc. San Francisco, USA',
                  'title': 'SymPy: Symbolic computing in Python',
                  'volume': '4',
                  'year': '2017'},
    'courses': {'_id': 'EMCH-552-2016-F',
                'active': False,
                'department': 'EMCH',
                'number': 552,
                'scale': [[0.875, 'A'],
                          [0.8125, 'B+'],
                          [0.75, 'B'],
                          [0.6875, 'C+'],
                          [0.625, 'C'],
                          [0.5625, 'D+'],
                          [0.5, 'D'],
                          [-1.0, 'F']],
                'season': 'F',
                'students': ['Human A. Person', 'Human B. Person'],
                'syllabus': 'emch552-2016-f-syllabus.pdf',
                'weights': {'class-notes': 0.15,
                            'final': 0.3,
                            'homework': 0.35,
                            'midterm': 0.2},
                'year': 2016},
    'grades': {
        '_id': 'Human A. Person-rx-power-hw02-EMCH-758-2017-S',
        'student': 'hap',
        'assignment': '2017-rx-power-hw02',
        'course': 'EMCH-758-2017-S',
        'scores': [1, 1.6, 3]},
    'grants': {'_id': 'SymPy-1.1',
               'amount': 3000.0,
               'begin_day': 1,
               'begin_month': 'May',
               'begin_year': 2017,
               'call_for_proposals': 'https://groups.google.com/d/msg'
                                     '/numfocus/wPjhdm8NJiA/S8JL1_NZDQAJ',
               'end_day': 31,
               'end_month': 'December',
               'end_year': 2017,
               'funder': 'NumFOCUS',
               'narrative': 'https://docs.google.com/document/d/1nZxqoL'
                            '-Ucni_aXLWmXtRDd3IWqW0mZBO65CEvDrsXZM/edit?usp'
                            '=sharing',
               'program': 'Small Development Grants',
               'team': [
                   {'institution': 'University of South Carolina',
                    'name': 'Anthony Scopatz',
                    'position': 'PI'},
                   {'institution': 'University of South Carolina',
                    'name': 'Aaron Meurer',
                    'position': 'researcher'}],
               'title': 'SymPy 1.1 Release Support'},
    'group': {
        '_id': 'ergs',
        'pi_name': 'Anthony Scopatz',
        'department': 'Mechanical Engineering',
        'institution': 'University of South Carolina',
        'name': 'ERGS',
        'website': 'www.ergs.sc.edu',
        'mission_statement': '''<b>ERGS</b>, or <i>Energy Research Group: 
    Scopatz</i>, is the Computational 
    <a href="http://www.me.sc.edu/nuclear/">Nuclear Engineering</a>
    research group at the 
    <a href="http://sc.edu/">University of South Carolina</a>. 
    Our focus is on uncertainty quantification & predictive modeling, nuclear fuel 
    cycle simulation, and improving nuclear engineering techniques through 
    automation.
    We are committed to open & accessible research tools and methods.''',
        'projects': '''ERGS is involved in a large number of computational 
    projects. Please visit the <a href="projects.html">projects page</a> for more 
    information!
    ''',
        'email': '<b>scopatz</b> <i>(AT)</i> <b>cec.sc.edu</b>'
    },
    'jobs': {'_id': '0004',
             'background_fields': ['Data Science',
                                   'Data Engineering',
                                   'Computer Engineering',
                                   'Computer Science',
                                   'Applied Mathematics',
                                   'Physics',
                                   'Nuclear Engineering',
                                   'Mechanical Engineering',
                                   'Or similar'],
             'compensation': [
                 'Salary and compensation will be based on prior work '
                 'experience.'],
             'contact': 'Please send CV or resume to Prof. Scopatz at '
                        'scopatzATcec.sc.edu.',
             'day': 1,
             'description': '<p>We are seeking a dedicated individual to '
                            'help to aid in ...',
             'month': 'July',
             'open': False,
             'positions': ['Scientific Software Developer',
                           'Programmer'],
             'start_date': 'ASAP',
             'title': 'Open Source Scientific Software Maintainer',
             'year': 2015},
    'news': {'_id': '56b4eb6d421aa921504ef2a9',
             'author': 'Anthony Scopatz',
             'body': 'Dr. Robert Flanagan joined ERGS as a post-doctoral '
                     'scholar.',
             'day': 1,
             'month': 'February',
             'year': 2016},
    'people': {'_id': 'scopatz',
               'aka': ['Scopatz',
                       'Scopatz, A',
                       'Scopatz, A.',
                       'Scopatz, A M',
                       'Anthony Michael Scopatz'],
               'avatar': 'https://avatars1.githubusercontent.com/u/320553?v'
                         '=3&s=200',
               'bio': 'Anthony Scopatz is currently an Assistant Professor',
               'education': [
                   {'begin_year': 2008,
                    'degree': 'Ph.D. Mechanical Engineering, '
                              'Nuclear and Radiation Engineering '
                              'Program',
                    'end_year': 2011,
                    'institution': 'The University of Texas at Austin',
                    'location': 'Austin, TX',
                    'other': [
                        'Adviser: Erich A. Schneider',
                        'Dissertation: Essential Physics for Fuel Cycle '
                        'Modeling & Analysis']},
                   {'begin_year': 2006,
                    'degree': 'M.S.E. Mechanical Engineering, Nuclear and '
                              'Radiation Engineering Program',
                    'end_year': 2007,
                    'institution': 'The University of Texas at Austin',
                    'location': 'Austin, TX',
                    'other': [
                        'Adviser: Erich A. Schneider',
                        'Thesis: Recyclable Uranium Options under the Global '
                        'Nuclear Energy Partnership']},
                   {'begin_year': 2002,
                    'degree': 'B.S. Physics',
                    'end_year': 2006,
                    'institution': 'University of California, Santa Barbara',
                    'location': 'Santa Barbara, CA',
                    'other': [
                        'Graduated with a Major in Physics and a Minor in '
                        'Mathematics']}],
               'email': 'scopatz@cec.sc.edu',
               'employment': [
                   {'begin_year': 2015,
                    'location': 'Columbia, SC',
                    'organization': 'The University of South Carolina',
                    'other': [
                        'Cyclus: An agent-based, discrete time nuclear fuel '
                        'cycle simulator.',
                        'PyNE: The Nuclear Engineering Toolkit.',
                        'Website: http://www.ergs.sc.edu/'],
                    'position': 'Assistant Professor, Mechanical Engineering '
                                'Department'},
                   {'begin_year': 2013,
                    'end_year': 2015,
                    'location': 'Madison, WI',
                    'organization': 'CNERG, The University of '
                                    'Wisconsin-Madison',
                    'other': [
                        'Cyclus: An agent-based, discrete time nuclear fuel '
                        'cycle simulator.',
                        'PyNE: The Nuclear Engineering Toolkit.',
                        'Website: https://cnerg.github.io/'],
                    'position': 'Associate Scientist, Engineering Physics '
                                'Department'},
                   {'begin_month': 'Nov',
                    'begin_year': 2011,
                    'end_month': 'May',
                    'end_year': 2013,
                    'location': 'Chicago, IL',
                    'organization': 'The FLASH Center, The University of '
                                    'Chicago',
                    'other': [
                        'NIF: Simulation of magnetic field generation from '
                        'neutral plasmas using FLASH.',
                        'CosmoB: Simulation of magnetic field generation '
                        'from neutral plasmas using FLASH.',
                        'FLASH4: High-energy density physics capabilities '
                        'and utilities.',
                        'Simulated Diagnostics: Schlieren, shadowgraphy, '
                        'Langmuir probes, etc. from FLASH.',
                        'OpacPlot: HDF5-based equation of state and opacity '
                        'file format.',
                        'Website: http://flash.uchicago.edu/site/'],
                    'position': 'Research Scientist, Postdoctoral Scholar'}],
               'funding': [
                   {'name': "Omega Laser User's Group Travel Award",
                    'value': 1100,
                    'year': 2013},
                   {
                       'name': "NIF User's Group Travel Award",
                       'value': 1150,
                       'year': 2013}],
               'membership': [{'begin_year': 2006,
                               'organization': 'American Nuclear Society',
                               'position': 'Member'},
                              {'begin_year': 2013,
                               'organization': 'Python Software Foundation',
                               'position': 'Fellow'}],
               'name': 'Anthony Scopatz',
               'position': 'professor',
               'skills': [{'category': 'Programming Languages',
                           'level': 'expert',
                           'name': 'Python'},
                          {
                              'category': 'Programming Languages',
                              'level': 'expert',
                              'name': 'Cython'}],
               'teaching': [{
                   'course': 'EMCH 552: Intro to Nuclear Engineering',
                   'description': 'This course is an introduction to nuclear '
                                  'physics.',
                   'month': 'August',
                   'organization': 'University of South Carolina',
                   'position': 'Professor',
                   'syllabus': 'https://drive.google.com/open?id'
                               '=0BxUpd34yizZreDBCMEJNY2FUbnc',
                   'year': 2017},
                   {
                       'course': 'EMCH 558/758: Reactor Power Systems',
                       'description': 'This course covers conventional '
                                      'reactors.',
                       'month': 'January',
                       'organization': 'University of South Carolina',
                       'position': 'Professor',
                       'syllabus': 'https://docs.google.com/document/d'
                                   '/1uMAx_KFZK9ugYyF6wWtLLWgITVhaTBkAf8'
                                   '-PxiboYdM/edit?usp=sharing',
                       'year': 2017}],
               'title': 'Dr.'},
    'projects': {'_id': 'Cyclus',
                 'name': 'Cyclus',
                 'description': 'Agent-Based Nuclear Fuel Cycle Simulator',
                 'logo': 'http://fuelcycle.org/_static/big_c.png',
                 'other': [
                     'Discrete facilities with discrete material transactions',
                     'Low barrier to entry, rapid payback to adoption'],
                 'repo': 'https://github.com/cyclus/cyclus/',
                 'team': [{'begin_month': 'June',
                           'begin_year': 2013,
                           'end_month': 'July',
                           'end_year': 2015,
                           'name': 'Anthony Scopatz',
                           'position': 'Project Lead'}],
                 'website': 'http://fuelcycle.org/'},
    'proposals': {'_id': 'mypropsal',
                  'ammount': 1000000.0,
                  'authors': ['Anthony Scopatz',
                              'Robert Flanagan'],
                  'currency': 'USD',
                  'day': 18,
                  'durration': 3,
                  'full': {
                      'benefit_of_collaboration': 'http://pdf.com'
                                                  '/benefit_of_collaboration',
                      'cv': [
                          'http://pdf.com/scopatz-cv',
                          'http://pdf.com/flanagan-cv'],
                      'narrative': 'http://some.com/pdf'},
                  'month': 'Aug',
                  'pi': 'Anthony Scopatz',
                  'pre': {
                      'benefit_of_collaboration': 'http://pdf.com'
                                                  '/benefit_of_collaboration',
                      'cv': [
                          'http://pdf.com/scopatz-cv',
                          'http://pdf.com/flanagan-cv'],
                      'day': 2,
                      'month': 'Aug',
                      'narrative': 'http://some.com/pdf',
                      'year': 1998},
                  'status': 'submitted',
                  'title': 'A very fine proposal indeed',
                  'year': 1999},
    'students': {'_id': 'Human A. Person',
                 'aka': ['H. A. Person'],
                 'email': 'haperson@uni.edu',
                 'university_id': 'HAP42'},
}

SCHEMAS = {
    'abstracts': {
        '_description': {
            'description': 'Abstracts for a conference or workshop. This is '
                           'generally public information'},
        '_id': {
            'description': 'Unique identifier for submission. This generally '
                           'includes the author name and part of the title.',
            'required': True,
            'type': 'string'},
        'coauthors': {'description': 'names of coauthors',
                      'required': False,
                      'type': 'string'},
        'email': {'description': 'contact email for the author.',
                  'required': True,
                  'type': 'string'},
        'firstname': {'description': 'first name of the author.',
                      'required': True,
                      'type': 'string'},
        'institution': {'description': 'name of the inistitution',
                        'required': True,
                        'type': 'string'},
        'lastname': {'description': 'last name of the author.',
                     'required': True,
                     'type': 'string'},
        'references': {
            'description': 'HTML string of reference for the abstract itself',
            'required': False,
            'type': 'string'},
        'text': {'description': 'HTML string of the abstract.',
                 'required': True,
                 'type': 'string'},
        'timestamp': {
            'description': 'The time when the abstract was submitted.',
            'required': True,
            'type': 'string'},
        'title': {'description': 'title of the presentation/paper.',
                  'required': True,
                  'type': 'string'}},
    'assignments': {
        '_description': {
            'description': 'Information about assignments for classes.'},
        '_id': {
            'description': 'A unique id for the assignment, such as '
                           'HW01-EMCH-558-2016-S',
            'required': True,
            'type': 'string'},
        'category': {'description': "such as 'homework' or 'final'",
                     'required': True,
                     'type': 'string'},
        'courses': {
            'description': 'ids of the courses that have this assignment',
            'required': True,
            'type': 'string'},
        'file': {'description': 'path to assignment file in store',
                 'required': False,
                 'type': 'string'},
        'points': {
            'description': 'list of number of points possible for each '
                           'question. Length is the number of questions',
            'required': True,
            'type': ('integer', 'float')},
        'question': {
            'description': 'titles for the questions on this assignment',
            'required': False,
            'type': 'string'},
        'solution': {'description': 'path to solution file in store',
                     'required': False,
                     'type': 'string'}},
    'blog': {
        '_description': {
            'description': 'This collection represents blog posts written by '
                           'the members of the research group.'},
        '_id': {
            'description': 'short representation, such as this-is-my-title',
            'required': True,
            'type': 'string'},
        'author': {'description': 'name or AKA of author',
                   'required': True,
                   'type': 'string'},
        'day': {'description': 'Publication day',
                'required': True,
                'type': 'integer'},
        'month': {'description': 'Publication month',
                  'required': True,
                  'type': 'string'},
        'original': {
            'description': 'URL of original post, if this is a repost',
            'required': False,
            'type': 'string'},
        'post': {'description': 'actual contents of the post',
                 'required': True,
                 'type': 'string'},
        'title': {'description': 'full human readable title',
                  'required': True,
                  'type': 'string'},
        'year': {'description': 'Publication year',
                 'required': True,
                 'type': 'integer'}},
    'grades': {
        '_description': {
            'description': 'The grade for a student on an assignment. This '
                           'information should be private.'},
        '_id': {
            'description': 'unique id, typically the '
                           'student-assignment-course',
            'required': True,
            'type': 'string'},
        'assignment': {'description': 'assignment id',
                       'required': True,
                       'type': 'string'},
        'course': {
            'description': 'course id',
            'required': True,
            'type': 'string'},
        'filename': {'description': 'path to file in store',
                     'required': False,
                     'type': 'string'},
        'scores': {
            'description': 'the number of points earned on each question',
            'required': True,
            'type': ('integer', 'float')},
        'student': {'description': 'student id',
                    'required': True,
                    'type': 'string'}},
    'grants': {
        '_description': {
            'description': 'This collection represents grants that have been '
                           'awarded to the group.'},
        '_id': {'description': 'short representation, such as this-is-my-name',
                'required': True,
                'type': ('string', 'integer', 'float')},
        'amount': {'description': 'value of award',
                   'required': True,
                   'type': ('integer', 'float')},
        'begin_day': {'description': 'start day of the grant',
                      'required': False,
                      'type': 'integer'},
        'begin_month': {'description': 'start month of the grant',
                        'required': True,
                        'type': 'string'},
        'begin_year': {'description': 'start year of the grant',
                       'required': True,
                       'type': 'integer'},
        'benefit_of_collaboration': {'description': '',
                                     'required': False,
                                     'type': 'string'},
        'call_for_proposals': {'description': '',
                               'required': False,
                               'type': 'string'},
        'currency': {'description': "typically '$' or 'USD'",
                     'required': False,
                     'type': 'string'},
        'end_day': {'description': 'end day of the grant',
                    'required': False,
                    'type': ('string', 'integer')},
        'end_month"': {'description': 'end month of the grant',
                       'required': False,
                       'type': 'string'},
        'end_year': {'description': 'end year of the grant',
                     'required': True,
                     'type': 'integer'},
        'funder': {'description': 'the agency funding the work',
                   'required': True,
                   'type': 'string'},
        'grant_id': {'description': 'the identifier for this work',
                     'required': False,
                     'type': 'string'},
        'narrative': {'description': '', 'required': False, 'type': 'string'},
        'program': {'description': 'the program the work was funded under',
                    'required': True,
                    'type': 'string'},
        'status': {'allowed': ['pending', 'declined', 'accepted', 'in-prep'],
                   'description': 'status of the grant',
                   'required': True,
                   'type': 'string'},
        'team': {
            'description': 'information about the team members participating '
                           'in the grant.',
            'required': True,
            'schema': {'schema': {'cv': {'required': False, 'type': 'string'},
                                  'institution': {
                                      'required': True,
                                      'type': 'string'},
                                  'name': {'required': True, 'type': 'string'},
                                  'position': {
                                      'required': True,
                                      'type': 'string'},
                                  'subaward_amount': {
                                      'required': False,
                                      'type': ('integer', 'float')}},
                       'type': 'dict'},
            'type': 'list'},
        'title': {'description': 'actual title of proposal / grant',
                  'required': True,
                  'type': 'string'}},
    'group': {
        '_description': {'description': 'Information about the research group'
                                        'this is generally public information'},
        '_id': {
            'description': 'Unique identifier for submission. This generally '
                           'includes the author name and part of the title.',
            'required': True,
            'type': 'string'},
        'pi_name': {'description': 'The name of the Principle Investigator',
                    'required': True,
                    'type': 'string'},
        'department': {'description': 'Name of host department',
                       'required': True,
                       'type': 'string'},
        'institution': {'description': 'Name of the host institution',
                        'required': True,
                        'type': 'string'},
        'name': {'description': 'Name of the group',
                 'required': True,
                 'type': 'string'},
        'website': {'description': 'URL to group webpage',
                    'type': 'string'},
        'mission_statement': {'description': 'Mission statement of the group',
                              'type': 'string'},
        'projects': {'description': 'About line for projects',
                     'type': 'string',
                     'required': True},
        'email': {'description': 'Contact email for the group',
                  'type': 'string',
                  'required': True}
    },
    'people': {
        '_description': {
            'description': 'This collection describes the members of the '
                           'research group.  This is normally public data.'},
        '_id': {'description': 'unique identifier for the group member',
                'required': True,
                'type': 'string'},
        'active': {
            'description': 'If the person is an active member, default True.',
            'required': False,
            'type': 'boolean'},
        'aka': {
            'description': 'list of aliases (also-known-as), useful for '
                           'identifying the group member in citations or '
                           'elsewhere.',
            'required': True,
            'type': ['string', 'list']},
        'avatar': {'description': 'URL to avatar',
                   'required': True,
                   'type': 'string'},
        'bio': {'description': 'short biographical text',
                'required': True,
                'type': 'string'},
        'collab': {
            'description': 'If the person is a collaborator, default False.',
            'required': False,
            'type': 'boolean'},
        'education': {
            'description': 'This contains the educational information for '
                           'the group member.',
            'required': True,
            'schema': {'type': 'dict',
                       'schema': {
                           'begin_month': {
                               'required': False,
                               'type': 'string'},
                           'begin_year': {'required': True, 'type': 'integer'},
                           'degree': {'required': True, 'type': 'string'},
                           'end_month': {'required': False, 'type': 'string'},
                           'end_year': {'required': True, 'type': 'integer'},
                           'gpa': {
                               'required': False,
                               'type': ('float', 'string')},
                           'institution': {'required': True, 'type': 'string'},
                           'location': {'required': True, 'type': 'string'},
                           'other': {'required': False, 'type': 'string'}}},
            'type': 'list'},
        'email': {'description': 'email address of the group member',
                  'required': False,
                  'type': 'string'},
        'employment': {
            'description': 'Employment information, similar to educational '
                           'information.',
            'required': True,
            'schema': {'type': 'dict',
                        'schema': {
                            'begin_month': {
                                'required': False,
                                'type': 'string'},
                            'begin_year': {
                                'required': True,
                                'type': 'integer'},
                            'end_month': {'required': False, 'type': 'string'},
                            'end_year': {'required': False, 'type': 'integer'},
                            'location': {'required': True, 'type': 'string'},
                            'organization': {
                                'required': True,
                                'type': 'string'},
                            'other': {'required': False, 'type': 'string'},
                            'position': {'required': True, 'type': 'string'}}},
            'type': 'list'},
        'funding': {
            'description': 'Funding and scholarship that the group member '
                           'has individually obtained in the past. '
                           '**WARNING:** this is not to be confused with the '
                           '**grants** collection',
            'required': False,
            'schema': {'type': 'dict',
                       'schema': {
                           'currency': {'required': False, 'type': 'string'},
                           'duration': {'required': False, 'type': 'string'},
                           'month': {'required': False, 'type': 'string'},
                           'name': {'required': True, 'type': 'string'},
                           'value': {
                               'required': True,
                               'type': ('float', 'integer')},
                           'year': {'required': True, 'type': 'integer'}}},
            'type': 'list'},
        'honors': {
            'description': 'Honors that have been awarded to this '
                           'group member',
            'required': False,
            'schema': {'type': 'dict',
                       'schema': {
                           'description': {
                               'required': False,
                               'type': 'string'},
                           'month': {'required': False, 'type': 'string'},
                           'name': {'required': True, 'type': 'string'},
                           'year': {'required': True, 'type': 'integer'}}},
            'type': 'list'},
        'membership': {
            'description': 'Professional organizations this member is '
                           'a part of',
            'required': False,
            'schema': {'type': 'dict',
                       'schema': {
                           'begin_month': {
                               'required': False,
                               'type': 'string'},
                           'begin_year': {'required': True, 'type': 'integer'},
                           'description': {
                               'required': False,
                               'type': 'string'},
                           'end_month': {'required': False, 'type': 'string'},
                           'end_year': {'required': False, 'type': 'integer'},
                           'organization': {
                               'required': True,
                               'type': 'string'},
                           'position': {'required': True, 'type': 'string'},
                           'website': {'required': False, 'type': 'string'}}},
            'type': 'list'},
        'name': {'description': 'Full, canonical name for the person',
                 'required': True,
                 'type': 'string'},
        'position': {
            'description': 'such as professor, graduate student, or scientist',
            'required': True,
            'type': 'list', 'allowed': list(SORTED_POSITION)},
        'service': {
            'description': 'Service that this group member has provided',
            'required': False,
            'schema': {'type': 'dict',
                       'schema': {
                           'description': {
                               'required': False,
                               'type': 'string'},
                           'duration': {'required': False, 'type': 'string'},
                           'month': {'required': False, 'type': 'string'},
                           'name': {'required': True, 'type': 'string'},
                           'year': {'required': True, 'type': 'integer'}}},
            'type': 'list'},
        'skills': {'description': 'Skill the group member has',
                   'required': False,
                   'schema': {'type': 'dict',
                              'schema': {
                                  'category': {
                                      'required': True,
                                      'type': 'string'},
                                  'level': {
                                      'required': True,
                                      'type': 'string'},
                                  'name': {
                                      'required': True,
                                      'type': 'string'}}},
                   'type': 'list'},
        'teaching': {
            'description': 'Courses that this group member has taught, if any',
            'required': False,
            'schema': {'type': 'dict',
                       'schema': {
                           'course': {'required': True, 'type': 'string'},
                           'description': {
                               'required': False,
                               'type': 'string'},
                           'end_month': {'required': False, 'type': 'string'},
                           'end_year': {'required': False, 'type': 'integer'},
                           'materials': {'required': False, 'type': 'string'},
                           'month': {'required': False, 'type': 'string'},
                           'organization': {
                               'required': True,
                               'type': 'string'},
                           'position': {'required': True, 'type': 'string'},
                           'syllabus': {'required': False, 'type': 'string'},
                           'video': {'required': False, 'type': 'string'},
                           'website': {'required': False, 'type': 'string'},
                           'year': {'required': True, 'type': 'integer'}}},
            'type': 'list'},
        'title': {'description': 'for example, Dr., etc.',
                  'required': False,
                  'type': 'string'}},
    'projects': {
        '_description': {
            'description': 'This collection describes the research group '
                           'projects. This is normally public data.'},
        '_id': {'description': 'Unique project identifier.',
                'required': True,
                'type': 'string'},
        'description': {'description': 'brief project description.',
                        'required': True,
                        'type': 'string'},
        'grant': {
            'description': 'Grant id if there is a grant supporting this '
                           'project',
            'type': 'string'},
        'logo': {'description': 'URL to the project logo',
                 'required': False,
                 'type': 'string'},
        'name': {'description': 'name of the project.',
                 'required': True,
                 'type': 'string'},
        'other': {'description': 'other information about the project',
                  'required': False,
                  'type': ['list', 'string']},
        'repo': {'description': 'URL of the source code repo, if available',
                 'required': False,
                 'type': 'string'},
        'team': {
            'description': 'People who are/have been working on this project.',
            'required': True,
            'schema': {'type': 'dict',
                       'schema': {
                           'begin_month': {
                               'required': False,
                               'type': 'string'},
                           'begin_year': {'required': True, 'type': 'integer'},
                           'end_month': {'required': False, 'type': 'string'},
                           'end_year': {'required': False, 'type': 'integer'},
                           'name': {'required': True, 'type': 'string'},
                           'position': {'required': True, 'type': 'string'}}},
            'type': 'list'},
        'website': {'description': 'URL of the website.',
                    'required': True,
                    'type': 'string'}},
    'proposals': {
        '_description': {
            'description': 'This collection represents proposals that have '
                           'been submitted by the group.'},
        '_id': {'description': 'short representation, such as this-is-my-name',
                'required': True,
                'type': ('string', 'integer', 'float')},
        'amount': {'description': 'value of award',
                   'required': True,
                   'type': ('integer', 'float')},
        'authors': {'description': 'other investigator names',
                    'required': True,
                    'type': 'string'},
        'currency': {'description': "typically '$' or 'USD'",
                     'required': True,
                     'type': 'string'},
        'day': {'description': 'day that the proposal is due',
                'required': True,
                'type': 'integer'},
        'duration': {'description': 'number of years',
                     'required': True,
                     'type': ('integer', 'float')},
        'month': {'description': 'month that the proposal is due',
                  'required': True,
                  'type': 'string'},
        'pi': {'description': 'principal investigator name',
               'required': True,
               'type': 'string'},
        'pre': {'description': 'Information about the pre-proposal',
                'required': False,
                'type': 'dict'},
        'status': {'description': "e.g. 'submitted', 'accepted', 'rejected'",
                   'required': True,
                   'type': 'string'},
        'title': {'description': 'actual title of proposal',
                  'required': True,
                  'type': 'string'},
        'year': {'description': 'Year that the proposal is due',
                 'required': True,
                 'type': 'integer'}},
    'students': {
        '_description': {
            'description': 'This is a collection of student names and '
                           'metadata. This should probably be private.'},
        '_id': {'description': 'short representation, such as this-is-my-name',
                'required': True,
                'type': 'string'},
        'aka': {'description': 'list of aliases',
                'required': False,
                'schema': {'type': 'string'},
                'type': ('list', 'string')},
        'email': {'description': 'email address',
                  'required': False,
                  'type': 'string'},
        'university_id': {
            'description': 'The university identifier for the student',
            'required': False,
            'type': 'string'}},
}


class NoDescriptionValidator(Validator):
    def _validate_description(self, description, field, value):
        if False:
            pass


def validate(coll, record, schemas):
    """Validate a record for a given db

    Parameters
    ----------
    coll : str
        The name of the db in question
    record : dict
        The record to be validated
    schemas : dict
        The schema to validate against

    Returns
    -------
    rtn : bool
        True is valid
    errors: dict
        The errors encountered (if any)

    """
    if coll in schemas:
        schema = schemas[coll]
        v = NoDescriptionValidator(schema)
        return v.validate(record), v.errors
    else:
        return True, ()
