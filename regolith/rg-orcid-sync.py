
def get_orcid_key_secret(person_id):
    """checks if a person's ORCID client key and secret are defined and valid in rc

    Parameters:
        person_id - string
            the person's id in regolith

    Returns:
        The client key and secret, or False/setup message if they are not present or properly formulated in rc
    """


def get_orcid_search_token(person_id):
    """checks if a person's ORCID search token is defined and valid in rc,
    or generates a search token if it isn't present or properly formulated in rc

    Parameters:
        person_id - string
            the person's id in regolith

    Returns:
        If found, returns search token
        If not found, attempts to generate search token, and returns the search token on success
        If an error occurs when generating search token, returns False/error message
    """


def search_orcid(person_id, target_section):
    """searches the ORCID public database in a defined section e.g. Activities, Funding, etc.
    given that the client key, secret, and search token are defined and valid in rc

    Parameters:
        person_id - string
            the person's id in regolith
        target_section - string
            the desired section to be searched

    Returns:
        The ORCID database in raw json format
    """


def orcid_json_to_regolith(raw_response):
    """converts json ORCID data to regolith compatible format (?and stores in rg-db-orcid database?)

    Parameters:
        raw_response - json
            raw JSON data from ORCID search

    Returns:
        The properly formatted (i.e. regolith compatible) search data
    """


def get_people_orcid_search_token(rc):
    """gets a list of people with ORCID client key, secret, and search tokens in rc

    Parameters:
        rc -
            Run Control instance to search from

    Returns:
        a list of people with valid ORCID search tokens
    """


def search_orcid_all(people_orcid_search_token_present):
    """runs a search on ORCID public db for people with a valid and defined ORCID client key, secret, and search token

    Parameters:
        people_orcid_search_token_present
            a list of people with valid ORCID search tokens

    Returns:
        The properly formatted search data for everyone with a valid ORCID search token
    """