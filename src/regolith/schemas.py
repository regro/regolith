"""Database schemas, examples, and tools."""

import copy
import json
from pathlib import Path
from warnings import warn

from cerberus import Validator
from flatten_dict import flatten, unflatten

from .sorters import POSITION_LEVELS

SORTED_POSITION = sorted(POSITION_LEVELS.keys(), key=POSITION_LEVELS.get)
PROJECTUM_ACTIVE_STATI = ["proposed", "converged", "started"]
PROJECTUM_PAUSED_STATI = ["backburner", "paused"]
PROJECTUM_CANCELLED_STATI = ["cancelled"]
PROJECTUM_FINISHED_STATI = ["finished"]
PROJECTUM_STATI = list(
    PROJECTUM_ACTIVE_STATI + PROJECTUM_PAUSED_STATI + PROJECTUM_CANCELLED_STATI + PROJECTUM_FINISHED_STATI
)

alloweds = {
    "ACTIVITIES_TYPES": ["teaching", "research"],
    "AGENCIES": ["nsf", "doe", "other"],
    "APPOINTMENTS_TYPES": ["gra", "ss", "pd", "ug"],
    "APPOINTMENTS_STATI": ["proposed", "appointed", "finalized"],
    "COMMITTEES_TYPES": ["phdoral", "phddefense", "phdproposal", "promotion"],
    "COMMITTEES_LEVELS": ["department", "school", "university", "external"],
    "EXPENSES_STATI": ["unsubmitted", "submitted", "reimbursed", "declined"],
    "EXPENSES_TYPES": ["travel", "business"],
    "FACILITIES_TYPES": [
        "teaching",
        "research",
        "shared",
        "other",
        "teaching_wish",
        "research_wish",
    ],
    "GRANT_STATI": ["pending", "declined", "accepted", "in-prep"],
    "GRANT_ROLES": ["pi", "copi", "co-pi"],
    "MILESTONE_TYPES": [
        "mergedpr",
        "meeting",
        "other",
        "paper",
        "release",
        "email",
        "handin",
        "purchase",
        "approval",
        "presentation",
        "report",
        "submission",
        "decision",
        "demo",
        "skel",
    ],
    "POSITION_STATI": [
        "pi",
        "adjunct",
        "high-school",
        "undergrad",
        "ms",
        "phd",
        "postdoc",
        "visitor-supported",
        "visitor-unsupported",
        "research-associate",
    ],
    "PRESENTATION_TYPES": [
        "award",
        "colloquium",
        "contributed_oral",
        "invited",
        "keynote",
        "plenary",
        "poster",
        "seminar",
        "tutorial",
        "other",
    ],
    "PRESENTATION_STATI": [
        "in-prep",
        "submitted",
        "accepted",
        "declined",
        "cancelled",
        "postponed",
    ],
    "PROJECT_TYPES": ["ossoftware", "funded", "outreach"],
    "PROJECTUM_ACTIVE_STATI": PROJECTUM_ACTIVE_STATI,
    "PROJECTUM_PAUSED_STATI": PROJECTUM_PAUSED_STATI,
    "PROJECTUM_CANCELLED_STATI": PROJECTUM_CANCELLED_STATI,
    "PROJECTUM_FINISHED_STATI": PROJECTUM_FINISHED_STATI,
    "PROJECTUM_STATI": PROJECTUM_STATI,
    "PROPOSAL_STATI": ["pending", "declined", "accepted", "inprep", "submitted"],
    "PUBLICITY_TYPES": ["online", "article"],
    "REVIEW_STATI": [
        "invited",
        "accepted",
        "declined",
        "downloaded",
        "inprogress",
        "submitted",
        "cancelled",
    ],
    "REVIEW_RECOMMENDATIONS": ["reject", "asis", "smalledits", "diffjournal", "majoredits"],
    "SERVICE_TYPES": ["profession", "university", "school", "department"],
    "SORTED_POSITION": SORTED_POSITION,
    "TODO_STATI": ["started", "finished", "cancelled", "paused"],
    "OPTIONAL_KEYS_INSTITUTIONS": [
        "aka",
        "departments",
        "schools",
        "state",
        "street",
        "zip",
    ],
    # for status of kickoff, deliverable, milestones, and the projectum
}


def _update_dict_target(d, filter, new_value):
    flatd = flatten(d)
    for filtk, filtv in filter.items():
        for k, v in flatd.items():
            if filtk in k:
                if filtv == v:
                    flatd.update({k: new_value})
    unflatd = unflatten(flatd)
    return unflatd


def insert_alloweds(doc, alloweds, key):
    working_doc = copy.deepcopy(doc)
    for k, v in alloweds.items():
        working_doc = _update_dict_target(working_doc, {key: k}, v)
    return working_doc


def load_schemas():
    here = Path(__file__).parent
    schema_file = here / "schemas.json"
    with open(schema_file, "r", encoding="utf-8") as schema_file:
        raw_schemas = json.load(schema_file)
    schemas = insert_alloweds(raw_schemas, alloweds, "eallowed")
    return schemas


def load_exemplars():
    here = Path(__file__).parent
    exemplar_file = here / "exemplars.json"
    with open(exemplar_file, "r", encoding="utf-8") as efile:
        exemplars = json.load(efile)
    return exemplars


EXEMPLARS = load_exemplars()
SCHEMAS = load_schemas()

for s in SCHEMAS:
    SCHEMAS[s]["files"] = {
        "description": "Files associated with the document",
        # TODO: fix this since this is currently coming out a CommentedMap (+1: Yevgeny)
        # "type": "list",
        # "schema": {"type": "string"},
        "required": False,
    }


class NoDescriptionValidator(Validator):
    def _validate_description(self, description, field, value):
        """Don't validate descriptions.

        The rule's arguments are validated against this schema: {'type':
        'string'}
        """
        if False:
            pass

    def _validate_eallowed(self, eallowed, field, value):
        """Test if value is in list.

        The rule's arguments are validated against this schema: {'type':
        'list'}
        """
        if value not in eallowed:
            warn(
                '"{}" is not in the preferred entries for "{}", please '
                "consider changing this entry to conform or add this to the "
                "``eallowed`` field in the schema.".format(value, field)
            )


def validate(coll, record, schemas):
    """Validate a record for a given db.

    Parameters
    ----------
    coll : str
        The name of the db in question
    record : dict
        The record to be validated
    schemas : dict
        The schema to validate against

    Returns
    -------
    rtn : bool
        True is valid
    errors: dict
        The errors encountered (if any)
    """
    if coll in schemas:
        schema = copy.deepcopy(schemas[coll])
        v = NoDescriptionValidator(schema)
        return v.validate(record), v.errors
    else:
        return True, ()
