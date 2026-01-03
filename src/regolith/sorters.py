"""Builder for websites."""

import string

from regolith.dates import date_to_float


def doc_date_key(document):
    """Convert a dict of Datetime object to float serialization of date
    info.

    Parameters
    ----------
    document:  dict
        the document that is expected to contain date-like information in "year" and/or "month"

    Returns
    -------
    the float serialization of the date information in the document
    """
    return date_to_float(document.get("year", 1970), document.get("month", "jan"))


def doc_date_key_high(document):
    """Convert a dict of highest Datetime object to float serialization
    of date info.

    Parameters
    ----------
    document: dict
        the document that is expected to contain date-like information in "end_year" and/or "end_month"

    Returns
    -------
    the float serialization of the end date information in the document
    """
    return date_to_float(document.get("year", 1970), document.get("month", "dec"))


def ene_date_key(document):
    """Convert a dict of ene Datetime object to float serialization of
    date info.

    Parameters
    ----------
    document: dict
        the document that is expected to contain date-like information in "end_year" and/or "end_month"

    Returns
    -------
    the float serialization of the date information in the document
    """
    return date_to_float(document.get("end_year", 4242), document.get("end_month", "dec"))


def category_val(document):
    """Convert the category of a document into string of category info.

    Parameters
    ----------
    document : dict
        The dict of all corresponding categories for objects

    Returns
    -------
    The string of the category item.
    """
    return document.get("category", "<uncategorized>")


def level_val(document):
    """Convert the level of a document into string of category info.

    Parameters
    ----------
    document: dict
        The document

    Returns
    -------
    The string representing the level.
    """
    return document.get("level", "<no-level>")


def id_key(document):
    """Convert the id-key of a document into a string.

    Parameters
    ----------
    document: dict
        The document

    Returns
    -------
    The string of the _id
    """
    return document.get("_id", "")


def date_key(x):
    if "end_year" in x:
        v = date_to_float(x["end_year"], x.get("end_month", "jan"), x.get("end_day", 0))
    elif "year" in x:
        v = date_to_float(x["year"], x.get("month", "jan"), x.get("day", 0))
    elif "begin_year" in x:
        v = date_to_float(x["begin_year"], x.get("begin_month", "jan"), x.get("begin_day", 0))
    else:
        raise KeyError("could not find year in " + str(x))
    return v


POSITION_LEVELS = {
    "": -1,
    "editor": -1,
    "unknown": -1,
    "undergraduate research assistant": 1,
    "undergraduate researcher": 1,
    "intern": 1,
    "masters research assistant": 2.5,
    "masters researcher": 2.5,
    "visiting student": 2,
    "graduate research assistant": 3,
    "teaching assistant": 3,
    "research assistant": 2,
    "post-doctoral scholar": 4,
    "research fellow": 4,
    "assistant scientist": 4,
    "assistant lecturer": 4,
    "lecturer": 5,
    "research scientist": 4.5,
    "associate scientist": 6,
    "adjunct scientist": 5,
    "senior assistant lecturer": 5,
    "research associate": 5,
    "reader": 5,
    "ajunct professor": 5,
    "adjunct professor": 5,
    "consultant": 5,
    "programer": 5,
    "programmer": 5,
    "visiting scientist": 5,
    "research assistant professor": 5,
    "assistant professor": 8,
    "assistant physicist": 8,
    "associate professor": 9,
    "associate physicist": 9,
    "professor emeritus": 9,
    "visiting professor": 9,
    "manager": 10,
    "director": 10,
    "scientist": 10,
    "engineer": 10,
    "physicist": 10,
    "professor": 11,
    "president": 10,
    "distinguished professor": 12,
}


def position_key(x):
    """Sorts a people based on their position in the research group."""
    pos = x.get("position", "").casefold()
    first_letter_last = x.get("name", "zappa").rsplit(None, 1)[-1][0].upper()
    try:
        backward_position = 26 - string.ascii_uppercase.index(first_letter_last)
    except ValueError:
        raise ValueError(f"{x.get('_id')} has improperly composed name")
    return POSITION_LEVELS.get(pos, -1), backward_position
