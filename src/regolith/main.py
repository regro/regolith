"""The main CLI for regolith."""

from __future__ import print_function

import copy
import os
from argparse import ArgumentParser, Namespace, RawTextHelpFormatter

from regolith import __version__, commands
from regolith.builder import BUILDERS
from regolith.commands import CONNECTED_COMMANDS, DISCONNECTED_COMMANDS, INGEST_COLL_LU
from regolith.database import connect
from regolith.helper import HELPERS
from regolith.runcontrol import DEFAULT_RC, filter_databases, load_rcfile
from regolith.schemas import SCHEMAS
from regolith.tools import update_schemas

NEED_RC = set(CONNECTED_COMMANDS.keys())
NEED_RC |= {"rc", "deploy", "store"}


def create_parser():
    p = ArgumentParser()
    subp = p.add_subparsers(title="cmd", dest="cmd")

    p.add_argument("--version", action="store_true")

    # helper subparser
    subp.add_parser(
        "helper",
        help="runs an available helper target",
        formatter_class=RawTextHelpFormatter,
    )

    # rc subparser
    subp.add_parser("rc", help="prints run control")

    # add subparser
    addp = subp.add_parser("add", help="adds a record to a database and collection")
    addp.add_argument("db", help="database name")
    addp.add_argument("coll", help="collection name")
    addp.add_argument("documents", nargs="+", help="documents, in JSON / mongodb format")

    # ingest subparser
    ingp = subp.add_parser(
        "ingest",
        help="ingest many records from a foreign " "resource into a database",
    )
    ingp.add_argument("db", help="database name")
    ingp.add_argument(
        "filename",
        help="file to ingest. Currently valid formats are: \n{}" "".format([k for k in INGEST_COLL_LU]),
    )
    ingp.add_argument(
        "--coll",
        dest="coll",
        default=None,
        help="collection name, if this is not given it is inferred from the " "file type or file name.",
    )

    # store subparser
    strp = subp.add_parser("store", help="stores a file into the appropriate " "storage location.")
    strp.add_argument("storename", help="storage name")
    strp.add_argument(
        "documents",
        nargs="+",
        help="paths to documents, i.e. " "PDFs, images, etc.",
    )
    strp.add_argument(
        "-f",
        "--force",
        dest="force",
        default=False,
        action="store_true",
        help="forces copy of file if one of the same name " "already exists",
    )

    # app subparser
    appp = subp.add_parser(
        "app",
        help="starts up a flask app for inspecting and " "modifying regolith data.",
    )
    appp.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        default=False,
        help="starts server in debug mode",
    )

    # grade subparser
    grdp = subp.add_parser(
        "grade",
        help="starts up a flask app for adding " "grades to the database.",
    )
    grdp.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        default=False,
        help="starts server in debug mode",
    )

    # builder subparser
    bldp = subp.add_parser(
        "build",
        help="builds various available targets",
        formatter_class=RawTextHelpFormatter,
    )
    bldp.add_argument(
        "build_targets",
        nargs="+",
        help="targets to build. Currently valid targets are: \n{}".format([k for k in BUILDERS]),
    )
    bldp.add_argument(
        "--no-pdf",
        dest="pdf",
        help="don't produce PDFs during the build " "(for builds which produce PDFs)",
        action="store_false",
        default=True,
    )
    bldp.add_argument(
        "--from",
        dest="from_date",
        help="date in form YYYY-MM-DD.  Items will only be built"
        " if their date or end_date is equal or after this date",
        default=None,
    )
    bldp.add_argument(
        "--to",
        dest="to_date",
        help="date in form YYYY-MM-DD.  Items will only be built"
        " if their date or begin_date is equal or before this date",
        default=None,
    )
    bldp.add_argument(
        "--grants",
        nargs="+",
        dest="grants",
        help="specify a grant or a space-separated list of grants so items are "
        "built only if associated with this(these) grant(s)",
        default=None,
    )
    bldp.add_argument(
        "--people",
        nargs="+",
        dest="people",
        help="specify a person or a space-separated list of people such that "
        "the build will be for only those people",
        default=None,
    )
    bldp.add_argument(
        "--kwargs",
        nargs="+",
        dest="kwargs",
        help="pass a specific command to build a specific task " "if it exists",
        default=None,
    )

    # deploy subparser
    subp.add_parser("deploy", help="deploys what was built by regolith")

    # email subparser
    emlp = subp.add_parser("email", help="automates emailing")
    emlp.add_argument("email_target", help='targets to email, eg "test" or ' '"grades".')
    emlp.add_argument("--to", default=None, dest="to", help="receiver of email")
    emlp.add_argument("--subject", dest="subject", help="email subject line", default="")
    emlp.add_argument(
        "--body",
        dest="body",
        help="email body, as restructured text",
        default="",
    )
    emlp.add_argument(
        "--attach",
        nargs="+",
        dest="attachments",
        default=(),
        help="attachments to send along as well.",
    )
    emlp.add_argument(
        "-c",
        "--course-id",
        dest="course_ids",
        default=(),
        nargs="+",
        help="course identifier that should be emailed.",
    )
    emlp.add_argument("--db", help="database name", dest="db", default=None)

    # classlist subparser
    clp = subp.add_parser("classlist", help="updates classlist information from file")
    clp.add_argument("op", help='operatation to perform, such as "add" or "replace".')
    clp.add_argument("filename", help="file to read class information from.")
    clp.add_argument("course_id", help="course identifier whose registry should be updated")
    clp.add_argument(
        "-f",
        "--format",
        dest="format",
        default=None,
        help="file / school format to read information from. Current values are "
        '"json" and "usc". Determined from extension if not available.',
    )
    clp.add_argument(
        "-d",
        "--dry-run",
        dest="dry_run",
        action="store_true",
        default=False,
        help="only does a dry run and reports results",
    )
    clp.add_argument("--db", help="database name", dest="db", default=None)

    # JSON-to-YAML subparser
    jty = subp.add_parser("json-to-yaml", help="Converts files from JSON to YAML")
    jty.add_argument("files", nargs="+", help="file names to convert")

    # YAML-to-JSON subparser
    ytj = subp.add_parser("yaml-to-json", help="Converts files from YAML to JSON")
    ytj.add_argument("files", nargs="+", help="file names to convert")

    # mongo-to-fs subparser
    mtf = subp.add_parser(
        "mongo-to-fs",
        help="Backup database from mongodb to filesystem as json. "
        "The database will be imported to the destination specified by the 'database':'dst_url' key. "
        "For this to work, ensure that the database is included in the "
        "dst_url, and that local is set to true.",
    )

    mtf.add_argument(
        "--host",
        help="Specifies a resolvable hostname for the mongod to which to connect. By "
        "default, the mongoexport attempts to connect to a MongoDB instance running "
        "on the localhost on port number 27017.",
        dest="host",
        default=None,
    )

    # fs-to-mongo subparser
    ftm = subp.add_parser(
        "fs-to-mongo",
        help="Import database from filesystem to mongodb. By default, the database will be import to the local "
        "mongodb. The database can also be imported to the destination specified by the 'database':'dst_url' key."
        " For this to work, ensure that the database is included in the dst_url, and that local is set to true.",
    )

    ftm.add_argument(
        "--host",
        help="Specifies a resolvable hostname for the mongod to which to connect. By "
        "default, the mongoimport attempts to connect to a MongoDB instance running "
        "on the localhost on port number 27017.",
        dest="host",
        default=None,
    )

    # GitHub extractor subparser
    ghe = subp.add_parser(
        "gh-extractor",
        help="Extract GitHub repository metadata and write software YAML",
    )
    ghe.add_argument("owner", help="GitHub owner or organization")
    ghe.add_argument("--repo", help="Single repository name")
    ghe.add_argument("--all", action="store_true", help="Extract all active repositories")
    ghe.add_argument("--token", help="GitHub token (or set GITHUB_TOKEN)")

    # Validator
    val = subp.add_parser("validate", help="Validates db")
    val.add_argument(
        "--collection",
        dest="collection",
        default=None,
        help="If provided only validate that collection",
    )
    return p


def main(args=None):
    rc = copy.copy(DEFAULT_RC)
    parser = create_parser()
    args0 = Namespace()
    args1, rest = parser.parse_known_args(args, namespace=args0)
    if args1.version:
        print(__version__)
        return rc
    if args1.cmd == "helper":
        p = ArgumentParser(prog="regolith helper")
        p.add_argument(
            "helper_target",
            help="helper target to run. Currently valid targets are: \n{}".format([k for k in HELPERS]),
        )
        if len(rest) == 0:
            p.print_help()
        args2, rest2 = p.parse_known_args(rest, namespace=args0)
        # it is not apparent from this but the following line calls the subparser in
        #   in the helper module to get the rest of the args.
        HELPERS[args2.helper_target][1](p)
        if len(rest2) == 0:
            p.print_help()
        args3, rest3 = p.parse_known_args(rest, namespace=args0)
        ns = args3
    else:
        ns = args1
    if ns.cmd in NEED_RC:
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
    if ns.cmd in NEED_RC:
        filter_databases(rc)
    if rc.cmd in DISCONNECTED_COMMANDS:
        DISCONNECTED_COMMANDS[rc.cmd](rc)
    else:
        dbs = None
        if rc.cmd == "build":
            dbs = commands.build_db_check(rc)
        elif rc.cmd == "helper":
            dbs = commands.helper_db_check(rc)
        with connect(rc, dbs=dbs) as rc.client:
            CONNECTED_COMMANDS[rc.cmd](rc)
    return rc


if __name__ == "__main__":
    main()
