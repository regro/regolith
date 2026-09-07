"""Pieces shared by the mission control tools.

Kept apart from ``regolith.tools`` so that reading or writing a mission
control document does not import the rest of it.
"""

import secrets

# Lowercase base32 without the characters that are read for one another, so
# an id can be said aloud in a meeting and typed back correctly
ID_ALPHABET = "abcdefghijkmnpqrstuvwxyz23456789"
ID_LENGTH = 6


def short_id(taken=(), length=ID_LENGTH):
    """Return a short id that nothing has taken yet.

    The id appears beside every line of a mission control document, so it
    is as short as it can be while staying unique.  Six characters of this
    alphabet is about nine hundred million ids, and clashes are not left
    to chance: an id already taken is thrown away and another drawn.

    Parameters
    ----------
    taken : iterable of str, optional
        The ids already in use.
    length : int, optional
        How many characters to draw.  The default is six.

    Returns
    -------
    str
        The new id.
    """
    taken = set(taken)
    while True:
        candidate = "".join(secrets.choice(ID_ALPHABET) for _ in range(length))
        if candidate not in taken:
            return candidate


def struck(text, status):
    """Return the text struck through when the thing is finished.

    Striking a line through is how the group has always marked something
    off, so a rendered document does it too, and reading one back takes a
    struck line as finished whether or not its box was ticked.

    Parameters
    ----------
    text : str
        The text of the goal or task.
    status : str
        Its status.

    Returns
    -------
    str
        The text, struck through when it is finished.
    """
    return f"~~{text}~~" if status == "finished" else text
