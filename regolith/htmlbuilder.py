"""Builder for websites."""
import os
import shutil
from itertools import groupby


from regolith.builder_base import BuilderBase

from regolith.tools import all_docs_from_collection, date_to_rfc822, \
    rfc822now, gets, filter_publications, filter_projects, make_bibtex_file
from regolith.sorters import doc_date_key, ene_date_key, category_val, \
    level_val, id_key, date_key, position_key


class HtmlBuilder(BuilderBase):
    btype = 'html'

    def __init__(self, rc):
        super.__init__(rc)
        # TODO: get this from the RC
        self.cmds = ['root_index', 'people', 'projects', 'blog',
                     'jobs', 'abstracts', 'nojekyll', 'cname', 'finish']

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
        gtx['abstracts'] = list(
            all_docs_from_collection(rc.client, 'abstracts'))
        gtx['all_docs_from_collection'] = all_docs_from_collection

    def finish(self):
        # static
        stsrc = os.path.join('templates', 'static')
        stdst = os.path.join(self.bldir, 'static')
        if os.path.isdir(stdst):
            shutil.rmtree(stdst)
        shutil.copytree(stsrc, stdst)

    def root_index(self):
        self.render('root_index.html', 'index.html', title='Home')

    def people(self):
        rc = self.rc
        peeps_dir = os.path.join(self.bldir, 'people')
        former_peeps_dir = os.path.join(self.bldir, 'former')
        os.makedirs(peeps_dir, exist_ok=True)
        os.makedirs(former_peeps_dir, exist_ok=True)
        for p in self.gtx['people']:
            names = frozenset(p.get('aka', []) + [p['name']])
            pubs = filter_publications(
                all_docs_from_collection(rc.client, 'citations'),
                names, reverse=True, bold=False)
            bibfile = make_bibtex_file(pubs, pid=p['_id'],
                                       person_dir=peeps_dir)
            ene = p.get('employment', []) + p.get('education', [])
            ene.sort(key=ene_date_key, reverse=True)
            projs = filter_projects(
                all_docs_from_collection(rc.client, 'projects'), names)
            self.render('person.html',
                        os.path.join('people', p['_id'] + '.html'), p=p,
                        title=p.get('name', ''), pubs=pubs, names=names,
                        bibfile=bibfile,
                        education_and_employment=ene, projects=projs)
        self.render('people.html', os.path.join('people', 'index.html'),
                    title='People')

        self.render('former.html', os.path.join('former', 'index.html'),
                    title='Former Members')

    def projects(self):
        rc = self.rc
        projs = all_docs_from_collection(rc.client, 'projects')
        self.render('projects.html', 'projects.html', title='Projects',
                    projects=projs)

    def blog(self):
        rc = self.rc
        blog_dir = os.path.join(self.bldir, 'blog')
        os.makedirs(blog_dir, exist_ok=True)
        posts = list(all_docs_from_collection(rc.client, 'blog'))
        posts.sort(key=ene_date_key, reverse=True)
        for post in posts:
            self.render('blog_post.html',
                        os.path.join('blog', post['_id'] + '.html'),
                        post=post, title=post['title'])
        self.render('blog_index.html', os.path.join('blog', 'index.html'),
                    title='Blog',
                    posts=posts)
        self.render('rss.xml', os.path.join('blog', 'rss.xml'), items=posts)

    def jobs(self):
        jobs_dir = os.path.join(self.bldir, 'jobs')
        os.makedirs(jobs_dir, exist_ok=True)
        for job in self.gtx['jobs']:
            self.render('job.html', os.path.join('jobs', job['_id'] + '.html'),
                        job=job,
                        title='{0} ({1})'.format(job['title'], job['_id']))
        self.render('jobs.html', os.path.join('jobs', 'index.html'),
                    title='Jobs')

    def abstracts(self):
        abs_dir = os.path.join(self.bldir, 'abstracts')
        os.makedirs(abs_dir, exist_ok=True)
        for ab in self.gtx['abstracts']:
            self.render('abstract.html',
                        os.path.join('abstracts', ab['_id'] + '.html'),
                        abstract=ab,
                        title='{0} {1} - {2}'.format(ab['firstname'],
                                                     ab['lastname'],
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
