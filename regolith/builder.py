"""Generic builder."""

from regolith.builders.cvbuilder import CVBuilder
from regolith.builders.formalletterbuilder import FormalLetterBuilder
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
from regolith.builders.coabuilder import RecentCollaboratorsBuilder
from regolith.builders.beamplanbuilder import BeamPlanBuilder
from regolith.builders.activitylogbuilder import ActivitylogBuilder
from regolith.builders.internalhtmlbuilder import InternalHtmlBuilder
from regolith.builders.readinglistsbuilder import ReadingListsBuilder
from regolith.builders.grantreportbuilder import GrantReportBuilder


BUILDERS = {
    "annual-activity": ActivitylogBuilder,
    "beamplan": BeamPlanBuilder,
    "current-pending": CPBuilder,
    "cv": CVBuilder,
    "figure": FigureBuilder,
    "formalletter": FormalLetterBuilder,
    "grade": GradeReportBuilder,
    "grades": GradeReportBuilder,
    "grant-report": GrantReportBuilder,
    "html": HtmlBuilder,
    "internalhtml": InternalHtmlBuilder,
    "postdocad": PostdocadBuilder,
    "preslist": PresListBuilder,
    "publist": PubListBuilder,
    "reading-lists": ReadingListsBuilder,
    "reimb": ReimbursementBuilder,
    "recent-collabs": RecentCollaboratorsBuilder,
    "resume": ResumeBuilder,
    "review-man": ManRevBuilder,
    "review-prop": PropRevBuilder
}


def builder(btype, rc):
    """Returns builder of the appropriate type."""
    return BUILDERS[btype](rc)
