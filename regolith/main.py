"""The main CLI for regolith"""
import os
import json
from argparse import ArgumentParser

from regolith.runcontrol import RunControl, NotSpecified
from regolith.validators import DEFAULT_VALIDATORS

DEFAULT_RC = RunControl(
    _validators=DEFAULT_VALIDATORS,
    builddir='_build',
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
    return p


def main(args=None):
    rc = DEFAULT_RC
    rc._update(load_rcfile('regolithrc.json'))
    parser = create_parser()
    ns = parser.parse_args(args)
    rc._update(ns.__dict__)
    if rc.cmd == 'rc':
        print(rc._pformat())

if __name__ == '__main__':
    main()