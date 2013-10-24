# -*- coding: utf-8 -*-

"""
A simple implementation of a key case-insensitive dictionary.

@authors: U{Ivan Herman<http://www.ivan-herman.net>}, U{Sergio Fernández<http://www.wikier.org>}, U{Carlos Tejo Alonso<http://www.dayures.net>}
@organization: U{World Wide Web Consortium<http://www.w3.org>} and U{Foundation CTIC<http://www.fundacionctic.org/>}.
@license: U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/copyright-software">}
"""

class KeyCaseInsensitiveDict(dict):
    """
    A simple implementation of a key case-insensitive dictionary
    """

    def __init__(self, d={}):
        for k, v in d.items():
            self[k] = v

    def __setitem__(self, key, value):
        if (hasattr(key, "lower")):
            key = key.lower()
        dict.__setitem__(self, key, value)

    def __getitem__(self, key):
        if (hasattr(key, "lower")):
            key = key.lower()
        return dict.__getitem__(self, key)

    def __delitem__(self, key):
        if hasattr(key, "lower"):
            key = key.lower()
        dict.__delitem__(self, key)

