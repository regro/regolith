"""Builder for Grade Reports."""
import os
import shutil
import subprocess
from glob import glob
from itertools import groupby

from jinja2 import Environment, FileSystemLoader
try:
    from bibtexparser.bwriter import BibTexWriter
    from bibtexparser.bibdatabase import BibDatabase
    HAVE_BIBTEX_PARSER = True
except ImportError:
    HAVE_BIBTEX_PARSER = False

try:
    import numpy as np
except ImportError:
    np = None

from regolith.tools import all_docs_from_collection, date_to_float, \
    date_to_rfc822, rfc822now, gets, month_and_year
from regolith.sorters import doc_date_key, ene_date_key, category_val, \
    level_val, id_key, date_key, position_key

LATEX_OPTS = ['-halt-on-error', '-file-line-error']

def latex_safe(s):
    return s.replace('&', '\&').replace('$', '\$').replace('#', '\#')


class GradeReportBuilder(object):

    btype = 'grades'

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
        gtx['sum'] = sum
        gtx['zip'] = zip
        gtx['True'] = True
        gtx['False'] = False
        gtx['None'] = None
        gtx['sorted'] = sorted
        gtx['groupby'] = groupby
        gtx['range'] = range
        gtx['gets'] = gets
        gtx['date_key'] = date_key
        gtx['doc_date_key'] = doc_date_key
        gtx['level_val'] = level_val
        gtx['category_val'] = category_val
        gtx['rfc822now'] = rfc822now
        gtx['date_to_rfc822'] = date_to_rfc822
        gtx['month_and_year'] = month_and_year
        gtx['latex_safe'] = latex_safe
        gtx['all_docs_from_collection'] = all_docs_from_collection
        gtx['grades'] = list(all_docs_from_collection(rc.client, 'grades'))
        gtx['courses'] = list(all_docs_from_collection(rc.client, 'courses'))
        gtx['assignments'] = list(all_docs_from_collection(rc.client,
                                                           'assignments'))

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
        os.makedirs(self.bldir, exist_ok=True)
        self.latex()
        self.clean()

    def latex(self):
        rc = self.rc
        for course in self.gtx['courses']:
            course_id = course['_id']
            stats = self.makestats(course)
            asgn = filter((lambda x: course_id in x['courses']),
                          self.gtx['assignments'])
            catfunc = lambda x: x['category']
            asgn = sorted(asgn, key=catfunc)
            grouped_assignments = {k: list(i) for k, i in groupby(asgn, catfunc)}

            student_wavgs = []
            students_kwargs = {}
            for student_id in course['students']:
                student_grade_list = list(filter(
                    (lambda x: (x['student'] == student_id and
                               x['course'] == course_id)), self.gtx['grades']))
                student_grades = {k: [] for k in grouped_assignments.keys()}
                for category, asngs in grouped_assignments.items():
                    for asgn in asngs:
                        for sg in student_grade_list:
                            if sg['assignment'] == asgn['_id']:
                                student_grades[category].append(sg)
                                break
                        else:
                            student_grades[category].append(None)
                student_totals, student_wavg = self.maketotals(student_grades,
                                                               grouped_assignments,
                                                               course)
                student_wavgs.append(student_wavg)
                students_kwargs[student_id] = dict(
                    title=student_id, stats=stats,
                    student_id=student_id, course_id=course_id,
                    grouped_assignments=grouped_assignments,
                    student_grades=student_grades,
                    student_totals=student_totals,
                    student_wavg=student_wavg
                    )
            max_wavg = max(student_wavgs)
            curve = 1.0 - max_wavg
            for student_id in course['students']:
                base = self.basename(student_id, course_id)
                self.render('gradereport.tex', base + '.tex', p=student_id,
                            max_wavg=max_wavg, curve=curve,
                            **students_kwargs[student_id])
                self.pdf(base)

    def pdf(self, base):
        """Compiles latex files to PDF"""
        self.run(['latex'] + LATEX_OPTS + [base + '.tex'])
        self.run(['dvipdf', base])

    def run(self, cmd):
        subprocess.run(cmd, cwd=self.bldir, check=True)

    def clean(self):
        postfixes = ['*.dvi', '*.toc', '*.aux', '*.out', '*.log', '*.bbl',
                     '*.blg', '*.log', '*.spl', '*~', '*.spl', '*.run.xml',
                     '*-blx.bib']
        to_rm = []
        for pst in postfixes:
            to_rm += glob(os.path.join(self.bldir, pst))
        for f in set(to_rm):
            os.remove(f)

    def makestats(self, course):
        """Returns a dictionary of statistics for a course whose keys are
        the assignments and whose values are a (mean-problem, std-problem,
        mean-total, std-total) tuple.
        """
        scores = {}
        course_id = course['_id']
        for grade in self.gtx['grades']:
            if grade['course'] != course_id:
                 continue
            assignment_id = grade['assignment']
            if assignment_id not in scores:
                scores[assignment_id] = []
            scores[assignment_id].append(grade['scores'])
        stats = {}
        for assignment_id, data in scores.items():
            stats[assignment_id] = (np.mean(data, axis=0),
                                    np.std(data, axis=0),
                                    np.mean(np.sum(data, axis=1)),
                                    np.std(np.sum(data, axis=1)))
        # handle stats for ungraded assignments
        for assignment in self.gtx['assignments']:
            assignment_id = assignment['_id']
            if assignment_id not in stats:
                n = len(assignment['points'])
                z = (0,) * n
                stats[assignment_id] = (z, z, 0, 0)
        return stats

    def basename(self, student_id, course_id):
        """Returns the base file name for a student in a course."""
        name = student_id.replace('.', '').replace(' ', '')
        name += '-' + course_id
        return name

    def maketotals(self, student_grades, grouped_assignments, course):
        """Makes total grades."""
        totals = []
        totalweight = totalfrac = 0.0
        for category in student_grades.keys():
            cat = [category]
            sgtot = catmax = 0
            for sg, asgn in zip(student_grades[category],
                                grouped_assignments[category]):
                if sg is not None:
                    sgtot += sum(sg['scores'])
                catmax += sum(asgn['points'])
            cat.append(sgtot)
            cat.append(catmax)
            weight = course['weights'][category]
            cat.append(weight)
            totalweight += weight
            catfrac = sgtot / catmax
            #cat.append(catfrac)
            wfrac = catfrac * weight
            cat.append(wfrac)
            totalfrac += wfrac
            totals.append(cat)
        wtotal = totalfrac / totalweight
        return sorted(totals), wtotal
