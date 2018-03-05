"""Builder for current and pending reports."""
import time

import datetime

from regolith.basebuilder import LatexBuilderBase
from regolith.sorters import position_key
from regolith.tools import (all_docs_from_collection, filter_grants)


def is_current(sd, sm, sy, ed, em, ey):
    s = '{}/{}/{}'.format(sd, sm, sy)
    e = '{}/{}/{}'.format(ed, em, ey)
    start = time.mktime(datetime.datetime.strptime(s, "%d/%m/%Y").timetuple())
    end = time.mktime(datetime.datetime.strptime(e, "%d/%m/%Y").timetuple())
    return start < time.time() < end


def is_pending(sd, sm, sy):
    s = '{}/{}/{}'.format(sd, sm, sy)
    start = time.mktime(datetime.datetime.strptime(s, "%d/%m/%Y").timetuple())
    return time.time() < start


class CPBuilder(LatexBuilderBase):
    """Build current and pending report from database entries"""
    btype = 'cp'

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        gtx['people'] = sorted(all_docs_from_collection(rc.client, 'people'),
                               key=position_key, reverse=True)
        gtx['grants'] = sorted(all_docs_from_collection(rc.client, 'grants'),
                               key=position_key, reverse=True)
        gtx['groups'] = sorted(all_docs_from_collection(rc.client, 'groups'),
                               key=position_key, reverse=True)
        gtx['all_docs_from_collection'] = all_docs_from_collection

    def latex(self):
        """Render latex template"""
        for group in self.gtx['groups']:
            pi_name = group['pi']
            for p in self.gtx['people']:
                if pi_name in frozenset(p.get('aka', []) + [p['name']]):
                    pi = p
                    break

            current_grants = [g for g in self.gtx['grants']
                              if is_current(*[g[s] for s in ['start_day',
                                                             'start_month',
                                                             'start_year',
                                                             'end_day',
                                                             'end_month',
                                                             'end_year']])]
            pending_grants = [g for g in self.gtx['grants']
                              if is_pending(*[g[s] for s in ['start_day',
                                                             'start_month',
                                                             'start_year', ]])]
            grants, _, _ = filter_grants(current_grants + pending_grants,
                                         {pi['name']})

            self.render('current_pending.tex', 'cpp.tex', pi=pi, grants=grants)
