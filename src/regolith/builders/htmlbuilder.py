"""Builder for websites."""

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
    make_bibtex_file,
)


class HtmlBuilder(BuilderBase):
    """Build HTML files for website."""

    btype = "html"

    def __init__(self, rc):
        super().__init__(rc)
        # TODO: get this from the RC
        self.cmds = [
            "root_index",
            "people",
            "projects",
            "blog",
            "jobs",
            "abstracts",
            "nojekyll",
            "cname",
            "finish",
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
        gtx["abstracts"] = list(all_docs_from_collection(rc.client, "abstracts"))
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
        if os.path.isdir(stsrc):
            shutil.copytree(stsrc, stdst)

    def root_index(self):
        """Render root index."""
        self.render("root_index.html", "index.html", title="Home")
        make_bibtex_file(
            list(all_docs_from_collection(self.rc.client, "citations")),
            pid="group",
            person_dir=self.bldir,
        )

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
            emps = p.get("employment", [])
            emps = [em for em in emps if not em.get("not_in_cv", False)]
            for e in emps:
                e["position"] = e.get("position_full", e.get("position").title())
            ene = emps + p.get("education", [])
            ene.sort(key=ene_date_key, reverse=True)
            for e in ene:
                dereference_institution(e, all_docs_from_collection(rc.client, "institutions"))
            projs = filter_projects(all_docs_from_collection(rc.client, "projects"), names)
            for serve in p.get("service", []):
                serve_dates = get_dates(serve)
                date = serve_dates.get("date")
                if not date:
                    date = serve_dates.get("end_date")
                if not date:
                    date = serve_dates.get("begin_date")
                serve["year"] = date.year
                serve["month"] = date.month
            sns = p.get("service", [])
            sns.sort(key=ene_date_key, reverse=True)
            p["service"] = sns
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
