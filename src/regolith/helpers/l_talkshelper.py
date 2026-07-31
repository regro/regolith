"""Lister for talks.

A talk is the reusable content, assembled from decks in the slides
collection, and a presentation is one occasion on which it was given.
The presentations a talk has been given at are shown beside it, so that
the id needed to build one can be found.
"""

from gooey import GooeyParser

from regolith.fsclient import _id_key
from regolith.helpers.basehelper import SoutHelperBase
from regolith.tools import all_docs_from_collection, get_person_contact, strip_str

TARGET_COLL = "talks"
HELPER_TARGET = "l_talks"


def subparser(subpi):
    int_kwargs = {}
    if isinstance(subpi, GooeyParser):
        int_kwargs["widget"] = "IntegerField"
        int_kwargs["gooey_options"] = {"min": 1900, "max": 2100}

    subpi.add_argument(
        "-t",
        "--talk-id",
        help="Filter talks to those whose id contains this fragment.",
        type=strip_str,
    )
    subpi.add_argument(
        "-d",
        "--description",
        help="Filter talks to those whose description contains this fragment.",
        type=strip_str,
    )
    subpi.add_argument(
        "-p",
        "--presenter",
        help="Filter talks to those given by this person, by id or name.",
        type=strip_str,
    )
    subpi.add_argument(
        "-y",
        "--year",
        help="Filter talks to those written in this year.",
        **int_kwargs,
    )
    subpi.add_argument(
        "--all",
        action="store_true",
        help="Show talks that are no longer active, which are left out by default.",
    )
    subpi.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show the description and the topics of each talk.",
    )
    return subpi


class TalksListerHelper(SoutHelperBase):
    """Helper for listing talks and the presentations they were given
    at."""

    # btype must be the same as helper target in helper.py
    btype = HELPER_TARGET
    needed_colls = [f"{TARGET_COLL}", "presentations", "people", "contacts"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        rc.coll = f"{TARGET_COLL}"
        colls = [
            sorted(all_docs_from_collection(rc.client, collname), key=_id_key) for collname in self.needed_colls
        ]
        for db, coll in zip(self.needed_colls, colls):
            gtx[db] = coll
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def _presentations_by_talk(self):
        """Return the ids of the presentations that name each talk.

        A talk may have been given more than once, so every presentation
        that names it is kept rather than only the last one found.
        """
        presentations = {}
        for presentation in self.gtx["presentations"]:
            talk_id = presentation.get("talk_id")
            if talk_id:
                presentations.setdefault(talk_id, []).append(presentation.get("_id"))
        return presentations

    def _presenter_name(self, talk):
        """Return the name of the person who gives a talk."""
        presenter = talk.get("presenter")
        if not presenter:
            return ""
        person = get_person_contact(presenter, self.gtx["people"], self.gtx["contacts"])
        if person is None:
            return presenter
        return person.get("name") or presenter

    def _count_slides(self, talk):
        """Return the number of sections and decks a talk is built
        from."""
        sections = talk.get("topics") or []
        decks = 0
        for section in sections:
            decks += len(section.get("topics") or []) if "supertopic" in section else 1
        return len(sections), decks

    def sout(self):
        rc = self.rc
        talks = self.gtx["talks"]
        presentations = self._presentations_by_talk()

        if not getattr(rc, "all", False):
            talks = [talk for talk in talks if talk.get("active", True)]
        if rc.talk_id:
            talks = [talk for talk in talks if rc.talk_id.casefold() in talk.get("_id", "").casefold()]
        if rc.description:
            talks = [
                talk
                for talk in talks
                if rc.description.casefold() in (talk.get("talk_description") or "").casefold()
            ]
        if rc.presenter:
            talks = [
                talk
                for talk in talks
                if rc.presenter.casefold() in (talk.get("presenter") or "").casefold()
                or rc.presenter.casefold() in self._presenter_name(talk).casefold()
            ]
        if rc.year:
            talks = [talk for talk in talks if talk.get("year") == int(rc.year)]

        if not talks:
            print("No talks were found. Please loosen the filters and try again.")
            return

        for talk in talks:
            given_at = presentations.get(talk.get("_id"))
            given_at = ", ".join(given_at) if given_at else "no presentation"
            print(f"{talk.get('_id')} - ({given_at})")
            if rc.verbose:
                presenter = self._presenter_name(talk)
                if presenter:
                    print(f"    presenter: {presenter}")
                if talk.get("talk_description"):
                    print(f"    description: {talk.get('talk_description')}")
                sections, decks = self._count_slides(talk)
                print(f"    {sections} sections built from {decks} decks")
        return
