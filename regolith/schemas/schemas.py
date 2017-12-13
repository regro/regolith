schemas = {}
schemas['grants'] = {
    '_id': {'description': 'short represntation, such as this-is-my-name',
            'type': (str, int, float)},
    'amount': {'description': 'value of award', 'type': (int, float)},
    'begin_day': {
        'description': 'start day of the grant, optional',
        'type': int},
    'begin_month': {'description': 'start month of the grant', 'type': str},
    'begin_year': {'description': 'start year of the grant', 'type': int},
    'benefit_of_collaboration': {'description': 'optional, URL of document',
                                 'type': str},
    'call_for_proposals': {
        'description': 'optional, URL to the call for proposals',
        'type': str},
    'currency': {'description': "typically '$' or 'USD'", 'type': str},
    'end_day': {'description': 'end day of teh grant, optional',
                'type': (str, int)},
    'end_month"': {'description': 'end month of the grant', 'type': str},
    'end_year': {'description': 'end year of the grant', 'type': int},
    'funder': {'description': 'the agency funding the work', 'type': str},
    'grant_id': {
        'description': 'optional, the identfier for this work, eg #42024',
        'type': str},
    'narrative': {'description': 'optional, URL of document', 'type': str},
    'program': {'description': 'the program the work was funded under',
                'type': str},
    'team': {
        'description': 'information about the team members participating in '
                       'the grant.',
        'type': [{"name": {
            'type': str,
            'description': "should match a person's name  or AKA"},
          "position": {
              'type': str,
              'description': "PI, Co-PI, Co-I, Researcher, etc."},
          "institution": {
              "type": str,
              'description': "The institution of this investigator"},
          "subaward_amount": {"type": (int, float)},
          "cv": {'type': str, 'description': "URL of document"}}]},
    'title': {'description': 'actual title of proposal / grant', 'type': str}}
