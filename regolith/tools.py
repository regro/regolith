"""Misc. regolith tools.
"""
import os
import re
import sys
import platform

import pymongo

if sys.version_info[0] >= 3:
    string_types = (str, bytes)
    unicode_type = str
else:
    string_types = (str, unicode)
    unicode_type = unicode

DEFAULT_ENCODING = sys.getdefaultencoding()

ON_WINDOWS = (platform.system() == 'Windows')
ON_MAC = (platform.system() == 'Darwin')
ON_LINUX = (platform.system() == 'Linux')
ON_POSIX = (os.name == 'posix')

if pymongo.version.split('.')[0] == '2':
    ON_PYMONGO_V2 = True
    ON_PYMONGO_V3 = False
else:
    ON_PYMONGO_V2 = False
    ON_PYMONGO_V3 = True

def fallback(cond, backup):
    """Decorator for returning the object if cond is true and a backup if cond is false.
    """
    def dec(obj):
        return obj if cond else backup
    return dec

@fallback(ON_PYMONGO_V2, None)
class InsertOneProxy(object):

    def __init__(self, inserted_id, acknowledged):
        self.inserted_id = inserted_id
        self.acknowledged = acknowledged


def insert_one(coll, doc):
    if ON_PYMONGO_V2:
        i = coll.insert(doc)
        return InsertOneProxy(i, True)
    else:
        return coll.insert_one(doc)

def insert_many(coll, docs):
    if ON_PYMONGO_V2:
        return coll.insert(docs)
    else:
        return coll.insert_many(docs)

def delete_one(coll, doc):
    if ON_PYMONGO_V2:
        return coll.remove(doc, multi=False)
    else:
        return coll.delete_one(doc)
    
def all_docs_from_collection(client, collname):
    """Yield all entries in for all collections of a given name in a given database."""
    for dbname in client.database_names():
        if dbname == 'local':
            continue
        db = client[dbname]
        if collname not in db.collection_names():
            continue
        yield from db[collname].find()


MONTHS = {
    'jan': 1,
    'jan.': 1,
    'january': 1,
    'feb': 2,
    'feb.': 2,
    'february': 2,
    'mar': 3,
    'mar.': 3,
    'march': 3,
    'apr': 4,
    'apr.': 4,
    'april': 4,
    'may': 5,
    'may.': 5,
    'jun': 6,
    'jun.': 6,
    'june': 6,
    'jul': 7,
    'jul.': 7,
    'july': 7,
    'aug': 8,
    'aug.': 8,
    'august': 8,
    'sep': 9,
    'sep.': 9,
    'sept': 9,
    'sept.': 9,
    'september': 9,
    'oct': 10,
    'oct.': 10,
    'october': 10,
    'nov': 11,
    'nov.': 11,
    'november': 11,
    'dec': 12,
    'dec.': 12,
    'december': 12,
    }

def date_to_float(y, m, d=0):
    """Converts years / months / days to a float, eg 2015.0818 is August 18th 2015."""
    y = int(y)
    d = int(d)
    return y + (MONTHS[m.lower()]/10.0) + (d/10000.0)

