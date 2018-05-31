"""Builder for Lists of Presentations."""
from copy import deepcopy

from regolith.builders.basebuilder import LatexBuilderBase
from regolith.fsclient import _id_key
from regolith.sorters import position_key
from regolith.tools import (all_docs_from_collection, fuzzy_retrieval)


class PresListBuilder(LatexBuilderBase):
    """Build list of talks and posters (presentations) from database entries"""
    btype = 'preslist'

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
                                 group['pi_name'])

        presentationsdict = deepcopy(self.gtx['presentations'])
        for pres in presentationsdict:
            pauthors = pres['authors']
            if isinstance(pauthors, str):
                pauthors = [pauthors]
            pres['authors'] = [
                fuzzy_retrieval(self.gtx['people'], ['aka', 'name', '_id'],
                                author)['name'] for author in pauthors]

            authorlist = ', '.join(pres['authors'])
            pres['authors'] = authorlist
            if 'institution' in pres:
                pres['institution'] = fuzzy_retrieval(self.gtx['institutions'],
                                                      ['aka', 'name', '_id'],
                                                      pres['institution'])
                if 'department' in pres:
                    print('simon, ', pres['institution']['departments']
                    [pres['department']])
                    fulldept = pres['institution']['departments'][pres['department']]
                    pres['department'] = fulldept
        self.render('preslist.tex', 'presentations.tex', pi=pi,
                    presentations=presentationsdict)
        self.pdf('presentations')
