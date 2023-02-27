"""Builder for Reading Lists."""

from habanero import Crossref

from regolith.builders.basebuilder import LatexBuilderBase
from regolith.fsclient import _id_key
from regolith.sorters import position_key
from regolith.tools import (
    all_docs_from_collection,
    get_formatted_crossref_reference,
)

class ReadingListsBuilder(LatexBuilderBase):
    """Build reading lists from database entries"""

    btype = "readinglists"
    needed_colls = ['people', 'reading_lists']

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        self.cr = Crossref()
        cr = self.cr
        rc.verbose = True
        gtx["people"] = sorted(
            all_docs_from_collection(rc.client, "people"),
            key=position_key,
            reverse=True,
        )
        gtx["reading_lists"] = sorted(
            all_docs_from_collection(rc.client, "reading_lists"), key=_id_key
        )
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def latex(self):
        """Render latex template"""
        rc = self.rc

        for rlist in self.gtx["reading_lists"]:
            listid = rlist["_id"]
            outfile_bib = listid

            n = 1
            for paper in rlist['papers']:
                doi = paper.get('doi')
                paper['text'] = paper['text'].strip('.').strip()
                if doi == 'tbd' or doi == '':
                    doi = None
                url = paper.get('url')
                if doi:
                    # if rc.verbose:
                    #     print(f"getting {doi} for {paper.get('tite')}")
                    ref, ref_date = get_formatted_crossref_reference(doi)
                    # if rc.verbose:
                    #     try:
                    #         print(f"got ref: {ref}")
                    #     except:
                    #         print("obtained ref but print error")
                    paper.update({'reference': ref, 'ref_date': ref_date, 'n': n, 'label': 'DOI'})
                    n += 1
                elif url:
                    paper['doi'] = url
                    paper.update({'n': n, 'label': 'URL'})
                    n += 1
                else:
                    paper.update({'n': n})
                    n += 1

            self.render(
                "rlistbibfile.txt",
                outfile_bib + ".txt",
                rlist=rlist,
            )
