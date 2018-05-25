from regolith.tools import filter_publications
from regolith.tools import fuzzy_retrieval


def test_author_publications():
    citations = [{'author': ['CJ', 'SJLB']}, {'editor': 'SJLB'}]
    filter_publications(citations, {'SJLB'})


def test_fuzzy_retrieval():
    person = {'_id': 'scopatz',
              'aka': ['Scopatz',
                      'Scopatz, A',
                      'Scopatz, A.',
                      'Scopatz, A M',
                      'Anthony Michael Scopatz'],
              'name': 'Anthony Scopatz'}
    assert fuzzy_retrieval([person], ['aka', 'name', '_id'],
                           'scopatz') == person
