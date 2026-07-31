"""Builder for presentations.

A talk in the talks collection is assembled from decks of slides in the
slides collection.  A presentation in the presentations collection is
one occasion on which a talk was given, and points at its talk with
talk_id. This builder renders a beamer document for every presentation
that names a talk.
"""

import ast

from regolith.builders.basebuilder import LatexBuilderBase
from regolith.tools import all_docs_from_collection, get_person_contact


def string_to_slice(slice_str):
    """Return the slice described by a string such as "[2:5]".

    Parameters
    ----------
    slice_str: str
        The slice written in python syntax, with or without the enclosing
        brackets.  An omitted start, stop or step is taken as None

    Returns
    -------
    selection: slice
        The slice the string describes
    """
    parts = slice_str.strip("[]").split(":")
    start = int(parts[0]) if parts[0] else None
    stop = int(parts[1]) if parts[1] else None
    step = int(parts[2]) if len(parts) > 2 and parts[2] else None
    return slice(start, stop, step)


def select_slides(deck, slide_list, topic):
    """Return the slides a topic selects from a deck.

    Parameters
    ----------
    deck: dict
        The document from the slides collection
    slide_list: str
        The selection written in python indexing syntax, either a slice such
        as "[:]" or "[2:5]", or a list of indices such as "[1,4,7]"
    topic: str
        The id of the deck, used in the error message

    Returns
    -------
    slides: list of dicts
        The selected slides, in the order they are selected

    Raises
    ------
    ValueError
        If the selection cannot be read, or selects a slide the deck does not
        have
    """
    slides = deck.get("slides") or []
    try:
        if ":" in slide_list:
            return slides[string_to_slice(slide_list)]
        return [slides[index] for index in ast.literal_eval(slide_list)]
    except (IndexError, SyntaxError, TypeError, ValueError):
        raise ValueError(
            f"The slide_list '{slide_list}' of topic '{topic}' could not be applied to that deck, "
            f"which has {len(slides)} slides. Please write the slide_list as a slice, such as "
            '"[:]" or "[2:5]", or as a list of indices, such as "[1,4,7]", that the deck has.'
        )


class PresentationBuilder(LatexBuilderBase):
    """Build a beamer document for each presentation that names a talk.

    The slides are gathered from the decks the talk lists under its
    topics, and written to one tex file per presentation.

    Methods
    -------
    construct_global_ctx()
        Constructs the global context.
    latex()
        Render latex template.
    """

    btype = "presentation"
    needed_colls = ["presentations", "talks", "slides", "people", "contacts"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        # Listed, not left as the generator all_docs_from_collection returns, because each
        # collection is scanned once per topic and a generator yields nothing the second time
        for coll in self.needed_colls:
            gtx[coll] = list(all_docs_from_collection(rc.client, coll))

    def _get_deck(self, topic):
        """Return the deck of slides with the given id."""
        for deck in self.gtx["slides"]:
            if deck.get("_id") == topic:
                return deck
        raise ValueError(
            f"The topic '{topic}' was not found in the slides collection. Please add a deck with "
            f"that id, or correct the topic in the talk that asks for it."
        )

    def _gather_topics(self, talk):
        """Return the sections of a talk, each holding its selected
        slides.

        A section is either a topic taken straight from one deck, or a
        supertopic gathering slides from several decks under one
        heading.
        """
        topics = []
        for entry in talk.get("topics") or []:
            if "supertopic" in entry:
                slides = []
                for subtopic in entry.get("topics") or []:
                    topic = subtopic.get("topic")
                    deck = self._get_deck(topic)
                    slides.extend(select_slides(deck, subtopic.get("slide_list"), topic))
                topics.append({"name": entry.get("supertopic"), "slides": slides})
            else:
                topic = entry.get("topic")
                deck = self._get_deck(topic)
                # A new dict, so that the deck in the slides collection is left alone
                topics.append(
                    {
                        "name": deck.get("name"),
                        "slides": select_slides(deck, entry.get("slide_list"), topic),
                    }
                )
        return topics

    def _get_talk(self, presentation):
        """Return the talk a presentation names."""
        talk_id = presentation.get("talk_id")
        for talk in self.gtx["talks"]:
            if talk.get("_id") == talk_id:
                return talk
        raise ValueError(
            f"The talk '{talk_id}', named by presentation '{presentation.get('_id')}', was not "
            f"found in the talks collection. Please add a talk with that id, or correct the "
            f"talk_id of the presentation."
        )

    def _get_presenter_name(self, presentation, talk):
        """Return the name of the person giving the presentation."""
        presenter = presentation.get("presenter") or talk.get("presenter")
        if not presenter:
            return ""
        person = get_person_contact(presenter, self.gtx["people"], self.gtx["contacts"])
        if person is None:
            # The presenter is not in the collections, so their name is all we know
            return presenter
        return person.get("name") or presenter

    def latex(self):
        """Render latex template."""
        for presentation in self.gtx["presentations"]:
            if not presentation.get("talk_id"):
                continue
            talk = self._get_talk(presentation)
            general = {
                "title": presentation.get("title") or "",
                "subtitle": presentation.get("subtitle") or "",
                "presenter": self._get_presenter_name(presentation, talk),
            }
            presentation_id = presentation.get("_id")
            self.render(
                "talk.tex",
                f"{presentation_id}.tex",
                general=general,
                topics=self._gather_topics(talk),
            )
            self.pdf(presentation_id)
