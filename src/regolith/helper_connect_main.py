"""The main CLI for regolith."""

from __future__ import print_function

import copy
import os
import shlex
from argparse import ArgumentParser

from regolith import __version__
from regolith.commands import CONNECTED_COMMANDS
from regolith.database import connect
from regolith.helper import HELPERS
from regolith.runcontrol import DEFAULT_RC, filter_databases, load_rcfile
from regolith.schemas import SCHEMAS
from regolith.tools import update_schemas

NEED_RC = set(CONNECTED_COMMANDS.keys())
NEED_RC |= {"rc", "deploy", "store"}


def create_top_level_parser():
    p = ArgumentParser()
    p.add_argument("--version", action="store_true")
    p.add_argument(
        "-n",
        "--needed_colls",
        help="limit connecting collections to only those that will be used in this session",
        nargs="+",
        default=(),
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
    leave = False
    with connect(rc, dbs=ns.needed_colls) as rc.client:
        while leave is False:
            print("\ninput helper target and all target inputs:")
            get_cmds = input()
            cmds = get_cmds.split(" ", 1)
            if cmds[0] == "exit" or cmds[0] == "e":
                break
            if cmds[0] not in HELPERS:
                rc.print_help()
            rc.helper_target = cmds[0]
            p2 = ArgumentParser(prog="regolith helper")
            # it is not apparent from this but the following line calls the subparser in
            #   in the helper module to get the rest of the args.
            HELPERS[rc.helper_target][1](p2)
            if len(cmds) > 1:
                args3 = p2.parse_args(shlex.split(cmds[1]))
            else:
                args3 = p2.parse_args([])
            ns = args3
            rc._update(ns.__dict__)
            CONNECTED_COMMANDS[rc.cmd](rc)


if __name__ == "__main__":
    main()
