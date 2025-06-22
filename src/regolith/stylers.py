"""A collection of python stylers."""

import re

month_fullnames = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}
month_threelets = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sept",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}


def sentencecase(sentence):
    """Returns a sentence in sentencecase but with text in braces
    preserved.

    Parameters
    ----------
    sentence: str
        The sentence

    Returns
    -------
    The sentence in sentence-case (but preserving any text  wrapped in braces)

    Notes
    -----
    tbd or n/a are returned lower case, not sentence case.
    """
    freezecaps = re.findall("\\{[^{}]+\\}", sentence)
    datalow = sentence.capitalize()
    sentencecase = re.split("\\{[^{}]+\\}", datalow)
    title = ""
    freezecaps.reverse()
    for word in sentencecase:
        if len(freezecaps) > 0:
            title = title + word + freezecaps.pop()
        else:
            title = title + word
    if title.lower() == "n/a":
        title = title.lower()
    if title.lower() == "tbd":
        title = title.lower()
    return title
