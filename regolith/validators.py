"""Validators and convertors for regolith input."""
import re

from regolith.tools import string_types

def noop(x):
    """Does nothing, just returns the input."""
    return x


def is_int(x):
    """Tests if something is an integer"""
    return isinstance(x, int)


def always_true(x):
    """Returns True"""
    return True


def always_false(x):
    """Returns False"""
    return False


def is_bool(x):
    """Tests if something is a boolean"""
    return isinstance(x, bool)

def is_string(x):
    """Tests if something is a string"""
    return isinstance(x, string_types)


_FALSES = frozenset(['', '0', 'n', 'f', 'no', 'none', 'false'])


def to_bool(x):
    """"Converts to a boolean in a semantically meaningful way."""
    if isinstance(x, bool):
        return x
    elif isinstance(x, string_types):
        return False if x.lower() in _FALSES else True
    else:
        return bool(x)


def ensure_string(x):
    """Returns a string if x is not a string, and x if it already is."""
    if isinstance(x, string_types):
        return x
    else:
        return str(x)

def ensure_database(db):
    db['name'] = ensure_string(db['name'])
    db['url'] = ensure_string(db['url'])
    db['path'] = ensure_string(db['path'])
    db['public'] = to_bool(db.get('public', True))
    return db
    

def ensure_databases(dbs):
    """Ensures each dataset in a list of databases"""
    return list(map(ensure_database, dbs))


def ensure_store(store):
    store['name'] = ensure_string(store['name'])
    store['url'] = ensure_string(store['url'])
    store['path'] = ensure_string(store.get('path', None) or '')
    store['public'] = to_bool(store.get('public', True))
    return store
    

def ensure_stores(stores):
    """Ensures each store in a list of stores"""
    return list(map(ensure_store, stores))


DEFAULT_VALIDATORS = {
    'builddir': (is_string, ensure_string), 
    'databases': (always_false, ensure_databases),
    'stores': (always_false, ensure_stores),
    }
