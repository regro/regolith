"""Generic builder."""

from src.regolith.builders.activitylogbuilder import ActivitylogBuilder
from src.regolith.builders.beamplanbuilder import BeamPlanBuilder
from src.regolith.builders.coabuilder import RecentCollaboratorsBuilder
from src.regolith.builders.cpbuilder import CPBuilder
from src.regolith.builders.cvbuilder import CVBuilder
from src.regolith.builders.figurebuilder import FigureBuilder
from src.regolith.builders.formalletterbuilder import FormalLetterBuilder
from src.regolith.builders.gradebuilder import GradeReportBuilder
from src.regolith.builders.grantreportbuilder import GrantReportBuilder
from src.regolith.builders.htmlbuilder import HtmlBuilder
from src.regolith.builders.internalhtmlbuilder import InternalHtmlBuilder
from src.regolith.builders.manuscriptreviewbuilder import ManRevBuilder
from src.regolith.builders.postdocadbuilder import PostdocadBuilder
from src.regolith.builders.preslistbuilder import PresListBuilder
from src.regolith.builders.proposalreviewbuilder import PropRevBuilder
from src.regolith.builders.publistbuilder import PubListBuilder
from src.regolith.builders.readinglistsbuilder import ReadingListsBuilder
from src.regolith.builders.reimbursementbuilder import ReimbursementBuilder
from src.regolith.builders.resumebuilder import ResumeBuilder

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
    "review-prop": PropRevBuilder,
}


def builder(btype, rc):
    """Returns builder of the appropriate type."""
    return BUILDERS[btype](rc)
