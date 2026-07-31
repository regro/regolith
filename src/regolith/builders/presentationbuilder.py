"""Builder for presentations.

A talk in the talks collection is assembled from decks of slides in the
slides collection.  A presentation in the presentations collection is
one occasion on which a talk was given, and points at its talk with
talk_id. This builder renders a beamer document for every presentation
that names a talk.
"""

import ast

from regolith.builders.basebuilder import LatexBuilderBase
from regolith.dates import get_dates
from regolith.tools import (
    all_docs_from_collection,
    format_affiliation,
    fuzzy_retrieval,
    get_person_affiliation,
    get_person_contact,
    string_to_slice,
)


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


def number_affiliations(entries, presenter_name=""):
    """Return authors numbered by the affiliation they share.

    Parameters
    ----------
    entries: list of dicts
        The authors in the order they are to appear, each holding their "name" and their
        "affiliation" as a single line of text.  An empty affiliation is one that could
        not be found
    presenter_name: str
        The name of the author giving the presentation.  Default is an empty string,
        which marks nobody

    Returns
    -------
    authors: list of dicts
        The authors in the order given, each holding their "name", the "number" of their
        affiliation and whether they are the presenter under "is_presenter".  The number
        is None for an author with no affiliation, and for every author when there is
        nothing to tell apart
    affiliations: list of str
        The affiliations in the order they first appear, each listed once.  Two authors
        whose affiliation reads the same share a number, so two departments of one
        institution stay apart while one department shared by two authors is listed once
    """
    authors, affiliations = [], []
    for entry in entries:
        affiliation = entry.get("affiliation") or ""
        if affiliation and affiliation not in affiliations:
            affiliations.append(affiliation)
        authors.append(
            {
                "name": entry.get("name") or "",
                "number": affiliations.index(affiliation) + 1 if affiliation else None,
                "is_presenter": bool(presenter_name) and entry.get("name") == presenter_name,
            }
        )
    # A single affiliation needs no numbering, since every author shares it
    if len(affiliations) < 2:
        for author in authors:
            author["number"] = None
    return authors, affiliations


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
    needed_colls = ["presentations", "talks", "slides", "people", "contacts", "institutions"]

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

    def _resolve_address(self, address):
        """Return an entry of the addresses of a talk as text.

        The entry is either an id in the institutions collection or an
        address already written out.
        """
        institution = fuzzy_retrieval(
            self.gtx["institutions"], ["name", "aka", "_id"], address, case_sensitive=False
        )
        if institution is None:
            return address
        return institution.get("name") or address

    def _get_author(self, author, address, on):
        """Return the name and affiliation of one author of a talk.

        The author is looked for in the people and contacts collections,
        which give their canonical name and the affiliation they held on
        the date of the presentation.  For an author who is not in
        either collection the name is taken as written and the
        affiliation from the addresses of the talk.
        """
        try:
            affiliation = get_person_affiliation(
                author,
                self.gtx["people"],
                self.gtx["contacts"],
                self.gtx["institutions"],
                strict=False,
                now=on,
            )
        except ValueError:
            # Not a person we hold, so the talk itself has to say who they are
            return {"name": author, "affiliation": self._resolve_address(address) if address else ""}
        return {
            "name": affiliation["name"],
            "affiliation": format_affiliation(affiliation, style="short"),
        }

    def _get_authors(self, presentation, talk):
        """Return the authors of a talk and the affiliations they share.

        Authors keep the order the talk lists them in.  Affiliations are
        numbered in the order they first appear, and an affiliation
        shared by several authors is listed once, so that two authors in
        the same department of the same institution carry the same
        number while two departments of one institution stay apart.  The
        author giving the presentation is marked so that the template
        can pick them out.
        """
        authorlist = talk.get("authorlist") or []
        if isinstance(authorlist, str):
            authorlist = [authorlist]
        addresses = talk.get("addresses") or []
        if isinstance(addresses, str):
            addresses = [addresses]
        dates = get_dates(presentation) if presentation.get("begin_date") or presentation.get("begin_year") else {}
        on = dates.get("begin_date") or dates.get("date")
        presenter_name = self._get_presenter_name(presentation, talk)

        entries = [
            self._get_author(author, addresses[index] if index < len(addresses) else "", on)
            for index, author in enumerate(authorlist)
        ]
        return number_affiliations(entries, presenter_name)

    def latex(self):
        """Render latex template."""
        for presentation in self.gtx["presentations"]:
            if not presentation.get("talk_id"):
                continue
            talk = self._get_talk(presentation)
            authors, affiliations = self._get_authors(presentation, talk)
            general = {
                "title": presentation.get("title") or "",
                "subtitle": presentation.get("subtitle") or "",
                "presenter": self._get_presenter_name(presentation, talk),
                "authors": authors,
                "affiliations": affiliations,
            }
            presentation_id = presentation.get("_id")
            self.render(
                "talk.tex",
                f"{presentation_id}.tex",
                general=general,
                topics=self._gather_topics(talk),
            )
            self.pdf(presentation_id)
