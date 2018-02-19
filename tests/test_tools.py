from regolith.tools import filter_publications


def test_author_publications():
    citations = [{'author': ['CJ', 'SJLB']}, {'editor': 'SJLB'}]
    filter_publications(citations, {'SJLB'})
