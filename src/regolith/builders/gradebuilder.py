"""Builder for Grade Reports."""

import os
import pdb
import sys
import traceback
from itertools import groupby

import numpy as np

try:
    import scipy.stats as st
except ImportError:
    st = None

from regolith.builders.basebuilder import LatexBuilderBase
from regolith.tools import all_docs_from_collection


class GradeReportBuilder(LatexBuilderBase):
    btype = "grades"
    needed_colls = ["grades", "courses", "assignments"]

    def construct_global_ctx(self):
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        gtx["sum"] = sum
        gtx["zip"] = zip
        gtx["range"] = range
        gtx["id_key"] = lambda x: x["_id"]
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["grades"] = list(all_docs_from_collection(rc.client, "grades"))
        gtx["courses"] = list(all_docs_from_collection(rc.client, "courses"))
        gtx["assignments"] = list(all_docs_from_collection(rc.client, "assignments"))

    def render(self, tname, fname, **kwargs):
        template = self.env.get_template(tname)
        ctx = dict(self.gtx)
        ctx.update(kwargs)
        ctx["rc"] = ctx.get("rc", self.rc)
        ctx["static"] = ctx.get("static", os.path.relpath("static", os.path.dirname(fname)))
        ctx["root"] = ctx.get("root", os.path.relpath("/", os.path.dirname(fname)))
        try:
            result = template.render(ctx)
        except Exception:
            type, value, tb = sys.exc_info()
            traceback.print_exc()
            pdb.post_mortem(tb)
        with open(os.path.join(self.bldir, fname), "wt", encoding="utf-8") as f:
            f.write(result)

    def latex(self):
        for course in self.gtx["courses"]:
            if not course.get("active", True):
                continue
            course_id = course["_id"]
            stats = self.makestats(course)
            asgn = filter((lambda x: course_id in x["courses"]), self.gtx["assignments"])
            asgn = sorted(asgn, key=lambda x: x["category"])
            grouped_assignments = {
                k: sorted(i, key=lambda x: x["_id"]) for k, i in groupby(asgn, key=lambda x: x["category"])
            }

            student_wavgs = []
            students_kwargs = {}
            studs = []
            for student_id in course["students"]:
                studs.append(student_id)
                student_grade_list = list(
                    filter(
                        (lambda x: (x["student"] == student_id and x["course"] == course_id)),
                        self.gtx["grades"],
                    )
                )
                student_grades = {k: [] for k in grouped_assignments.keys()}
                for category, asngs in grouped_assignments.items():
                    for asgn in asngs:
                        for sg in student_grade_list:
                            if sg["assignment"] == asgn["_id"]:
                                student_grades[category].append(sg)
                                break
                        else:
                            student_grades[category].append(None)
                student_totals, student_wavg = self.maketotals(student_grades, grouped_assignments, course)
                student_wavgs.append(student_wavg)
                students_kwargs[student_id] = dict(
                    title=student_id,
                    stats=stats,
                    student_id=student_id,
                    course_id=course_id,
                    grouped_assignments=grouped_assignments,
                    student_grades=student_grades,
                    student_totals=student_totals,
                    student_wavg=student_wavg,
                )
            ordered_studs = sorted(studs, key=lambda x: (students_kwargs[x]["student_wavg"]), reverse=True)
            max_wavg = max(student_wavgs)
            curve = 1.0 - max_wavg
            # Make grades
            scale = course.get("scale", DEFAULT_LETTER_SCALE)
            for student_id in course["students"]:
                skw = students_kwargs[student_id]
                skw["student_letter_grade_raw"] = find_letter_grade(skw["student_wavg"], scale)
                skw["student_letter_grade_curved"] = find_letter_grade(skw["student_wavg"] + curve, scale)
            summary = [
                "{}: {:.2f}, Grade: {}".format(
                    stud,
                    students_kwargs[stud]["student_wavg"] * 100.0,
                    students_kwargs[stud]["student_letter_grade_raw"],
                )
                for stud in ordered_studs
            ]
            for stud in summary:
                print(stud)
            show_letter_plot = self.plot_letter_grades(students_kwargs, scale)
            # render PDF
            for student_id in course["students"]:
                base = self.basename(student_id, course_id)
                self.render(
                    "gradereport.tex",
                    base + ".tex",
                    p=student_id,
                    max_wavg=max_wavg,
                    curve=curve,
                    show_letter_plot=show_letter_plot,
                    **students_kwargs[student_id],
                )
                # TODO: this seems like something for the base class to handle
                self.pdf(base)

    def makestats(self, course):
        """Returns a dictionary of statistics for a course whose keys
        are the assignments and whose values are a (mean-problem, std-
        problem, mean- total, std-total) tuple."""
        scores = {}
        course_id = course["_id"]
        for grade in self.gtx["grades"]:
            if grade["course"] != course_id:
                continue
            assignment_id = grade["assignment"]
            if assignment_id not in scores:
                scores[assignment_id] = []
            scores[assignment_id].append(grade["scores"])
        stats = {}
        for assignment_id, data in scores.items():
            mu = np.mean(data, axis=0)
            sig = np.std(data, axis=0)
            max_score = np.max(data, axis=0)
            norm = st.norm(mu, sig)
            percent_above_60 = 1.0 - norm.cdf(0.6 * max_score)
            percent_above_80 = 1.0 - norm.cdf(0.8 * max_score)
            total = np.sum(data, axis=1)
            total_mu = np.mean(total, axis=0)
            total_sig = np.std(total, axis=0)
            total_max_score = np.max(total, axis=0)
            total_norm = st.norm(total_mu, total_sig)
            total_percent_above_60 = 1.0 - total_norm.cdf(0.6 * total_max_score)
            total_percent_above_80 = 1.0 - total_norm.cdf(0.8 * total_max_score)
            stats[assignment_id] = (
                mu,
                sig,
                max_score,
                percent_above_60,
                percent_above_80,
                total_mu,
                total_sig,
                total_max_score,
                total_percent_above_60,
                total_percent_above_80,
            )
        # handle stats for ungraded assignments
        for assignment in self.gtx["assignments"]:
            assignment_id = assignment["_id"]
            if assignment_id not in stats:
                n = len(assignment["points"])
                z = (0,) * n
                stats[assignment_id] = (z, z, z, z, z, 0, 0, 0, 0, 0)
        return stats

    @staticmethod
    def basename(student_id, course_id):
        """Returns the base file name for a student in a course."""
        name = student_id.replace(".", "").replace(" ", "")
        name += "-" + course_id
        return name

    def maketotals(self, student_grades, grouped_assignments, course):
        """Makes total grades."""
        totals = []
        totalweight = totalfrac = 0.0
        for category in student_grades.keys():
            cat = [category]
            sgtot = catmax = 0
            for sg, asgn in zip(student_grades[category], grouped_assignments[category]):
                if sg is not None:
                    sgtot += sum(sg["scores"])
                catmax += sum(asgn["points"])
            cat.append(sgtot)
            cat.append(catmax)
            weight = course["weights"][category]
            cat.append(weight)
            totalweight += weight
            catfrac = sgtot / catmax
            # cat.append(catfrac)
            wfrac = catfrac * weight
            cat.append(wfrac)
            totalfrac += wfrac
            totals.append(cat)
        wtotal = 0.0 if not totalweight else totalfrac / totalweight
        return sorted(totals), wtotal

    def plot_letter_grades(self, students_kwargs, scale):
        """Plots the letter grades in a histogram."""
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            return False
        bins = [x[1] for x in scale[::-1]]
        raws = []
        curveds = []
        for skw in students_kwargs.values():
            raws.append(skw["student_letter_grade_raw"])
            curveds.append(skw["student_letter_grade_curved"])
        rfreq = [raws.count(letter) for letter in bins]
        cfreq = [curveds.count(letter) for letter in bins]
        width = 1.0
        pos = np.arange(len(bins))
        f, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
        ax1.set_xticks(pos + (width / 2))
        ax1.set_xticklabels(bins)
        ax1.set_xlabel("Raw Grade")
        ax1.set_ylabel("Number of Students")
        ax1.bar(pos, rfreq, width, color="yellow")
        ax1.grid(True)
        ax2.set_xticks(pos + (width / 2))
        ax2.set_xticklabels(bins)
        ax2.set_xlabel("Curved Grade")
        ax2.bar(pos, cfreq, width, color="green")
        ax2.grid(True)
        base = os.path.join(self.bldir, "student-letter-grade-dist")
        plt.savefig(base + ".png", bbox_inches="tight")
        plt.savefig(base + ".eps", bbox_inches="tight")
        return True


DEFAULT_LETTER_SCALE = (
    (0.97, "A+"),
    (0.93, "A"),
    (0.90, "A-"),
    (0.87, "B+"),
    (0.83, "B"),
    (0.80, "B-"),
    (0.77, "C+"),
    (0.73, "C"),
    (0.70, "C-"),
    (0.67, "D+"),
    (0.63, "D"),
    (0.60, "D-"),
    (-1.0, "F"),
)


def find_letter_grade(score, scale=DEFAULT_LETTER_SCALE):
    """Finds the letter grade from a score and a value."""
    for lower, letter in scale:
        if lower <= score:
            return letter
    return letter
