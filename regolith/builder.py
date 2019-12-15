"""Generic builder."""

from regolith.builders.cvbuilder import CVBuilder
from regolith.builders.htmlbuilder import HtmlBuilder
from regolith.builders.postdocadbuilder import PostdocadBuilder
from regolith.builders.preslistbuilder import PresListBuilder
from regolith.builders.publistbuilder import PubListBuilder
from regolith.builders.gradebuilder import GradeReportBuilder
from regolith.builders.manuscriptreviewbuilder import ManRevBuilder
from regolith.builders.proposalreviewbuilder import PropRevBuilder
from regolith.builders.reimbursementbuilder import ReimbursementBuilder
from regolith.builders.resumebuilder import ResumeBuilder
from regolith.builders.cpbuilder import CPBuilder
from regolith.builders.figurebuilder import FigureBuilder
from regolith.builders.readinglistsbuilder import ReadingListsBuilder


BUILDERS = {
    "cv": CVBuilder,
    "html": HtmlBuilder,
    "publist": PubListBuilder,
    "grade": GradeReportBuilder,
    "grades": GradeReportBuilder,
    "resume": ResumeBuilder,
    "current-pending": CPBuilder,
    "postdocad": PostdocadBuilder,
    "review-man": ManRevBuilder,
    "review-prop": PropRevBuilder,
    "preslist": PresListBuilder,
    "reimb": ReimbursementBuilder,
    "figure": FigureBuilder,
    "reading_lists": ReadingListsBuilder,
}


def builder(btype, rc):
    """Returns builder of the appropriate type."""
    return BUILDERS[btype](rc)
