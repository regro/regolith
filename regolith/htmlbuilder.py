"""Builder for websites."""
import os
import shutil
from copy import deepcopy
from itertools import groupby

from jinja2 import Environment, FileSystemLoader
try:
    from bibtexparser.bwriter import BibTexWriter
    from bibtexparser.bibdatabase import BibDatabase
    HAVE_BIBTEX_PARSER = True
except ImportError:
    HAVE_BIBTEX_PARSER = False

from regolith.tools import all_docs_from_collection, date_to_float, date_to_rfc822, \
    rfc822now, gets
from regolith.sorters import doc_date_key, ene_date_key, category_val, \
    level_val, id_key, date_key, position_key


class HtmlBuilder(object):

    btype = 'html'

    def __init__(self, rc):
        self.rc = rc
        self.bldir = os.path.join(rc.builddir, self.btype)
        self.env = Environment(loader=FileSystemLoader([
                    'templates',
                    os.path.join(os.path.dirname(__file__), 'templates'),
                    ]))
        self.construct_global_ctx()
        if HAVE_BIBTEX_PARSER:
            self.bibdb = BibDatabase()
            self.bibwriter = BibTexWriter()

    def construct_global_ctx(self):
        self.gtx = gtx = {}
        rc = self.rc
        gtx['len'] = len
        gtx['True'] = True
        gtx['False'] = False
        gtx['None'] = None
        gtx['sorted'] = sorted
        gtx['groupby'] = groupby
        gtx['gets'] = gets
        gtx['date_key'] = date_key
        gtx['doc_date_key'] = doc_date_key
        gtx['level_val'] = level_val
        gtx['category_val'] = category_val
        gtx['rfc822now'] = rfc822now
        gtx['date_to_rfc822'] = date_to_rfc822
        gtx['jobs'] = list(all_docs_from_collection(rc.client, 'jobs'))
        gtx['people'] = sorted(all_docs_from_collection(rc.client, 'people'),
                               key=position_key, reverse=True)
        gtx['abstracts'] = list(all_docs_from_collection(rc.client, 'abstracts'))
        gtx['all_docs_from_collection'] = all_docs_from_collection

    def render(self, tname, fname, **kwargs):
        template = self.env.get_template(tname)
        ctx = dict(self.gtx)
        ctx.update(kwargs)
        ctx['rc'] = ctx.get('rc', self.rc)
        ctx['static'] = ctx.get('static',
                               os.path.relpath('static', os.path.dirname(fname)))
        ctx['root'] = ctx.get('root', os.path.relpath('/', os.path.dirname(fname)))
        result = template.render(ctx)
        with open(os.path.join(self.bldir, fname), 'wt') as f:
            f.write(result)

    def build(self):
        rc = self.rc
        os.makedirs(self.bldir, exist_ok=True)
        self.root_index()
        self.people()
        self.projects()
        self.blog()
        self.jobs()
        self.abstracts()
        self.nojekyll()
        self.cname()
        # static
        stsrc = os.path.join('templates', 'static')
        stdst = os.path.join(self.bldir, 'static')
        if os.path.isdir(stdst):
            shutil.rmtree(stdst)
        shutil.copytree(stsrc, stdst)

    def root_index(self):
        rc = self.rc
        self.render('root_index.html', 'index.html', title='Home')

    def people(self):
        rc = self.rc
        peeps_dir = os.path.join(self.bldir, 'people')
        os.makedirs(peeps_dir, exist_ok=True)
        for p in self.gtx['people']:
            names = frozenset(p.get('aka', []) + [p['name']])
            pubs = self.filter_publications(names, reverse=True)
            bibfile = self.make_bibtex_file(pubs, pid=p['_id'],
                                            person_dir=peeps_dir)
            ene = p.get('employment', []) + p.get('education', [])
            ene.sort(key=ene_date_key, reverse=True)
            projs = self.filter_projects(names)
            self.render('person.html',
                        os.path.join('people', p['_id'] + '.html'), p=p,
                        title=p.get('name', ''), pubs=pubs, names=names,
                        bibfile=bibfile,
                        education_and_employment=ene, projects=projs)
        self.render('people.html', os.path.join('people', 'index.html'),
                    title='People')

    def filter_publications(self, authors, reverse=False):
        rc = self.rc
        pubs = []
        for pub in all_docs_from_collection(rc.client, 'citations'):
            s = set(pub.get('author', []))
            # XXX: If editor but not author, but breaks multiple places
            # s |= set(pub.get('editor', []))
            if len(s & authors) == 0:
                continue
            pubs.append(deepcopy(pub))
        pubs.sort(key=doc_date_key, reverse=reverse)
        return pubs

    def make_bibtex_file(self, pubs, pid, person_dir='.'):
        if not HAVE_BIBTEX_PARSER:
            return None
        self.bibdb.entries = ents = []
        for pub in pubs:
            ent = dict(pub)
            ent['ID'] = ent.pop('_id')
            ent['ENTRYTYPE'] = ent.pop('entrytype')
            for n in ['author', 'editor']:
                if n in ent:
                    ent[n] = ' and '.join(ent[n])
            ents.append(ent)
        fname = os.path.join(person_dir, pid) + '.bib'
        with open(fname, 'w') as f:
            f.write(self.bibwriter.write(self.bibdb))
        return fname

    def filter_projects(self, authors, reverse=False):
        rc = self.rc
        projs = []
        for proj in all_docs_from_collection(rc.client, 'projects'):
            team_names = set(gets(proj['team'], 'name'))
            if len(team_names & authors) == 0:
                continue
            proj = dict(proj)
            proj['team'] = [x for x in proj['team'] if x['name'] in authors]
            projs.append(proj)
        projs.sort(key=id_key, reverse=reverse)
        return projs

    def projects(self):
        rc = self.rc
        projs = all_docs_from_collection(rc.client, 'projects')
        self.render('projects.html', 'projects.html', title='Projects', projects=projs)

    def blog(self):
        rc = self.rc
        blog_dir = os.path.join(self.bldir, 'blog')
        os.makedirs(blog_dir, exist_ok=True)
        posts = list(all_docs_from_collection(rc.client, 'blog'))
        posts.sort(key=ene_date_key, reverse=True)
        for post in posts:
            self.render('blog_post.html', os.path.join('blog', post['_id'] + '.html'),
                post=post, title=post['title'])
        self.render('blog_index.html', os.path.join('blog', 'index.html'), title='Blog',
                    posts=posts)
        self.render('rss.xml', os.path.join('blog', 'rss.xml'), items=posts)

    def jobs(self):
        rc = self.rc
        jobs_dir = os.path.join(self.bldir, 'jobs')
        os.makedirs(jobs_dir, exist_ok=True)
        for job in self.gtx['jobs']:
            self.render('job.html', os.path.join('jobs', job['_id'] + '.html'),
                job=job, title='{0} ({1})'.format(job['title'], job['_id']))
        self.render('jobs.html', os.path.join('jobs', 'index.html'), title='Jobs')

    def abstracts(self):
        rc = self.rc
        abs_dir = os.path.join(self.bldir, 'abstracts')
        os.makedirs(abs_dir, exist_ok=True)
        for ab in self.gtx['abstracts']:
            self.render('abstract.html', os.path.join('abstracts', ab['_id'] + '.html'),
                abstract=ab, title='{0} {1} - {2}'.format(ab['firstname'], ab['lastname'],
                                                          ab['title']))

    def nojekyll(self):
        """Touches a nojekyll file in the build dir"""
        with open(os.path.join(self.bldir, '.nojekyll'), 'a+'):
            pass

    def cname(self):
        rc = self.rc
        if not hasattr(rc, 'cname'):
            return
        with open(os.path.join(self.bldir, 'CNAME'), 'w') as f:
            f.write(rc.cname)
