"""Generic builder."""

from regolith.lazy import LazyRegistry

# The import path of each builder rather than the builder itself, so that
# a build imports only the target it was asked for.  Importing all of them
# costs about half a second and pulls in pandas, matplotlib and pypdf.
BUILDERS = LazyRegistry(
    {
        "annual-activity": "regolith.builders.activitylogbuilder:ActivitylogBuilder",
        "beamplan": "regolith.builders.beamplanbuilder:BeamPlanBuilder",
        "current-pending": "regolith.builders.cpbuilder:CPBuilder",
        "cv": "regolith.builders.cvbuilder:CVBuilder",
        "figure": "regolith.builders.figurebuilder:FigureBuilder",
        "formalletter": "regolith.builders.formalletterbuilder:FormalLetterBuilder",
        "grade": "regolith.builders.gradebuilder:GradeReportBuilder",
        "grades": "regolith.builders.gradebuilder:GradeReportBuilder",
        "grant-report": "regolith.builders.grantreportbuilder:GrantReportBuilder",
        "html": "regolith.builders.htmlbuilder:HtmlBuilder",
        "internalhtml": "regolith.builders.internalhtmlbuilder:InternalHtmlBuilder",
        "meals-log": "regolith.builders.mealslogbuilder:MealsLogBuilder",
        "postdocad": "regolith.builders.postdocadbuilder:PostdocadBuilder",
        "presentation": "regolith.builders.presentationbuilder:PresentationBuilder",
        "preslist": "regolith.builders.preslistbuilder:PresListBuilder",
        "publist": "regolith.builders.publistbuilder:PubListBuilder",
        "releaselist": "regolith.builders.releaselistbuilder:ReleaseListBuilder",
        "reading-lists": "regolith.builders.readinglistsbuilder:ReadingListsBuilder",
        "reimb": "regolith.builders.reimbursementbuilder:ReimbursementBuilder",
        "recent-collabs": "regolith.builders.coabuilder:RecentCollaboratorsBuilder",
        "resume": "regolith.builders.resumebuilder:ResumeBuilder",
        "review-man": "regolith.builders.manuscriptreviewbuilder:ManRevBuilder",
        "review-prop": "regolith.builders.proposalreviewbuilder:PropRevBuilder",
    }
)


def builder(btype, rc):
    """Returns builder of the appropriate type."""
    return BUILDERS[btype](rc)
