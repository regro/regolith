"""Small shared pieces that carry no heavy dependencies.

These live outside ``regolith.tools`` so that a module wanting one of
them does not import the rest of it, which reaches habanero and google's
api client and costs a quarter of a second.
"""

string_types = (str, bytes)
unicode_type = str


def fallback(cond, backup):
    """Decorator for returning the object if cond is true and a backup
    if cond is false."""

    def dec(obj):
        return obj if cond else backup

    return dec
