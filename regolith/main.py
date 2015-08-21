"""The main CLI for regolith"""
import os
import json
from argparse import ArgumentParser

from regolith.runcontrol import RunControl, NotSpecified
from regolith.validators import DEFAULT_VALIDATORS
from regolith.database import connect

DEFAULT_RC = RunControl(
    _validators=DEFAULT_VALIDATORS,
    builddir='_build',
    mongodbpath=property(lambda self: os.path.join(self.builddir, '_dbpath'))
    )


def load_json_rcfile(fname):
    """Loads a JSON run control file."""
    with open(fname, 'r') as f:
        rc = json.load(f)
    return rc


def load_rcfile(fname):
    """Loads a run control file."""
    base, ext = os.path.splitext(fname)
    if ext == '.json':
        rc = load_json_rcfile(fname)
    else:
        raise RuntimeError('could not detemine run control file type from extension.')
    return rc


def create_parser():
    p = ArgumentParser()
    subp = p.add_subparsers(title='cmd', dest='cmd')
    # rc subparser
    rcp = subp.add_parser('rc', help='prints run control')
    # add subparser
    addp = subp.add_parser('add', help='adds a record to a database and collection')
    addp.add_argument('db', help='database name')
    addp.add_argument('coll', help='collection name')
    addp.add_argument('document', help='document, in JSON / mongodb format')
    return p


def filter_databases(rc):
    """Filters the databases list down to only the ones we need, in place."""
    dbs = rc.databases
    public_only = rc._get('public_only', False)
    if public_only:
        dbs = [db for db in dbs if db['public']]
    dbname = rc._get('db') 
    if dbname is not None:
        dbs = [db for db in dbs if db['name'] == dbname]
    rc.databases = dbs
    

def main(args=None):
    rc = DEFAULT_RC
    rc._update(load_rcfile('regolithrc.json'))
    parser = create_parser()
    ns = parser.parse_args(args)
    rc._update(ns.__dict__)
    filter_databases(rc)
    if rc.cmd == 'rc':
        print(rc._pformat())
    else:
        with connect(rc) as rc.client:
            pass

if __name__ == '__main__':
    main()
