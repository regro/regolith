"""The main CLI for regolith"""
from __future__ import print_function
import os
import json
from argparse import ArgumentParser, RawTextHelpFormatter

from regolith.commands import INGEST_COLL_LU
from regolith.runcontrol import RunControl, NotSpecified
from regolith.validators import DEFAULT_VALIDATORS
from regolith.database import connect
from regolith import commands
from regolith import storage
from regolith.builder import BUILDERS

DEFAULT_RC = RunControl(
    _validators=DEFAULT_VALIDATORS,
    backend='filesystem',
    builddir='_build',
    mongodbpath=property(lambda self: os.path.join(self.builddir, '_dbpath')),
    )

DISCONNECTED_COMMANDS = {
    'rc': lambda rc: print(rc._pformat()),
    'deploy': commands.deploy,
    'store': storage.main,
    'json-to-yaml': commands.json_to_yaml,
    'yaml-to-json': commands.yaml_to_json,
    }

CONNECTED_COMMANDS = {
    'add': commands.add_cmd,
    'ingest': commands.ingest,
    'app': commands.app,
    'grade': commands.grade,
    'build': commands.build,
    'email': commands.email,
    'classlist': commands.classlist,
    }

NEED_RC = set(CONNECTED_COMMANDS.keys())
NEED_RC |= {'rc', 'deploy', 'store'}


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
    addp = subp.add_parser('add',
                           help='adds a record to a database and collection')
    addp.add_argument('db', help='database name')
    addp.add_argument('coll', help='collection name')
    addp.add_argument('documents', nargs='+', help='documents, in JSON / mongodb format')

    # ingest subparser
    ingp = subp.add_parser('ingest', help='ingest many records from a foreign '
                                          'resource into a database')
    ingp.add_argument('db', help='database name')
    ingp.add_argument('filename',
                      help='file to ingest. Currently valid formats are: \n{}'
                           ''.format([k for k in INGEST_COLL_LU]))
    ingp.add_argument('--coll', dest='coll',  default=None,
                      help='collection name, if this is not given it is infered from the '
                           'file type or file name.')

    # store subparser
    strp = subp.add_parser('store', help='stores a file into the appropriate '
                                         'storage location.')
    strp.add_argument('storename', help='storage name')
    strp.add_argument('documents', nargs='+', help='paths to documents, i.e. '
                                                   'PDFs, images, etc.')
    strp.add_argument('-f', '--force', dest='force', default=False,
                      action='store_true',
                      help='forces copy of file if one of the same name '
                           'already exists')

    # app subparser
    appp = subp.add_parser('app', help='starts up a flask app for inspecting and '
                                       'modifying regolith data.')
    appp.add_argument('--debug', dest='debug', action='store_true', default=False,
                      help='starts server in debug mode')

    # grade subparser
    grdp = subp.add_parser('grade', help='starts up a flask app for adding '
                                         'grades to the database.')
    grdp.add_argument('--debug', dest='debug', action='store_true',
                      default=False, help='starts server in debug mode')

    # builder subparser
    bldp = subp.add_parser('build', help='builds various available targets',
                           formatter_class=RawTextHelpFormatter)
    bldp.add_argument('build_targets', nargs='+',
                      help='targets to build. Currently valid targets are: \n{}'.
                      format([k for k in BUILDERS]))

    # deploy subparser
    depp = subp.add_parser('deploy', help='deploys what was built by regolith')

    # email subparser
    emlp = subp.add_parser('email', help='automates emailing')
    emlp.add_argument('email_target', help='targets to email, eg "test" or '
                                           '"grades".')
    emlp.add_argument('--to', default=None, dest='to',
                      help='receiver of email')
    emlp.add_argument('--subject', dest='subject', help='email subject line',
                      default='')
    emlp.add_argument('--body', dest='body', help='email body, as restructured text',
                      default='')
    emlp.add_argument('--attach', nargs='+', dest='attachments', default=(),
                      help='attachments to send along as well.')
    emlp.add_argument('-c', '--course-id', dest='course_id', default=None,
                      help='course identifier that should be emailed.')
    emlp.add_argument('--db', help='database name', dest='db', default=None)

    # classlist subparser
    clp = subp.add_parser('classlist', help='updates classlist information from file')
    clp.add_argument('op', help='operatation to perform, such as "add" or "replace".')
    clp.add_argument('filename', help='file to read class information from.')
    clp.add_argument('course_id', help='course identifier whose registry should be updated')
    clp.add_argument('-f', '--format', dest='format', default=None,
                     help='file / school format to read information from. Current values are '
                          '"json" and "usc". Determined from extension if not available.')
    clp.add_argument('-d', '--dry-run', dest='dry_run', action='store_true',
                     default=False, help='only does a dry run and reports results')
    clp.add_argument('--db', help='database name', dest='db', default=None)

    # JSON-to-YAML subparser
    jty = subp.add_parser('json-to-yaml', help='Converts files from JSON to YAML')
    jty.add_argument('files', nargs='+', help='file names to convert')

    # YAML-to-JSON subparser
    ytj = subp.add_parser('yaml-to-json', help='Converts files from YAML to JSON')
    ytj.add_argument('files', nargs='+', help='file names to convert')
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
    elif len(dbs) == 1:
        rc.db = dbs[0]['name']
    rc.databases = dbs


def main(args=None):
    rc = DEFAULT_RC
    parser = create_parser()
    ns = parser.parse_args(args)
    if ns.cmd in NEED_RC:
        rc._update(load_rcfile('regolithrc.json'))
    rc._update(ns.__dict__)
    if ns.cmd in NEED_RC:
        filter_databases(rc)
    if rc.cmd in DISCONNECTED_COMMANDS:
        DISCONNECTED_COMMANDS[rc.cmd](rc)
    else:
        with connect(rc) as rc.client:
            CONNECTED_COMMANDS[rc.cmd](rc)


if __name__ == '__main__':
    main()
