"""The main CLI for regolith"""
from __future__ import print_function

import copy
import os
from argparse import ArgumentParser, RawTextHelpFormatter, Namespace

from regolith.database import connect

from regolith import commands
from regolith import storage
from regolith.builder import BUILDERS
from regolith.commands import INGEST_COLL_LU
from regolith.helper import HELPERS
from regolith.runcontrol import DEFAULT_RC, load_rcfile, filter_databases
from regolith.schemas import SCHEMAS
from regolith.tools import update_schemas
from regolith.helpers.a_expensehelper import subparser as exp_subparser
from regolith.helpers.l_todohelper import subparser as todo_subparser
from gooey import Gooey, GooeyParser

DISCONNECTED_COMMANDS = {
    "rc": lambda rc: print(rc._pformat()),
    "deploy": commands.deploy,
    "store": storage.main,
    "json-to-yaml": commands.json_to_yaml,
    "yaml-to-json": commands.yaml_to_json,
}

CONNECTED_COMMANDS = {
    "add": commands.add_cmd,
    "ingest": commands.ingest,
    "app": commands.app,
    "grade": commands.grade,
    "build": commands.build,
    "email": commands.email,
    "classlist": commands.classlist,
    "validate": commands.validate,
    "helper": commands.helper,
    "fs-to-mongo": commands.fs_to_mongo
}

NEED_RC = set(CONNECTED_COMMANDS.keys())
NEED_RC |= {"rc", "deploy", "store"}

# @Gooey(advanced=True)
@Gooey(body_bg_color='#000000',
       required_cols=1,
       optional_cols=1)
def create_parser():
    p = GooeyParser()
    #p = ArgumentParser()
    subp = p.add_subparsers(title="helper_target", dest="helper_target")
    for k, v in HELPERS.items():
        subpi = subp.add_parser(k)
        v[1](subpi)
    # subpi = subp.add_parser("a_expense")
    # subpl = subp.add_parser("l_todo")
    # exp_subparser(subpi)
    # todo_subparser(subpl)

    return p


def main(args=None):
    rc = DEFAULT_RC
    parser = create_parser()
    ns = parser.parse_args()
    ns.cmd = "helper"
    if os.path.exists(rc.user_config):
        rc._update(load_rcfile(rc.user_config))
    rc._update(load_rcfile("regolithrc.json"))
    rc._update(ns.__dict__)
    if "schemas" in rc._dict:
        user_schema = copy.deepcopy(rc.schemas)
        default_schema = copy.deepcopy(SCHEMAS)
        rc.schemas = update_schemas(default_schema, user_schema)
    else:
        rc.schemas = SCHEMAS
    filter_databases(rc)
    dbs = None
    if rc.cmd == 'build':
        dbs = commands.build_db_check(rc)
    elif rc.cmd == 'helper':
        dbs = commands.helper_db_check(rc)
    with connect(rc, dbs=dbs) as rc.client:
        CONNECTED_COMMANDS[rc.cmd](rc)


if __name__ == "__main__":
    main()
