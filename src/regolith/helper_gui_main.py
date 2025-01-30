"""The main CLI for regolith."""

from __future__ import print_function

import copy
import os

from gooey import Gooey, GooeyParser

from regolith import commands
from regolith.commands import CONNECTED_COMMANDS
from regolith.database import connect
from regolith.helper import HELPERS
from regolith.runcontrol import DEFAULT_RC, filter_databases, load_rcfile
from regolith.schemas import SCHEMAS
from regolith.tools import update_schemas

NEED_RC = set(CONNECTED_COMMANDS.keys())
NEED_RC |= {"rc", "deploy", "store"}


# @Gooey(advanced=True)
@Gooey(  # body_bg_color='#808080',
    # header_bg_color='#808080',
    required_cols=1,
    optional_cols=1,
    sidebar_title="Helpers",
    program_name="Regolith Helper GUI",
)
def create_parser():
    p = GooeyParser()
    subp = p.add_subparsers(title="helper_target", dest="helper_target")
    for k, v in HELPERS.items():
        subpi = subp.add_parser(k)
        v[1](subpi)

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
    dbs = commands.helper_db_check(rc)
    with connect(rc, dbs=dbs) as rc.client:
        CONNECTED_COMMANDS[rc.cmd](rc)


if __name__ == "__main__":
    main()
