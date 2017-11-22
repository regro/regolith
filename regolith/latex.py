import os

try:
    from bibtexparser.bwriter import BibTexWriter
    from bibtexparser.bibdatabase import BibDatabase
    HAVE_BIBTEX_PARSER = True
except ImportError:
    HAVE_BIBTEX_PARSER = False

LATEX_OPTS = ['-halt-on-error', '-file-line-error']


def latex_safe(s):
    return s.replace('&', '\&').replace('$', '\$').replace('#', '\#')


def make_bibtex_file(pubs, pid, person_dir='.'):
    if not HAVE_BIBTEX_PARSER:
        return None
    skip_keys = set(['ID', 'ENTRYTYPE', 'author'])
    bibdb = BibDatabase()
    bibwriter = BibTexWriter()
    bibdb.entries = ents = []
    for pub in pubs:
        ent = dict(pub)
        ent['ID'] = ent.pop('_id')
        ent['ENTRYTYPE'] = ent.pop('entrytype')
        for n in ['author', 'editor']:
            if n in ent:
                ent[n] = ' and '.join(ent[n])
        for key in ent.keys():
            if key in skip_keys:
                continue
            ent[key] = latex_safe(ent[key])
        ents.append(ent)
    fname = os.path.join(person_dir, pid) + '.bib'
    with open(fname, 'w') as f:
        f.write(bibwriter.write(bibdb))
    return fname
