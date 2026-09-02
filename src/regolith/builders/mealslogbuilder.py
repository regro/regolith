"""Builder for the daily meals log that is submitted with a travel
expense."""

import os

from pypdf import PdfReader, PdfWriter

from regolith.builders.basebuilder import BuilderBase
from regolith.dates import get_dates
from regolith.tools import all_docs_from_collection, fuzzy_retrieval

# The form has one row per day, named DateRow1 ... DateRow19, so a trip longer than
# this is written out over more than one copy of the form.
ROWS_PER_FORM = 19
# The field name for each column, keyed by the purpose the adder gives the meal.
MEAL_COLUMNS = {
    "breakfast": "BreakfastRow{}",
    "lunch": "LunchRow{}",
    "dinner": "DinnerRow{}",
    "incidentals": "IncidentalsRow{}",
}
DATE_COLUMN = "DateRow{}"
DAILY_TOTAL_COLUMN = "Daily TotalRow{}"
# The form is submitted to a US university, so the dates are written the US way.
DATE_FORMAT = "%m/%d/%Y"


def meals_by_day(expense):
    """Collect the meals of an expense into one row per day.

    Meals that were not taken are deleted from the expense rather than zeroed, so a
    day contributes a row only if at least one of its meals survives.

    Parameters
    ----------
    expense : dict
        The expense document, whose itemized_expenses carry a purpose naming the
        meal and a date saying which day it falls on.

    Returns
    -------
    list
        The rows, each a tuple of the date and a dict of amounts keyed by meal name,
        ordered by date.
    """
    days = {}
    for item in expense.get("itemized_expenses", []):
        purpose = item.get("purpose")
        if purpose not in MEAL_COLUMNS:
            continue
        dates = get_dates(item)
        date = dates.get("date", dates.get("begin_date"))
        if date is None:
            continue
        days.setdefault(date, {})[purpose] = float(item.get("unsegregated_expense", 0))
    return sorted(days.items())


def fill_form(template, rows, filename):
    """Write one copy of the meals log with the given rows filled in.

    Parameters
    ----------
    template : str
        The path to the empty form.
    rows : list
        The rows to write, as returned by meals_by_day, at most ROWS_PER_FORM of them.
    filename : str
        The path to write the filled form to.
    """
    reader = PdfReader(template)
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    values = {}
    for row_number, (date, amounts) in enumerate(rows, start=1):
        values[DATE_COLUMN.format(row_number)] = date.strftime(DATE_FORMAT)
        for purpose, column in MEAL_COLUMNS.items():
            if purpose in amounts:
                values[column.format(row_number)] = "{:.2f}".format(amounts[purpose])
        values[DAILY_TOTAL_COLUMN.format(row_number)] = "{:.2f}".format(sum(amounts.values()))
    writer.update_page_form_field_values(writer.pages[0], values)
    # without this some viewers show the fields empty, since the form carries no
    # appearance stream for the values we have just written
    writer.set_need_appearances_writer(True)
    with open(filename, "wb") as fh:
        writer.write(fh)


class MealsLogBuilder(BuilderBase):
    """Build the daily meals log for travel expenses."""

    btype = "meals-log"
    needed_colls = ["expenses", "people"]

    def __init__(self, rc):
        super().__init__(rc)
        # TODO: templates for other universities?
        self.template = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates", "ucsb-meals-log.pdf")
        self.cmds = ["pdf_form"]

    def construct_global_ctx(self):
        """Constructs the global context."""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        if not rc.people and not getattr(rc, "kwargs", None):
            raise ValueError(
                "Missing person for the meals log.  Please rerun specifying "
                "--people and a person or list of people, or --kwargs _id:<id> "
                "to build the meals log of one expense"
            )
        for n in ["expenses", "people"]:
            gtx[n] = list(all_docs_from_collection(rc.client, n))
        gtx["all_docs_from_collection"] = all_docs_from_collection

    def _selected(self, expenses):
        """Return the expenses the kwargs of the run ask for.

        A run may name one expense to build with "_id:<id>".  A run
        naming none builds every expense of the people that were asked
        for.

        Raises
        ------
        ValueError
            If a key other than _id is given, or if nothing matches what
            was asked for
        """
        kwargs = getattr(self.rc, "kwargs", None)
        if not kwargs:
            return expenses
        key, _, value = kwargs[0].partition(":")
        if key != "_id":
            raise ValueError(
                f"'{key}' is not something the meals log builder can be filtered on. Please "
                f"pass --kwargs _id:<id> to build the meals log of one expense."
            )
        selected = [expense for expense in expenses if expense.get("_id") == value]
        if not selected:
            raise ValueError(
                f"There is nothing to build, because the expense '{value}' was not found in "
                f"the expenses collection. Please check the id."
            )
        return selected

    def pdf_form(self):
        """Write one filled meals log per expense that has meals on
        it."""
        gtx = self.gtx
        rc = self.rc
        if isinstance(rc.people, str):
            rc.people = [rc.people]
        # an expense named by its id is built whoever the payee is
        named_by_id = bool(getattr(rc, "kwargs", None))
        chosen_names = []
        if not named_by_id:
            chosen_ones = [fuzzy_retrieval(gtx["people"], ["name", "aka", "_id"], one) for one in rc.people]
            chosen_names = [one.get("name") for one in chosen_ones if one]
        for expense in self._selected(sorted(gtx["expenses"], key=lambda doc: doc["_id"])):
            if not named_by_id:
                payee = fuzzy_retrieval(gtx["people"], ["name", "aka", "_id"], expense.get("payee"))
                if not payee or payee.get("name") not in chosen_names:
                    continue
            rows = meals_by_day(expense)
            if not rows:
                continue
            for form_number, start in enumerate(range(0, len(rows), ROWS_PER_FORM), start=1):
                chunk = rows[start : start + ROWS_PER_FORM]
                suffix = "" if form_number == 1 else "_{}".format(form_number)
                filename = os.path.join(self.bldir, "{}{}.pdf".format(expense["_id"], suffix))
                fill_form(self.template, chunk, filename)
                print("built {}".format(filename))
