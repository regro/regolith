"""Database schemas"""
schemas = {
    'grants': {
        '_id':
            {'description': 'short representation, such as this-is-my-name',
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
        'grant_id': {'description': 'the identfier for this work',
                     'required': False,
                     'type': 'string'},
        'narrative': {
            'description': '',
            'required': False,
            'type': 'string'},
        'program': {'description': 'the program the work was funded under',
                    'required': True,
                    'type': 'string'},
        'team': {
            'description': 'information about the team members participating '
                           'in the grant.',
            'required': True,
            'type': 'list',
            'schema': {'type': 'dict',
                       'schema': {'cv': {'required': False, 'type': 'string'},
                                  'institution': {
                                      'required': True,
                                      'type': 'string'},
                                  'name': {'required': True, 'type': 'string'},
                                  'position': {
                                      'required': True,
                                      'type': 'string'},
                                  'subaward_amount': {
                                      'required': False,
                                      'type': ('integer', 'float')}}}},
        'title': {'description': 'actual title of proposal / grant',
                  'required': True,
                  'type': 'string'}},
    'abstracts': {
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
    'blog': {
        '_id': {'description': 'short represntation, such as this-is-my-title',
                'required': True,
                'type': 'string'},
        'author': {'description': 'name or AKA of author',
                   'required': True,
                   'type': 'string'},
        'day': {
            'description': 'Publication day',
            'required': True,
            'type': 'integer'},
        'month': {
            'description': 'Publication month',
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
        'year': {
            'description': 'Publication year',
            'required': True,
            'type': 'integer'}},
    'grades': {
        '_id': {
            'description': 'unique id, typically the '
                           'student-assignment-course',
            'required': True,
            'type': 'string'},
        'assignment': {
            'description': 'assignment id',
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
        'student': {
            'description': 'student id',
            'required': True,
            'type': 'string'}},
    'assignments': {
        '_id': {
            'description': 'A unique id for the assignment, such a '
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
    'projects': {'_id': {'description': 'Unique project identifier.',
                         'required': True,
                         'type': 'string'},
                 'description': {'description': 'brief project description.',
                                 'required': True,
                                 'type': 'string'},
                 'logo': {'description': 'URL to the project logo',
                          'required': False,
                          'type': 'string'},
                 'name': {'description': 'name of the project.',
                          'required': True,
                          'type': 'string'},
                 'other': {
                     'description': 'other information about the project',
                     'required': False,
                     'type': ['list','string']},
                 'repo': {
                     'description': 'URL of the source code repo, if available',
                     'required': False,
                     'type': 'string'},
                 'team': {
                     'description': 'People who are/have been woking on this '
                                    'project.',
                     'required': True,
                     'type': 'list',
                     'schema': {
                         'begin_month': {'required': False, 'type': 'string'},
                         'begin_year': {'required': True, 'type': 'integer'},
                         'end_month': {'required': False, 'type': 'string'},
                         'end_year': {'required': False, 'type': 'integer'},
                         'name': {'required': True, 'type': 'string'},
                         'position': {'required': True, 'type': 'string'}}
                 },
                 'website': {'description': 'URL of the website.',
                             'required': True,
                             'type': 'string'}},
    'proposals': {
        '_id': {'description': 'short represntation, such as this-is-my-name',
                'required': True,
                'type': ('string', 'integer', 'float')},
        'ammount': {'description': 'value of award',
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
        'durration': {'description': 'number of years',
                      'required': True,
                      'type': ('integer', 'float')},
        'month': {'description': 'month that the proposal is due',
                  'required': True,
                  'type': 'string'},
        'pi': {'description': 'principal investigator name',
               'required': True,
               'type': 'string'},
        # XXX: FIXME
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
        '_id': {'description': 'short represntation, such as this-is-my-name',
                'required': True,
                'type': 'string'},
        'aka': {'description': 'list of aliases',
                'required': False,
                'type': ('list', 'string'),
                'schema': {'type': 'string'}},
        'email': {
            'description': 'email address',
            'required': False,
            'type': 'string'},
        'university_id': {
            'description': 'The university identifier for the student',
            'required': False,
            'type': 'string'}},
    'people': {'_id': {'description': 'unique identifier for the group member',
                       'required': True,
                       'type': 'string'},
               'active': {
                   'description': 'If the person is an active member, '
                                  'default True.',
                   'required': False,
                   'type': 'boolean'},
               'aka': {
                   'description': 'list of aliases (also-known-as), useful '
                                  'for identifying the group member in '
                                  'citations or elsewhere.',
                   'required': True,
                   'type': ['string', 'list']},
               'avatar': {
                   'description': 'URL to avatar',
                   'required': True,
                   'type': 'string'},
               'bio': {'description': 'short biographical text',
                       'required': True,
                       'type': 'string'},
               'collab': {
                   'description': 'If the person is a collaborator, default '
                                  'False.',
                   'required': False,
                   'type': 'boolean'},
               'education': {
                   'description': 'This contains the educational information '
                                  'for the group member.',
                   'required': True,
                   'type': 'list',
                   'schema': {
                       'begin_month': {'required': False, 'type': 'string'},
                       'begin_year': {'required': True, 'type': 'integer'},
                       'degree': {'required': True, 'type': 'string'},
                       'end_month': {'required': False, 'type': 'string'},
                       'end_year': {'required': True, 'type': 'integer'},
                       'gpa': {'required': False, 'type': ('float', 'string')},
                       'institution': {'required': True, 'type': 'string'},
                       'location': {'required': True, 'type': 'string'},
                       'other': {'required': False, 'type': 'string'}}
               },
               'email': {'description': 'email address of the group member',
                         'required': False,
                         'type': 'string'},
               'employment': {
                   'description': 'Employment information, similar to '
                                  'educational information.',
                   'required': True,
                   'type': 'list',
                   'schema': {
                       'begin_month': {'required': False, 'type': 'string'},
                       'begin_year': {'required': True, 'type': 'integer'},
                       'end_month': {'required': False, 'type': 'string'},
                       'end_year': {'required': False, 'type': 'integer'},
                       'location': {'required': True, 'type': 'string'},
                       'organization': {'required': True, 'type': 'string'},
                       'other': {'required': False, 'type': 'string'},
                       'position': {'required': True, 'type': 'string'}}},
               'funding': {
                   'description': 'Funding and scholarship that the group '
                                  'member has individually obtained in the '
                                  'past. **WARNING:** this is not to be '
                                  'confused with the **grants** collection',
                   'required': False,
                   'type': 'list',
                   'schema': {
                       'currency': {'required': False, 'type': 'string'},
                       'duration': {'required': False, 'type': 'string'},
                       'month': {'required': False, 'type': 'string'},
                       'name': {'required': True, 'type': 'string'},
                       'value': {
                           'required': True,
                           'type': ('float', 'integer')},
                       'year': {'required': True, 'type': 'integer'}}
               },
               'honors': {
                   'description': 'Honors that have been awarded to this '
                                  'group member',
                   'required': False,
                   'type': 'list',
                   'schema': {
                       'description': {'required': False, 'type': 'string'},
                       'month': {'required': False, 'type': 'string'},
                       'name': {'required': True, 'type': 'string'},
                       'year': {'required': True, 'type': 'integer'}}
               },
               'membership': {
                   'description': 'Profesional organizations this member is '
                                  'a part of',
                   'required': False,
                   'type': 'list',
                   'schema': {
                       'begin_month': {'required': False, 'type': 'string'},
                       'begin_year': {'required': True, 'type': 'integer'},
                       'description': {'required': False, 'type': 'string'},
                       'end_month': {'required': False, 'type': 'string'},
                       'end_year': {'required': False, 'type': 'integer'},
                       'organization': {'required': True, 'type': 'string'},
                       'position': {'required': True, 'type': 'string'},
                       'website': {'required': False, 'type': 'string'}}},
               'name': {'description': 'Full, canonical name for the person',
                        'required': True,
                        'type': 'string'},
               'position': {
                   'description': 'such as professor, graduate student, '
                                  'or scientist',
                   'required': True,
                   'type': 'string'},
               'service': {
                   'description': 'Service that this group member has provided',
                   'required': False,
                   'type': 'list',
                   'schema': {
                       'description': {'required': False, 'type': 'string'},
                       'duration': {'required': False, 'type': 'string'},
                       'month': {'required': False, 'type': 'string'},
                       'name': {'required': True, 'type': 'string'},
                       'year': {'required': True, 'type': 'integer'}}
               },
               'skills': {'description': 'Skill the group member has',
                          'required': False,
                          'type': 'list',
                          'schema': {
                              'category': {'required': True, 'type': 'string'},
                              'level': {'required': True, 'type': 'string'},
                              'name': {'required': True, 'type': 'string'}}
                          },
               'teaching': {
                   'description': 'Courses that this group member has '
                                  'taught, if any',
                   'required': False,
                   'type': 'list',
                   'schema': {'course': {'required': True, 'type': 'string'},
                              'description': {
                                  'required': False,
                                  'type': 'string'},
                              'end_month': {
                                  'required': False,
                                  'type': 'string'},
                              'end_year': {
                                  'required': False,
                                  'type': 'integer'},
                              'materials': {
                                  'required': False,
                                  'type': 'string'},
                              'month': {'required': False, 'type': 'string'},
                              'organization': {
                                  'required': True,
                                  'type': 'string'},
                              'position': {'required': True, 'type': 'string'},
                              'syllabus': {
                                  'required': False,
                                  'type': 'string'},
                              'video': {'required': False, 'type': 'string'},
                              'website': {'required': False, 'type': 'string'},
                              'year': {'required': True, 'type': 'integer'}}
               },
               'title': {'description': 'for example, Dr., etc.',
                         'required': False,
                         'type': 'string'}
               }
}
