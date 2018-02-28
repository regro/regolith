"""Builder for current and pending reports."""
import os
import subprocess
from glob import glob

from regolith.basebuilder import BuilderBase
from regolith.sorters import ene_date_key, position_key
from regolith.tools import (all_docs_from_collection, month_and_year,
                            filter_publications, filter_projects,
                            filter_grants, awards_grants_honors, latex_safe,
                            LATEX_OPTS, make_bibtex_file)


class CPBuilder(BuilderBase):
    """Build current and pending report from database entries"""
    btype = 'cv'

    def __init__(self, rc):
        super().__init__(rc)
        self.cmds = ['latex', 'pdf', 'clean']

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        gtx['month_and_year'] = month_and_year
        gtx['latex_safe'] = latex_safe
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
            grants, _, _ = filter_grants(self.gtx['grants'], {pi['name']})
            
            self.render('current_pending.tex', 'cpp.tex',
                        pi=pi,
                        grants=grants)
