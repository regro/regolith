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

    def group_member_ids(self, grp):
        """Get a list of all group member ids

        Parameters
        ----------
        grp: string
            The id of the group in groups.yml

        Returns
        -------
        set:
            The set of ids of the people in the group

        Notes
        -----
        - Groups that are being tracked are listed in the groups.yml collection
        with a name and an id.
        - People are in a group during an educational or employment period.
        - To assign a person to a tracked group during one such period, add
        a "group" key to that education/employment item with a value
        that is the group id.
        - This function takes the group id that is passed and searches
        the people collection for all people that have been
        assigned to that group in some period of time and returns a list of
        """
        grpmembers = set()
        for person in self.gtx['people']:
            for k in ['education', 'employment']:
                for position in person.get(k, {}):
                    if position.get('group', None) == grp:
                        grpmembers.add(person['_id'])
        print(grpmembers)
        return grpmembers

    def latex(self):
        """Render latex template"""
        for group in self.gtx['groups']:
            grp = group['_id']
            grpmember_ids = self.group_member_ids(grp)
            for member in grpmember_ids:
                presentations = deepcopy(self.gtx['presentations'])
                presclean = list()
                
                # build the filtered collection
                for pres in presentations:
                    pauthors = pres['authors']
                    if isinstance(pauthors, str):
                        pauthors = [pauthors]
                    authorids = [
                        fuzzy_retrieval(self.gtx['people'],
                                        ['aka', 'name', '_id'],
                                        author)['_id'] for author in
                        pauthors]
                    if member in authorids:
                        presclean.append(pres)

                # format the filtered collection
                for pres in presclean:
                    pauthors = pres['authors']
                    if isinstance(pauthors, str):
                        pauthors = [pauthors]
                    pres['authors'] = [
                        fuzzy_retrieval(self.gtx['people'],
                                        ['aka', 'name', '_id'],
                                        author)['name'] for author in
                        pauthors]
                    authorlist = ', '.join(pres['authors'])
                    pres['authors'] = authorlist
                    if 'institution' in pres:
                        pres['institution'] = fuzzy_retrieval(
                            self.gtx['institutions'],
                            ['aka', 'name', '_id'],
                            pres['institution'])
                        if 'department' in pres:
                            pres['department'] = \
                                pres['institution']['departments'][
                                    pres['department']]
                if len(presclean) > 0:
                    outfile = 'presentations-' + grp + '-' + member + '.tex'
                    pi = [person for person in self.gtx['people']
                          if person['_id'] is member][0]
                    self.render('preslist.tex', outfile, pi=pi,
                                presentations=presclean)
#                    self.pdf('presentations')
