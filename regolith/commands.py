"""Implementation of commands for command line."""
import os
import re
import json

from regolith.tools import string_types
from regolith.builder import builder
from regolith.emailer import emailer as email
from regolith.deploy import deploy as dploy

RE_AND = re.compile('\s+and\s+')
RE_SPACE = re.compile('\s+')

INGEST_COLL_LU = {'.bib': 'citations'}


def add_cmd(rc):
    """Adds documents to a collection in a database."""
    db = rc.client[rc.db]
    coll = db[rc.coll]
    docs = [json.loads(doc) if isinstance(doc, string_types) else doc
            for doc in rc.documents]
    rc.client.insert_many(rc.db, rc.coll, docs)


def _ingest_citations(rc):
    import bibtexparser
    from bibtexparser.bparser import BibTexParser
    from bibtexparser.customization import getnames

    parser = BibTexParser()
    parser.ignore_nonstandard_types = False

    def customizations(record):
        for n in ['author', 'editor']:
            if n in record:
                a = [i for i in record[n].replace('\n', ' ').split(', ')]
                b = [i.split(" and ") for i in a]
                c = [item for sublist in b for item in sublist]
                d = [i.strip() for i in c]
                record[n] = getnames(d)

        return record

    parser.customization = customizations
    with open(rc.filename, 'r') as f:
        bibs = bibtexparser.load(f, parser=parser)
    coll = rc.client[rc.db][rc.coll]
    for bib in bibs.entries:
        bibid = bib.pop('ID')
        bib['entrytype'] = bib.pop('ENTRYTYPE')
        if 'author' in bib:
            bib['author'] = [a.strip() for b in bib['author'] for a in
                             RE_AND.split(b)]
        if 'title' in bib:
            bib['title'] = RE_SPACE.sub(' ', bib['title'])
        rc.client.update_one(rc.db, rc.coll, {'_id': bibid},
                             bib, upsert=True)


def _determine_ingest_coll(rc):
    f = rc.filename
    base, ext = os.path.splitext(f)
    return INGEST_COLL_LU.get(ext, base)


def ingest(rc):
    """Ingests a foreign resource into a database."""
    if rc.coll is None:
        rc.coll = _determine_ingest_coll(rc)
    if rc.coll == 'citations':
        _ingest_citations(rc)
    else:
        raise ValueError(
            "don't know how to ingest collection {0!r}".format(rc.coll))


def _run_app(app, rc):
    if hasattr(app, 'rc'):
        raise RuntimeError('cannot assign rc to app')
    app.rc = rc
    app.debug = rc.debug
    print('\nDO NOT type Ctrl-C to close the server!!!')
    print('Instead, run the following:')
    print("\n$ curl -d '' http://localhost:5000/shutdown\n")
    app.run(host='localhost')
    del app.rc


def app(rc):
    """Runs flask app"""
    from regolith.app import app
    _run_app(app, rc)


def grade(rc):
    """Runs flask grading app"""
    from regolith.grader import app
    _run_app(app, rc)


def build(rc):
    """Builds all of the build targets"""
    for t in rc.build_targets:
        bldr = builder(t, rc)
        bldr.build()


def deploy(rc):
    """Deploys all of the deployment targets."""
    if not hasattr(rc, 'deploy') or len(rc.deploy) == 0:
        raise RuntimeError('run control has no deployment targets!')
    for target in rc.deploy:
        dploy(rc, **target)


def classlist(rc):
    """Sets values for the class list."""
    from regolith.classlist import register
    register(rc)


def json_to_yaml(rc):
    """Converts JSON to YAML"""
    from regolith import fsclient
    for inp in rc.files:
        base, ext = os.path.splitext(inp)
        out = base + '.yaml'
        fsclient.json_to_yaml(inp, out)


def yaml_to_json(rc):
    """Converts YAML to JSON"""
    from regolith import fsclient
    for inp in rc.files:
        base, ext = os.path.splitext(inp)
        out = base + '.json'
        fsclient.yaml_to_json(inp, out)


def validate(rc):
    """Validate the combined database against the schemas"""
    from regolith.schemas import validate
    print('\nVALIDATING\n')
    for coll in rc.client.chained_db:
        validate(coll, rc.client.chained_db[coll])
    print('\nNO ERORS IN DBS\n')
