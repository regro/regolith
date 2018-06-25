"""A collection of python stylers"""

import re


def sentencecase(sentence):
    """returns a sentence in sentencecase but with text in braces preserved

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
    freezecaps = re.findall("\{[^{}]+\}", sentence)
    datalow = sentence.capitalize()
    sentencecase = re.split("\{[^{}]+\}", datalow)
    title = ''
    freezecaps.reverse()
    for word in sentencecase:
        if len(freezecaps) > 0:
            title = title + word + freezecaps.pop()
        else:
            title = title + word
    if title.lower() == 'n/a':
        title = title.lower()
    if title.lower() == 'tbd':
        title = title.lower()
    return title
