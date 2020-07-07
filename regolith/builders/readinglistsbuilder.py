"""Builder for Reading Lists."""

from copy import deepcopy, copy
import datetime, sys
import requests
from habanero import Crossref

from regolith.builders.basebuilder import LatexBuilderBase
from regolith.fsclient import _id_key
from regolith.sorters import position_key
from regolith.tools import (
    all_docs_from_collection,
    fuzzy_retrieval,
    number_suffix,
)
from regolith.stylers import sentencecase, month_fullnames
from regolith.dates import month_to_int


class ReadingListsBuilder(LatexBuilderBase):
    """Build reading lists from database entries"""

    btype = "readinglists"
    needed_dbs = ['people', 'reading_lists']

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        self.cr = Crossref()
        cr = self.cr
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

        for rlist in self.gtx["reading_lists"]:
            listid = rlist["_id"]
            outfile_bib = listid

            n = 1
            for paper in rlist['papers']:
                # fixme: code here to get info from crossref
                doi = paper.get('doi')
                url = paper.get('url')
#                if doi == 'tbd':
#                    pass
#                    print(
#                        "  doi needed for paper: {}".format(paper.get('text')))
                if doi and doi != 'tbd':
                    article = self.cr.works(ids=doi)
                    authorlist = [
                        "{} {}".format(a['given'].strip(), a['family'].strip())
                        for a in article.get('message').get('author')]
                    try:
                        journal = \
                        article.get('message').get('short-container-title')[0]
                    except IndexError:
                        journal = article.get('message').get('container-title')[
                            0]
                    if article.get('message').get('volume'):
                        if len(authorlist) > 1:
                            authorlist[-1] = "and {}".format(authorlist[-1])
                        sauthorlist = ", ".join(authorlist)
                        ref = "{}, {}, {}, v.{}, pp.{}, ({}).".format(
                            article.get('message').get('title')[0],
                            sauthorlist,
                            journal,
                            article.get('message').get('volume'),
                            article.get('message').get('page'),
                            article.get('message').get('issued').get(
                                'date-parts')[
                                0][
                                0],
                        )
                    else:
                        if len(authorlist) > 1:
                            authorlist[-1] = "and {}".format(authorlist[-1])
                        sauthorlist = ", ".join(authorlist)
                        ref = "{}, {}, {}, pp.{}, ({}).".format(
                            article.get('message').get('title')[0],
                            sauthorlist,
                            journal,
                            article.get('message').get('page'),
                            article.get('message').get('issued').get('date-parts')[
                                0][
                                0],
                        )
                    paper.update({'reference': ref, 'n': n, 'label': 'DOI'})
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


"""            self.render(
                "rlist_word.docx",
                outfile_bib + ".docx",
                rlist=rlist,
            )
"""
