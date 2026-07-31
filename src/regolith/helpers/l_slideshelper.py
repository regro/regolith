"""Lister for decks of slides.

A deck holds slides on a single topic, and talks assemble decks into
sections.  The id of a deck is the name a talk refers to it by, and the
number of slides it holds is what a slide_list indexes into.
"""

from gooey import GooeyParser

from regolith.fsclient import _id_key
from regolith.helpers.basehelper import SoutHelperBase
from regolith.tools import all_docs_from_collection, strip_str

TARGET_COLL = "slides"
HELPER_TARGET = "l_slides"


def subparser(subpi):
    int_kwargs = {}
    if isinstance(subpi, GooeyParser):
        int_kwargs["widget"] = "IntegerField"

    subpi.add_argument(
        "-d",
        "--deck-id",
        help="Filter decks to those whose id contains this fragment.",
        type=strip_str,
    )
    subpi.add_argument(
        "-t",
        "--tag",
        help="Filter decks to those carrying this tag.",
        type=strip_str,
    )
    subpi.add_argument(
        "-i",
        "--title",
        help="Filter decks to those holding a slide whose title contains this fragment.",
        type=strip_str,
    )
    subpi.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show the title and type of every slide, with the index a slide_list would use.",
    )
    return subpi


class SlidesListerHelper(SoutHelperBase):
    """Helper for listing the decks of slides that talks are built
    from."""

    # btype must be the same as helper target in helper.py
    btype = HELPER_TARGET
    needed_colls = [f"{TARGET_COLL}"]

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

    @staticmethod
    def _tags(deck):
        """Return the tags of a deck as a list, however they are
        written."""
        tags = deck.get("tags") or []
        return [tags] if isinstance(tags, str) else tags

    def sout(self):
        rc = self.rc
        decks = self.gtx["slides"]

        if rc.deck_id:
            decks = [deck for deck in decks if rc.deck_id.casefold() in deck.get("_id", "").casefold()]
        if rc.tag:
            decks = [
                deck for deck in decks if any(rc.tag.casefold() in tag.casefold() for tag in self._tags(deck))
            ]
        if rc.title:
            decks = [
                deck
                for deck in decks
                if any(
                    rc.title.casefold() in (slide.get("title") or "").casefold()
                    for slide in (deck.get("slides") or [])
                )
            ]

        if not decks:
            print("No decks of slides were found. Please loosen the filters and try again.")
            return

        for deck in decks:
            slides = deck.get("slides") or []
            name = deck.get("name")
            heading = f"{deck.get('_id')} - ({len(slides)} slides)"
            print(f"{heading} - {name}" if name else heading)
            if rc.verbose:
                for index, slide in enumerate(slides):
                    print(f"    [{index}] {slide.get('type')}: {slide.get('title')}")
        return
