"""Generic builder."""

from regolith.builders.cvbuilder import CVBuilder
from regolith.builders.htmlbuilder import HtmlBuilder
from regolith.builders.preslistbuilder import PresListBuilder
from regolith.builders.publistbuilder import PubListBuilder
from regolith.builders.gradebuilder import GradeReportBuilder
from regolith.builders.resumebuilder import ResumeBuilder
from regolith.builders.cpbuilder import CPBuilder


BUILDERS = {
    'cv': CVBuilder,
    'html': HtmlBuilder,
    'publist': PubListBuilder,
    'grade': GradeReportBuilder,
    'grades': GradeReportBuilder,
    'resume': ResumeBuilder,
    'current-pending': CPBuilder,
    'preslist': PresListBuilder
    }


def builder(btype, rc):
    """Returns builder of the approriate type."""
    return BUILDERS[btype](rc)
