"""The main CLI for regolith"""
from __future__ import print_function

import copy
import os
from argparse import ArgumentParser

from regolith.database import connect

from regolith import commands, __version__
from regolith import storage
from regolith.helper import HELPERS
from regolith.runcontrol import DEFAULT_RC, load_rcfile, filter_databases
from regolith.schemas import SCHEMAS
from regolith.tools import update_schemas
from regolith.commands import CONNECTED_COMMANDS

from gooey import Gooey, GooeyParser


NEED_RC = set(CONNECTED_COMMANDS.keys())
NEED_RC |= {"rc", "deploy", "store"}

def create_top_level_parser():
    p = ArgumentParser()
    p.add_argument(
        "--version",
        action="store_true"
    )
    return p

def create_parser(inputs):
    p = ArgumentParser()
    subp = p.add_subparsers(title="helper_target", dest="helper_target")
    for k, v in HELPERS.items():
        subpi = subp.add_parser(k)
        v[1](subpi)

    return p


def main(args=None):
    rc = copy.copy(DEFAULT_RC)
    parser = create_top_level_parser()
    ns = parser.parse_args()
    if ns.version:
        print(__version__)
        return rc
    rc.cmd = "helper"
    if os.path.exists(rc.user_config):
        rc._update(load_rcfile(rc.user_config))
    rc._update(load_rcfile("regolithrc.json"))
    if "schemas" in rc._dict:
        user_schema = copy.deepcopy(rc.schemas)
        default_schema = copy.deepcopy(SCHEMAS)
        rc.schemas = update_schemas(default_schema, user_schema)
    else:
        rc.schemas = SCHEMAS
    filter_databases(rc)
    with connect(rc) as rc.client:
        CONNECTED_COMMANDS[rc.cmd](rc)


if __name__ == "__main__":
    main()
