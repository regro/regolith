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
            The id of the group

        Returns
        -------
        list:
            The list of ids of the people in the group

        Notes
        -----
        - Groups that are being tracked are listed in the groups collection
        with a name and an id.
        - People are in a group during an educational or employment period.
        - To assign a person to a tracked group during one such period, add
        a "group" key to that education/employment item with a value
        that is the group name.
        - This function takes the group id that is passed and searches
        the people collection for all people that have been
        assigned to that group in some period of time and returns a list of
        """
        grpmembers = []
        for person in self.gtx['people']:
            for position in person.get('education', {}):
                if position.get('group', None) == grp:
                    if person['_id'] not in grpmembers:
                        grpmembers.append(person['_id'])
            for position in person.get('employment', {}):
                if position.get('group', None) == grp:
                    if person['_id'] not in grpmembers:
                        grpmembers.append(person['_id'])
        return grpmembers

    def latex(self):
        """Render latex template"""
        for group in self.gtx['groups']:
            pi = fuzzy_retrieval(self.gtx['people'], ['aka', 'name', '_id'],
                                 group['pi_name'])

        #        all_grps = [name.key() for name in self.gtx['groups']]
        #        all_grps = self.gtx['groups'].getkeys()
        #        print('all grps',all_grps)
        # List(set(first_list)|set(second_list))
        # fixme, want to iterate over all groups in groups.yml
        grp = self.rc.groupname
        grpmember_ids = self.group_member_ids(grp)
        # remove, don't think I need it here
        # grpmembers = [fuzzy_retrieval(self.gtx['people'], ['_id', 'aka', 'name'],
        #                       person) for person in grpmember_ids]

        for member in grpmember_ids:
            presentationsdict = deepcopy(self.gtx['presentations'])
            for pres in presentationsdict:
                pauthors = pres['authors']
                if isinstance(pauthors, str):
                    pauthors = [pauthors]
                if member in pauthors:
                    pres['authors'] = [
                        fuzzy_retrieval(self.gtx['people'],
                                        ['aka', 'name', '_id'],
                                        author)['name'] for author in pauthors]

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
            outfile = 'presentations-' + member + '.tex'
            self.render('preslist.tex', outfile, pi=pi,
                        presentations=presentationsdict)
            self.pdf('presentations')
