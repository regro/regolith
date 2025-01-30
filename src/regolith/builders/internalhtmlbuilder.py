"""Builder for websites."""

import datetime as dt
import os
import shutil

from regolith.builders.basebuilder import BuilderBase
from regolith.dates import get_dates
from regolith.fsclient import _id_key
from regolith.sorters import ene_date_key, position_key
from regolith.tools import (
    all_docs_from_collection,
    dereference_institution,
    document_by_value,
    filter_projects,
    filter_publications,
    fuzzy_retrieval,
    get_formatted_crossref_reference,
    make_bibtex_file,
)

PROJ_URL_BASE = "https://gitlab.thebillingegroup.com/talks/"


class InternalHtmlBuilder(BuilderBase):
    """Build HTML files for website."""

    btype = "internalhtml"
    needed_colls = ["people", "meetings"]

    def __init__(self, rc):
        super().__init__(rc)
        # TODO: get this from the RC
        self.cmds = [
            "root_index",
            "meetings",
            "nojekyll",
            "cname",
        ]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        gtx["jobs"] = list(all_docs_from_collection(rc.client, "jobs"))
        gtx["people"] = sorted(
            all_docs_from_collection(rc.client, "people"),
            key=position_key,
            reverse=True,
        )
        gtx["meetings"] = list(all_docs_from_collection(rc.client, "meetings"))
        gtx["group"] = document_by_value(all_docs_from_collection(rc.client, "groups"), "name", rc.groupname)
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["institutions"] = sorted(all_docs_from_collection(rc.client, "institutions"), key=_id_key)

    def finish(self):
        """Move files over to their destination and remove them from the
        source."""
        # static
        stsrc = os.path.join(getattr(self.rc, "static_source", "templates"), "static")
        stdst = os.path.join(self.bldir, "static")
        if os.path.isdir(stdst):
            shutil.rmtree(stdst)
        shutil.copytree(stsrc, stdst)

    def root_index(self):
        """Render root index."""
        self.render("introot_index.html", "intindex.html", title="Home")

    def meetings(self):
        """Render projects."""
        rc = self.rc
        mtgsi = all_docs_from_collection(rc.client, "meetings")

        pp_mtgs, f_mtgs, jclub_cumulative = [], [], []
        for mtg in mtgsi:
            if not mtg.get("lead"):
                print("{} missing a meeting lead".format(mtg["_id"]))
            if not mtg.get("scribe"):
                print("{} missing a meeting scribe".format(mtg["_id"]))
            lead = fuzzy_retrieval(
                all_docs_from_collection(rc.client, "people"), ["_id", "name", "aka"], mtg.get("lead")
            )
            if not lead:
                print("{} lead {} not found in people".format(mtg["_id"], mtg.get("lead")))
            mtg["lead"] = lead["name"]
            scribe = fuzzy_retrieval(
                all_docs_from_collection(rc.client, "people"), ["_id", "name", "aka"], mtg.get("scribe")
            )
            if not scribe:
                print("{} scribe {} not found in people".format(mtg["_id"], mtg.get("scribe")))
            mtg["scribe"] = scribe["name"]
            if mtg.get("journal_club"):
                prsn_id = mtg["journal_club"].get("presenter", "None")
                prsn = fuzzy_retrieval(
                    all_docs_from_collection(rc.client, "people"), ["_id", "name", "aka"], prsn_id
                )
                if not prsn:
                    if prsn_id.lower() not in ["tbd", "hold", "na"]:
                        print(
                            "WARNING: {} presenter {} not found in people".format(
                                mtg["_id"], mtg["presentation"].get("presenter")
                            )
                        )
                    prsn = {"name": prsn_id}
                mtg["journal_club"]["presenter"] = prsn["name"]
                mtg_jc_doi = mtg["journal_club"].get("doi", "tbd")
                mtg_jc_doi_casefold = mtg_jc_doi.casefold()
                if mtg_jc_doi_casefold == "na":
                    mtg["journal_club"]["doi"] = "N/A"
                elif mtg_jc_doi_casefold != "tbd":
                    if not mtg_jc_doi_casefold.startswith("arxiv"):
                        ref, _ = get_formatted_crossref_reference(mtg["journal_club"].get("doi"))
                        mtg["journal_club"]["doi"] = ref
                    else:
                        ref = mtg_jc_doi
                    jclub_cumulative.append((ref, get_dates(mtg).get("date", "no date")))

            if mtg.get("presentation"):
                prsn_id = mtg["presentation"].get("presenter", "None")
                prsn = fuzzy_retrieval(
                    all_docs_from_collection(rc.client, "people"), ["_id", "name", "aka"], prsn_id
                )
                if not prsn:
                    if prsn_id.lower() not in ["tbd", "hold", "na"]:
                        print(
                            "WARNING: {} presenter {} not found in people".format(
                                mtg["_id"], mtg["presentation"].get("presenter")
                            )
                        )
                    prsn = {"name": prsn_id}
                mtg["presentation"]["presenter"] = prsn["name"]
                mtg["presentation"]["link"] = mtg["presentation"].get("link", "tbd")
            mtg["date"] = dt.date(mtg.get("year"), mtg.get("month"), mtg.get("day"))
            mtg["datestr"] = mtg["date"].strftime("%m/%d/%Y")
            today = dt.date.today()
            if mtg["date"] >= today:
                f_mtgs.append(mtg)
            else:
                pp_mtgs.append(mtg)

        jclub_cumulative = sorted(jclub_cumulative, key=lambda x: x[1], reverse=True)
        pp_mtgs = sorted(pp_mtgs, key=lambda x: x.get("date"), reverse=True)
        f_mtgs = sorted(f_mtgs, key=lambda x: x.get("date"))
        self.render(
            "grpmeetings.html",
            "grpmeetings.html",
            title="Group Meetings",
            ppmeetings=pp_mtgs,
            fmeetings=f_mtgs,
            jclublist=jclub_cumulative,
        )

    def nojekyll(self):
        """Touches a nojekyll file in the build dir."""
        with open(os.path.join(self.bldir, ".nojekyll"), "a+"):
            pass

    def cname(self):
        """Add CNAME."""
        rc = self.rc
        if not hasattr(rc, "cname"):
            return
        with open(os.path.join(self.bldir, "CNAME"), "w", encoding="utf-8") as f:
            f.write(rc.cname)

    def people(self):
        """Render people, former members, and each person."""
        rc = self.rc
        peeps_dir = os.path.join(self.bldir, "people")
        former_peeps_dir = os.path.join(self.bldir, "former")
        os.makedirs(peeps_dir, exist_ok=True)
        os.makedirs(former_peeps_dir, exist_ok=True)
        peeps = self.gtx["people"]
        for p in peeps:
            names = frozenset(p.get("aka", []) + [p["name"]])
            pubs = filter_publications(
                all_docs_from_collection(rc.client, "citations"),
                names,
                reverse=True,
                bold=False,
            )

            bibfile = make_bibtex_file(pubs, pid=p["_id"], person_dir=peeps_dir)
            ene = p.get("employment", []) + p.get("education", [])
            ene.sort(key=ene_date_key, reverse=True)
            for e in ene:
                dereference_institution(e, self.gtx["institutions"])
            projs = filter_projects(all_docs_from_collection(rc.client, "projects"), names)
            self.render(
                "person.html",
                os.path.join("people", p["_id"] + ".html"),
                p=p,
                title=p.get("name", ""),
                pubs=pubs,
                names=names,
                bibfile=bibfile,
                education_and_employment=ene,
                projects=projs,
            )
        self.render("people.html", os.path.join("people", "index.html"), title="People")

        self.render(
            "former.html",
            os.path.join("former", "index.html"),
            title="Former Members",
        )

    def projects(self):
        """Render projects."""
        rc = self.rc
        projs = all_docs_from_collection(rc.client, "projects")
        self.render("projects.html", "projects.html", title="Projects", projects=projs)

    def blog(self):
        """Render the blog and rss."""
        rc = self.rc
        blog_dir = os.path.join(self.bldir, "blog")
        os.makedirs(blog_dir, exist_ok=True)
        posts = list(all_docs_from_collection(rc.client, "blog"))
        posts.sort(key=ene_date_key, reverse=True)
        for post in posts:
            self.render(
                "blog_post.html",
                os.path.join("blog", post["_id"] + ".html"),
                post=post,
                title=post["title"],
            )
        self.render(
            "blog_index.html",
            os.path.join("blog", "index.html"),
            title="Blog",
            posts=posts,
        )
        self.render("rss.xml", os.path.join("blog", "rss.xml"), items=posts)

    def jobs(self):
        """Render the jobs and each job."""
        jobs_dir = os.path.join(self.bldir, "jobs")
        os.makedirs(jobs_dir, exist_ok=True)
        for job in self.gtx["jobs"]:
            self.render(
                "job.html",
                os.path.join("jobs", job["_id"] + ".html"),
                job=job,
                title="{0} ({1})".format(job["title"], job["_id"]),
            )
        self.render("jobs.html", os.path.join("jobs", "index.html"), title="Jobs")

    def abstracts(self):
        """Render each abstract."""
        abs_dir = os.path.join(self.bldir, "abstracts")
        os.makedirs(abs_dir, exist_ok=True)
        for ab in self.gtx["abstracts"]:
            self.render(
                "abstract.html",
                os.path.join("abstracts", ab["_id"] + ".html"),
                abstract=ab,
                title="{0} {1} - {2}".format(ab["firstname"], ab["lastname"], ab["title"]),
            )
