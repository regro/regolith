"""Builder for Lists of Presentations."""
import datetime
import time
from copy import deepcopy

from regolith.builders.basebuilder import LatexBuilderBase
from regolith.dates import month_to_int
from regolith.fsclient import _id_key
from regolith.sorters import position_key
from regolith.tools import (all_docs_from_collection, filter_grants,
                            fuzzy_retrieval)


def has_started(sd, sm, sy):
    s = '{}/{}/{}'.format(sd, month_to_int(sm), sy)
    start = time.mktime(datetime.datetime.strptime(s, "%d/%m/%Y").timetuple())
    return start < time.time()


def has_finished(ed, em, ey):
    e = '{}/{}/{}'.format(ed, month_to_int(em), ey)
    end = time.mktime(datetime.datetime.strptime(e, "%d/%m/%Y").timetuple())
    return end < time.time()


def is_current(sd, sm, sy, ed, em, ey):
    return has_started(sd, sm, sy) and not has_finished(ed, em, ey)


def is_pending(sd, sm, sy):
    return not has_started(sd, sm, sy)


class PresListBuilder(LatexBuilderBase):
    """Build list of talks and posters (presentations) from database entries"""
    btype = 'presentations'

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        gtx['people'] = sorted(all_docs_from_collection(rc.client, 'people'),
                               key=position_key, reverse=True)
        gtx['grants'] = sorted(all_docs_from_collection(rc.client, 'grants'),
                               key=_id_key)
        gtx['groups'] = sorted(all_docs_from_collection(rc.client, 'groups'),
                               key=_id_key)
        gtx['presentations'] = sorted(all_docs_from_collection(
            rc.client, 'presentations'), key=_id_key)
        gtx['institutions'] = sorted(all_docs_from_collection(
            rc.client, 'institutions'), key=_id_key)
        gtx['all_docs_from_collection'] = all_docs_from_collection
        gtx['float'] = float
        gtx['str'] = str
        gtx['zip'] = zip

    def latex(self):
        """Render latex template"""
        for group in self.gtx['groups']:
            pi = fuzzy_retrieval(self.gtx['people'], ['aka', 'name', '_id'],
                                 group['pi_name'])['name']

        presentationsdict = deepcopy(self.gtx['presentations'])
        for pres in presentationsdict:
            pauthors = pres['authors']
            if isinstance(pauthors, str):
                pauthors = [pauthors]
            pres['authors'] = [
                fuzzy_retrieval(self.gtx['people'], ['aka', 'name', '_id'],
                                author)['name'] for author in pauthors]
            if 'institution' in pres:
                pres['institution'] = fuzzy_retrieval(self.gtx['institutions'],
                                                      ['aka', 'name', '_id'],
                                                      pres['institution'])
        self.render('preslist.tex', 'presentations.tex', pi=pi,
                    presentations=presentationsdict)
        self.pdf('presentations')
