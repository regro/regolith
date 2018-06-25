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
        The sentence in sentence-case (but preserving any text wrapped in braces)
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
    return title
