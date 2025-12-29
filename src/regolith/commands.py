"""Implementation of commands for command line."""

import json
import os
import re
import sys
from copy import copy
from pprint import pprint

from ruamel.yaml import YAML

from regolith import storage
from regolith.builder import BUILDERS, builder
from regolith.deploy import deploy as dploy
from regolith.emailer import emailer
from regolith.GHextractor import extract_github, to_software_yaml
from regolith.helper import FAST_UPDATER_WHITELIST, HELPERS, UPDATER_HELPERS, helpr
from regolith.runcontrol import RunControl
from regolith.tools import string_types

email = emailer

RE_AND = re.compile(r"\s+and\s+")
RE_SPACE = re.compile(r"\s+")

INGEST_COLL_LU = {".bib": "citations"}


def add_cmd(rc):
    """Adds documents to a collection in a database."""
    docs = [json.loads(doc) if isinstance(doc, string_types) else doc for doc in rc.documents]
    rc.client.insert_many(rc.db, rc.coll, docs)


def _ingest_citations(rc):
    import bibtexparser
    from bibtexparser.bparser import BibTexParser
    from bibtexparser.customization import getnames

    parser = BibTexParser()
    parser.ignore_nonstandard_types = False

    def customizations(record):
        for n in ["author", "editor"]:
            if n in record:
                a = [i for i in record[n].replace("\n", " ").split(", ")]
                b = [i.split(" and ") for i in a]
                c = [item for sublist in b for item in sublist]
                d = [i.strip() for i in c]
                record[n] = getnames(d)

        return record

    parser.customization = customizations
    with open(rc.filename, "r", encoding="utf-8") as f:
        bibs = bibtexparser.load(f, parser=parser)
    for bib in bibs.entries:
        bibid = bib.pop("ID")
        bib["entrytype"] = bib.pop("ENTRYTYPE")
        if "author" in bib:
            bib["author"] = [a.strip() for b in bib["author"] for a in RE_AND.split(b)]
        if "title" in bib:
            bib["title"] = RE_SPACE.sub(" ", bib["title"])
        rc.client.update_one(rc.db, rc.coll, {"_id": bibid}, bib, upsert=True)


def _determine_ingest_coll(rc):
    f = rc.filename
    base, ext = os.path.splitext(f)
    return INGEST_COLL_LU.get(ext, base)


def ingest(rc):
    """Ingests a foreign resource into a database."""
    if rc.coll is None:
        rc.coll = _determine_ingest_coll(rc)
    if rc.coll == "citations":
        _ingest_citations(rc)
    else:
        raise ValueError("don't know how to ingest collection {0!r}".format(rc.coll))


def _run_app(app, rc):
    if hasattr(app, "rc"):
        raise RuntimeError("cannot assign rc to app")
    app.rc = rc
    app.debug = rc.debug
    print("\nDO NOT type Ctrl-C to close the server!!!")
    print("Instead, run the following:")
    print("\n$ curl -d '' http://localhost:5000/shutdown\n")
    app.run(host="localhost")
    del app.rc


def app(rc):
    """Runs flask app."""
    from regolith.app import app

    _run_app(app, rc)


def grade(rc):
    """Runs flask grading app."""
    from regolith.grader import app

    _run_app(app, rc)


def build_db_check(rc):
    """Checks which DBs a builder needs."""
    dbs = set()
    for t in rc.build_targets:
        bldr = BUILDERS[t]
        needed_colls = getattr(bldr, "needed_colls", None)
        # If the requested builder doesn't state DB deps then it requires
        # all dbs!
        if not needed_colls:
            return None
        dbs.update(needed_colls)
    return dbs


def helper_db_check(rc):
    """Checks which DBs a builder needs."""
    # if the helper is an fast_updater, only open the database from rc.database
    rc.fast_updater = False
    for helperkey in UPDATER_HELPERS.keys():
        if helperkey == rc.helper_target and rc.helper_target in FAST_UPDATER_WHITELIST:
            rc.fast_updater = True
    if rc.database is None:
        rc.database = rc.databases[0]["name"]
    if rc.fast_updater:
        rc.databases = [database for database in rc.databases if database.get("name") == rc.database]

    # only open the needed collections
    colls = set()
    bldr = HELPERS[rc.helper_target][0]
    needed_colls = getattr(bldr, "needed_colls", None)
    # If the requested builder doesn't state DB deps then it requires
    # all dbs!
    if not needed_colls:
        return None
    colls.update(needed_colls)
    return colls


def build(rc):
    """Builds all of the build targets."""
    for t in rc.build_targets:
        bldr = builder(t, rc)
        bldr.build()


def helper(rc):
    """Runs the helper targets."""
    hlpr = helpr(rc.helper_target, rc)
    hlpr.hlp()


def deploy(rc):
    """Deploys all of the deployment targets."""
    if not hasattr(rc, "deploy") or len(rc.deploy) == 0:
        raise RuntimeError("run control has no deployment targets!")
    for target in rc.deploy:
        dploy(rc, **target)


def classlist(rc):
    """Sets values for the class list."""
    from regolith.classlist import register

    register(rc)


def json_to_yaml(rc):
    """Converts JSON to YAML."""
    from regolith import fsclient

    for inp in rc.files:
        base, ext = os.path.splitext(inp)
        out = base + ".yaml"
        fsclient.json_to_yaml(inp, out)


def yaml_to_json(rc):
    """Converts YAML to JSON."""
    from regolith import fsclient

    for inp in rc.files:
        base, ext = os.path.splitext(inp)
        out = base + ".json"
        fsclient.yaml_to_json(inp, out)


def fs_to_mongo(rc: RunControl) -> None:
    """Convert database collection from filesystem to mongo db.

    Parameters
    ----------
    rc : RunControl
        The RunControl. The mongo client will be created according to 'mongodbpath' in it. The databases will
        be loaded according to the 'databases' in it.
    """
    from regolith.mongoclient import MongoClient

    client = MongoClient(rc)
    dbs = getattr(rc, "databases")
    for db in dbs:
        client.import_database(db)
    return


def mongo_to_fs(rc: RunControl) -> None:
    """Convert database collection from filesystem to mongo db.

    Parameters
    ----------
    rc : RunControl
        The RunControl. The mongo client will be created according to 'mongodbpath' in it. The databases will
        be loaded according to the 'databases' in it.
    """
    dbs = getattr(rc, "databases")
    for db in dbs:
        rc.client.export_database(db)
    return


def validate(rc):
    """Validate the combined database against the schemas."""
    from regolith.schemas import validate

    print("=" * 10 + "\nVALIDATING\n")
    any_errors = False
    if getattr(rc, "collection"):
        db = {rc.collection: rc.client.chained_db[rc.collection]}
    else:
        db = rc.client.chained_db
    for name, collection in db.items():
        errored_print = False
        for doc_id, doc in collection.items():
            v = validate(name, doc, rc.schemas)
            if v[0] is False:
                if errored_print is False:
                    errored_print = True
                    any_errors = True
                    print(f"Errors found in {name}")
                    print("=" * len(f"Errors found in {name}"))
                print(f"ERROR in {doc_id}:")
                pprint(v[1])
                cap = copy(v[1])
                for vv in v[1]:
                    pprint(doc.get(vv))
                print("-" * 15)
                print("\n")
    if not any_errors:
        print("\nNO ERRORS IN DBS\n" + "=" * 15)
    else:
        # uncomment when debugging scheme errors
        #
        sys.exit(f"Validation failed on some records\n {cap}")
        # sys.exit(f"Validation failed on some records")


def ghextractor(rc):
    """Extract GitHub repository metadata and write software YAML."""
    owner = rc.owner
    repo = getattr(rc, "repo", None)
    all_repos = getattr(rc, "all", False)
    token = getattr(rc, "token", None) or os.getenv("GITHUB_TOKEN")
    data = extract_github(
        owner,
        repo=repo,
        all_repos=all_repos,
        token=token,
    )
    yaml_dict = to_software_yaml(data)
    output = getattr(rc, "output", "software.yml")
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.allow_unicode = True
    with open(output, "w", encoding="utf-8") as f:
        yaml.dump(yaml_dict, f)
    print(f"Wrote {output}")


DISCONNECTED_COMMANDS = {
    "rc": lambda rc: print(rc._pformat()),
    "deploy": deploy,
    "store": storage.main,
    "json-to-yaml": json_to_yaml,
    "yaml-to-json": yaml_to_json,
    "gh-extractor": ghextractor,
}

CONNECTED_COMMANDS = {
    "add": add_cmd,
    "ingest": ingest,
    "app": app,
    "grade": grade,
    "build": build,
    "email": email,
    "classlist": classlist,
    "validate": validate,
    "helper": helper,
    "fs-to-mongo": fs_to_mongo,
    "mongo-to-fs": mongo_to_fs,
}
