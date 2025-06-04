import datetime as dt

from regolith.dates import get_dates
from regolith.fsclient import _id_key
from regolith.helpers.basehelper import SoutHelperBase
from regolith.tools import all_docs_from_collection, strip_str

TARGET_COLL = "expenses"


def subparser(subpi):
    subpi.add_argument("payee", help="payee id for the expense", type=strip_str)
    return subpi


class ReimbstatusHelper(SoutHelperBase):
    """Helper for reimbstatus"""

    # btype must be the same as helper target in helper.py
    btype = "reimbstatus"
    needed_colls = [f"{TARGET_COLL}"]

    def construct_global_ctx(self):
        """Constructs the global context"""
        super().construct_global_ctx()
        gtx = self.gtx
        rc = self.rc
        gtx["expenses"] = sorted(all_docs_from_collection(rc.client, "expenses"), key=_id_key)
        gtx["all_docs_from_collection"] = all_docs_from_collection
        gtx["float"] = float
        gtx["str"] = str
        gtx["zip"] = zip

    def sout(self):
        rc = self.rc
        exps = self.gtx["expenses"]
        reimb, sub, unsub, future, unknown = [], [], [], [], []
        for expense in exps:
            if expense.get("payee") == rc.payee:
                dates = get_dates(expense)
                expense["end_date"] = dates["end_date"]
                expense["begin_date"] = dates["begin_date"]
                expense["begin_month"] = dates["begin_date"].month
                expense["end_month"] = dates["end_date"].month
                for j in expense.get("itemized_expenses"):
                    if j.get("unsegregated_expense") == "tbd":
                        print("WARNING: An expense in {} is tbd".format(expense["_id"]))
                        j["unsegregated_expense"] = 0
                    if j.get("exchange_rate"):
                        try:
                            j["unsegregated_expense"] = j.get("unsegregated_expense") / j.get("exchange_rate")
                        except TypeError:
                            print(
                                "exchange rate correction failed for {}, with "
                                "expense: {} rate: {}".format(
                                    expense["_id"], j.get("unsegregated_expense"), j.get("exchange_rate")
                                )
                            )
                        j["segregated_expense"] = j.get("segregated_expense") / j.get("exchange_rate")
                        j["prepaid_expense"] = j.get("prepaid_expense") / j.get("exchange_rate")
                if expense.get("status") == "reimbursed":
                    reimb.append(expense)
                elif expense.get("status") == "submitted":
                    sub.append(expense)
                elif expense.get("status") == "unsubmitted":
                    if expense["end_date"] < dt.datetime.today().date():
                        unsub.append(expense)
                    else:
                        future.append(expense)
                elif expense.get("status") == "cancelled":
                    pass
                else:
                    unknown.append(expense.get("_id"))
        sorted_reimb = sorted(reimb, key=lambda i: i["end_date"])
        sorted_sub = sorted(sub, key=lambda i: i["end_date"])
        sorted_unsub = sorted(unsub, key=lambda i: i["end_date"])
        sorted_future = sorted(future, key=lambda i: i["end_date"])
        print("Reimbursed expenses:")
        for i in sorted_reimb:
            unseg = 0
            for j in i.get("itemized_expenses"):
                unseg = unseg + j.get("unsegregated_expense")
            for j in i.get("reimbursements", []):
                reimb_dates = get_dates(j)
                print(
                    " - {} - {} {} to {}"
                    ",".format(
                        i.get("end_date").isoformat().replace("-", "")[2:],
                        i.get("overall_purpose")[:59],
                        i.get("begin_date"),
                        i.get("end_date"),
                    )
                )
                grantstring = ", ".join(i.get("grants"))
                print(
                    f"   Requested: {unseg}, "
                    f"Reimbursed: {j.get('amount')}, Date: "
                    f"{reimb_dates.get('date', dt.date(1900, 1, 1).isoformat())}, "
                    f"Grants: {grantstring}"
                )
        print("\nSubmitted expenses:")
        for i in sorted_sub:
            unseg, seg = 0, 0
            for j in i.get("itemized_expenses"):
                unseg = unseg + j.get("unsegregated_expense")
                seg = seg + j.get("segregated_expense")
            total = seg + unseg
            for j in i.get("reimbursements", []):
                print(
                    " - {} - {} {} to {}"
                    ",".format(
                        i.get("end_date").isoformat().replace("-", "")[2:],
                        i.get("overall_purpose")[:59],
                        i.get("begin_date"),
                        i.get("end_date"),
                    )
                )
                if j.get("submission_date"):
                    when = j.get("submission_date")
                else:
                    when = "-".join(
                        (
                            str(j.get("submission_year")),
                            str(j.get("submission_month")),
                            str(j.get("submission_day")),
                        )
                    )
                print(
                    "   Expenses: unseg={:.2f}, Seg={:.2f}, Total={:.2f}, Where: {}, When: {}".format(
                        unseg, seg, total, j.get("where"), when
                    )
                )
            grantstring = ", ".join(i.get("grants"))
            print("   Grants: {}".format(grantstring))
            if isinstance(i.get("notes"), str):
                print(i.get("notes"))
            else:
                for note in i.get("notes"):
                    print("    - {}".format(note[:59]))
                    if len(note) > 60:
                        print("      {}".format(note[60:]))

        print("\nUnsubmitted expenses:")
        for i in sorted_unsub:
            unseg, seg = 0, 0
            for j in i.get("itemized_expenses"):
                unseg = unseg + j.get("unsegregated_expense")
                seg = seg + j.get("segregated_expense")
            total = seg + unseg
            for j in i.get("reimbursements", []):
                print(
                    " - {} - {} {} to {}"
                    ",".format(
                        i.get("end_date").isoformat().replace("-", "")[2:],
                        i.get("overall_purpose")[:59],
                        i.get("begin_date"),
                        i.get("end_date"),
                    )
                )
                print(
                    "   Expenses: unseg={:.2f}, Seg={:.2f}, Total={:.2f}, "
                    "Where: {}".format(
                        unseg,
                        seg,
                        total,
                        j.get("where"),
                    )
                )
            grantstring = ", ".join(i.get("grants"))
            print("   Grants: {}".format(grantstring))
        print("\nFuture expenses:")
        for i in sorted_future:
            unseg, seg = 0, 0
            for j in i.get("itemized_expenses"):
                unseg = unseg + j.get("unsegregated_expense")
                seg = seg + j.get("segregated_expense")
            total = seg + unseg
            for j in i.get("reimbursements", []):
                print(
                    " - {} - {} {} to {}"
                    ",".format(
                        i.get("end_date").isoformat().replace("-", "")[2:],
                        i.get("overall_purpose")[:59],
                        i.get("begin_date"),
                        i.get("end_date"),
                    )
                )
                print(
                    "   Expenses: unseg={:.2f}, Seg={:.2f}, Total={:.2f}, ".format(
                        unseg,
                        seg,
                        total,
                    )
                )

        if len(unknown) > 0:
            print("\nThese expenses have invalid statuses:")
            print(*unknown)
