"""A collection of python stylers"""

import re


def sentencecase(string):
    """returns a string in sentencecase but with text in braces preserved

    parameters
    ----------
    string
        The string
    :returns
        The string in sentence-case (but preserving any text wrapped in braces
    """
    freezecaps = re.findall("\{[^{}]+\}", string)
    datalow = string.capitalize()
    sentencecase = re.split("\{[^{}]+\}", datalow)
    title = ''
    freezecaps.reverse()
    for word in sentencecase:
        if len(freezecaps) > 0:
            title = title + word + freezecaps.pop()
        else:
            title = title + word
    return title
