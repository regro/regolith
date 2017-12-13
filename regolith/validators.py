"""Validators and convertors for regolith input."""
import collections
import os
import re
from getpass import getpass

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


def ensure_email(email):
    """Ensures the email top-level key is well formed."""
    email['url'] = ensure_string(email['url'])
    if 'cred' in email:
        email['cred'] = ensure_string(email['cred'])
    else:
        email['cred'] = email['url'] + '.cred'
    if not os.path.isfile(email['cred']):
        user = input('Email address for ' + email['url'] + ': ')
        password = getpass()
        s = user + '\n' + password
        with open(email['cred'], 'w') as f:
            f.write(s)
    with open(email['cred']) as f:
        email['from'] = f.readline().strip()
        email['password'] = f.readline().strip()
    email['user'] = email['from'].partition('@')[0]
    email['port'] = int(email.get('port', 0))
    email['verbosity'] = int(email.get('verbosity', 0))
    email['tls'] = to_bool(email.get('tls', False))
    return email


DEFAULT_VALIDATORS = {
    'backend': (is_string, ensure_string),
    'builddir': (is_string, ensure_string),
    'databases': (always_false, ensure_databases),
    'stores': (always_false, ensure_stores),
    'email': (always_false, ensure_email),
}


def validate_schema(record, schema, key=None):
    if isinstance(record, dict):
        total_keys = set(schema.keys())
        remove_keys = ['required', 'type', 'description']
        for k in remove_keys:
            if k in total_keys:
                total_keys.remove(k)
        total_keys.update(set(record.keys()))

        for k in total_keys:
            if k not in schema:
                pass
            if k not in record and schema[k].get('required', False):
                raise ValueError('{} is required'.format(k))
            elif k in record and k in schema:
                validate_schema(record[k], schema[k], k)
    elif isinstance(record, collections.Iterable) and not isinstance(record,
                                                                     str):
        for r in record:
            validate_schema(r, schema, key)
    else:
        if not isinstance(record, schema['type']):
            raise ValueError('Schema expected type: {}, '
                             'got type: {} in '
                             '{{{}:{}}}'.format(type(record),
                                                schema['type'], key, record))
