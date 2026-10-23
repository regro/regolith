"""Builder for the NSF synergistic activities document.

The activities are chosen by the uuids of entries in the person's
document, such as their service, given in the order they are to appear.
"""

from regolith.builders.basebuilder import LatexBuilderBase
from regolith.dates import get_dates
from regolith.tools import all_docs_from_collection, fuzzy_retrieval

# NSF allows no more than five activities
MAX_ACTIVITIES = 5


def entries_with_uuids(person):
    """Return every entry in the person's document that carries a uuid.

    Parameters
    ----------
    person : dict
        The person document.

    Returns
    -------
    list of dict
        The entries, from any of the person's lists, that have a uuid.
    """
    return [
        entry
        for value in person.values()
        if isinstance(value, list)
        for entry in value
        if isinstance(entry, dict) and entry.get("uuid")
    ]


def select_activities(person, uuid_fragments):
    """Return the entries chosen by full or partial uuids, in order.

    Parameters
    ----------
    person : dict
        The person document.
    uuid_fragments : list of str
        The full or partial uuids of the chosen entries.

    Returns
    -------
    activities : list of dict
        The chosen entries, in the order of the uuids.
    problems : list of str
        Each uuid that matched no entry or more than one.
    """
    candidates = entries_with_uuids(person)
    activities, problems = [], []
    for fragment in uuid_fragments:
        matches = [entry for entry in candidates if entry["uuid"].startswith(fragment)]
        if len(matches) == 1:
            activities.append(matches[0])
        elif not matches:
            problems.append(f"{fragment} matches no entry")
        else:
            problems.append(f"{fragment} matches {len(matches)} entries")
    return activities, problems


def activity_years(entry):
    """Return the years of an activity, e.g., 2018-2021 or 2019-present.

    Parameters
    ----------
    entry : dict
        The activity.

    Returns
    -------
    str
        The years, or an empty string when the activity has no dates.
    """
    dates = get_dates(entry)
    begin_date, end_date = dates.get("begin_date"), dates.get("end_date")
    if begin_date is None:
        return ""
    if end_date is None:
        return f"{begin_date.year}--present"
    if end_date.year == begin_date.year:
        return str(begin_date.year)
    return f"{begin_date.year}--{end_date.year}"


class SynergisticActivitiesBuilder(LatexBuilderBase):
    """Build the NSF synergistic activities document of a person."""

    btype = "synergistic-activities"
    needed_colls = ["people"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        self.gtx["people"] = list(all_docs_from_collection(self.rc.client, "people"))

    def _person(self):
        """Return the person whose activities are built.

        A run that names nobody builds for the user of the run control.
        """
        people = self.rc.people
        if isinstance(people, str):
            people = [people]
        if not people and getattr(self.rc, "default_user_id", None):
            people = [self.rc.default_user_id]
        if len(people) != 1:
            raise ValueError(
                "The synergistic activities are built for one person at a time. Please rerun "
                "specifying --people and one person."
            )
        person = fuzzy_retrieval(self.gtx["people"], ["_id", "name", "aka"], people[0], case_sensitive=False)
        if person is None:
            raise ValueError(f"{people[0]} is not in the people collection. Please check the id.")
        return person

    def _uuid_fragments(self, person):
        """Return the uuids given as uuid:<uuid> in the kwargs of the
        run."""
        kwargs = getattr(self.rc, "kwargs", None) or []
        fragments, unknown = [], []
        for kwarg in kwargs:
            key, _, value = kwarg.partition(":")
            if key == "uuid" and value:
                fragments.append(value)
            else:
                unknown.append(kwarg)
        if unknown:
            raise ValueError(
                f"The synergistic activities builder does not understand {', '.join(unknown)}. "
                f"Please choose each activity with --kwargs uuid:<uuid>."
            )
        if not fragments:
            choices = "\n".join(
                f"    {entry['uuid']}  {entry.get('name', '')}" for entry in entries_with_uuids(person)
            )
            raise ValueError(
                f"No activities were chosen. Please rerun with --kwargs uuid:<uuid> for up to "
                f"{MAX_ACTIVITIES} of these, in the order they should appear (the first few "
                f"characters of a uuid are enough):\n{choices}"
            )
        if len(fragments) > MAX_ACTIVITIES:
            raise ValueError(
                f"{len(fragments)} activities were chosen, but NSF allows at most {MAX_ACTIVITIES}. "
                f"Please rerun choosing no more than {MAX_ACTIVITIES}."
            )
        return fragments

    def latex(self):
        """Render the latex template."""
        person = self._person()
        activities, problems = select_activities(person, self._uuid_fragments(person))
        if problems:
            raise ValueError(
                f"Some activities could not be found in the document of {person['_id']}: "
                f"{'; '.join(problems)}. Please check the uuids; rerunning without --kwargs lists "
                f"the ones to choose from."
            )
        for activity in activities:
            activity["years"] = activity_years(activity)
        outname = f"{person['_id']}-synergistic-activities"
        self.render("synergistic_activities.tex", f"{outname}.tex", person=person, activities=activities)
        self.pdf(outname)
