"""Find, read and write a person's record, which may be split across
several databases.

A person's record is joined from every database that holds part of it. A
list, such as service, that more than one database holds is joined end
to end, so each part has to be written back to its own database.
"""

import io
import warnings

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

from regolith.schemas import validate
from regolith.tools import fragment_retrieval, public_and_private_databases

PEOPLE_COLL = "people"
# Fields kept in the private database when a person does not have them yet
PRIVATE_PERSON_FIELDS = ("appointments", "notes", "miscellaneous", "home_address", "office")


def person_names(person):
    """Return a person's id, name and akas."""
    aka = person.get("aka") or []
    aka = [aka] if isinstance(aka, str) else list(aka)
    return [person.get("_id"), person.get("name")] + aka


def find_person(people, wanted):
    """Find a person from their id, name or one of their akas.

    An exact id wins. Otherwise the id, name and akas are matched
    ignoring case, and when nothing matches, the people whose id, name
    or aka contains what was given are offered instead.

    Parameters
    ----------
    people : list of dict
        The people to look in.
    wanted : str
        The id, name or aka of the person, or part of one.

    Returns
    -------
    person : dict or None
        The person, or None when there is no single person it names.
    candidates : list of dict
        The people it might mean when there is no single one.
    """
    exact = [person for person in people if person.get("_id") == wanted]
    if exact:
        return exact[0], []
    named = [
        person
        for person in people
        if wanted.casefold() in (str(name).casefold() for name in person_names(person) if name)
    ]
    if len(named) == 1:
        return named[0], []
    if named:
        return None, named
    return None, fragment_retrieval(people, ["_id", "name", "aka"], wanted)


def person_parts(rc, person_id):
    """Return the part of a person's record each database holds.

    Parameters
    ----------
    rc : RunControl
        The run control, with the client and databases.
    person_id : str
        The id of the person.

    Returns
    -------
    dict
        The part each database holds, empty when it holds none, keyed
        by database name in the order of regolithrc.json.
    """
    return {
        database["name"]: rc.client.find_one(database["name"], PEOPLE_COLL, {"_id": person_id}) or {}
        for database in rc.databases
    }


def database_for(rc, parts, field, private=False):
    """Return the database to write a field of a person's record to.

    The database already holding the field is used, the last when more
    than one does, since that is the one a read shows. A field the person
    does not have yet goes to the private database if it is private,
    and to the public one otherwise.

    Parameters
    ----------
    rc : RunControl
        The run control, with the databases.
    parts : dict
        The part of the record each database holds.
    field : str
        The field.
    private : bool, optional
        The switch for keeping a new field private.

    Returns
    -------
    str
        The name of the database.
    """
    holding = [name for name, part in parts.items() if field in part]
    if holding:
        return holding[-1]
    public_database, private_database = public_and_private_databases(rc.databases)
    if private or field in PRIVATE_PERSON_FIELDS:
        return private_database or public_database or rc.database
    return public_database or private_database or rc.database


def write_field(rc, database, person_id, field, value):
    """Write one field of a person's record to one database.

    Parameters
    ----------
    rc : RunControl
        The run control, with the client.
    database : str
        The name of the database.
    person_id : str
        The id of the person.
    field : str
        The field.
    value : object
        The value to write.
    """
    rc.client.update_one(database, PEOPLE_COLL, {"_id": person_id}, {field: value}, partial=True, upsert=True)


def _yaml():
    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.width = 4096
    return yaml


def section_to_text(person, field, parts, databases):
    """Return one field of a person's record as YAML to edit, grouped by
    the database each part is stored in.

    Parameters
    ----------
    person : dict
        The person.
    field : str
        The field, a list or dict.
    parts : dict
        The part of the record each database holds.
    databases : list of dict
        The databases from regolithrc.json, with their public flags.

    Returns
    -------
    str
        The text to edit.
    """
    visibility = {database["name"]: "public" if database.get("public") else "private" for database in databases}
    lines = [
        f"# {field} of {person.get('name', person['_id'])}, under the database each part is stored in:",
        *[f"#   {name} is {visibility[name]}" for name in parts],
        "# Move an entry to another database to change who can see it. Delete an entry to remove it.",
        "# Save and close the editor to store the changes. To leave them unchanged, close without saving.",
        "",
    ]
    grouped = {name: part.get(field) for name, part in parts.items()}
    stream = io.StringIO()
    _yaml().dump(grouped, stream)
    return "\n".join(lines) + stream.getvalue()


def validate_field(field, value, person_id, schemas):
    """Check one field of a person's record against the schema.

    The field is checked in full, so its own entries must have the
    fields they require, while the rest of the record is not needed.

    Parameters
    ----------
    field : str
        The field.
    value : object
        Its value.
    person_id : str
        The id of the person.
    schemas : dict
        The schemas.

    Returns
    -------
    list of str
        The problems found, in words for someone who does not program.
    """
    people_schema = schemas[PEOPLE_COLL]
    field_schema = {PEOPLE_COLL: {"_id": people_schema["_id"], field: people_schema[field]}}
    # Values outside a field's preferred entries only warn, and older entries are full of them
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        valid, errors = validate(PEOPLE_COLL, {"_id": person_id, field: value}, field_schema)
    return [] if valid else _readable(errors)


def _readable(errors, path=""):
    lines = []
    if isinstance(errors, dict):
        for key, value in errors.items():
            label = f"entry {key + 1}" if isinstance(key, int) else str(key)
            lines += _readable(value, f"{path}, {label}" if path else label)
    elif isinstance(errors, list):
        for item in errors:
            lines += _readable(item, path)
    else:
        lines.append(f"{path}: {errors}")
    return lines


def section_from_text(text, field, person_id, parts, schemas):
    """Return the parts of one field read back from edited YAML, and the
    problems with them.

    Parameters
    ----------
    text : str
        The YAML, as written by section_to_text and then edited.
    field : str
        The field.
    person_id : str
        The id of the person.
    parts : dict
        The part of the record each database holds, before editing.
    schemas : dict
        The schemas, to check the field against.

    Returns
    -------
    changes : dict
        The new value of the field for each database whose part changed.
    problems : list of str
        Every problem found, in words for someone who does not program.
    """
    try:
        loaded = YAML(typ="safe").load(text) or {}
    except YAMLError as error:
        return {}, [f"The text could not be read as YAML: {error}"]
    if not isinstance(loaded, dict):
        return {}, ["The text must list each database by name, followed by its part, as it was shown."]
    problems = [
        f"{name} is not one of the databases, which are {', '.join(parts)}."
        for name in loaded
        if name not in parts
    ]
    changes = {}
    for name, value in loaded.items():
        if name not in parts:
            continue
        before = parts[name].get(field)
        if value == before or (value is None and before is None):
            continue
        if value is None:
            value = [] if isinstance(before, list) else {}
        problems += [f"In {name}, {line}" for line in validate_field(field, value, person_id, schemas)]
        changes[name] = value
    return changes, problems
