# -*- coding: utf-8 -*-

"""
A simple implementation of a key case-insensitive dictionary.

:author: Ivan Herman <http://www.ivan-herman.net>
:author: Sergio Fernández <http://www.wikier.org>
:author: Carlos Tejo Alonso <http://www.dayures.net>
:author: Alexey Zakhlestin <https://indeyets.ru/>
:organization: `World Wide Web Consortium <http://www.w3.org>`_ and `Foundation CTIC <http://www.fundacionctic.org/>`_.
:license: `W3C® Software notice and license <http://www.w3.org/Consortium/Legal/copyright-software>`_
"""

class KeyCaseInsensitiveDict(dict):
    """
    A simple implementation of a key case-insensitive dictionary
    """

    def __init__(self, d={}):
        for k, v in d.items():
            self[k] = v

    def __setitem__(self, key, value):
        if hasattr(key, "lower"):
            key = key.lower()
        dict.__setitem__(self, key, value)

    def __getitem__(self, key):
        if hasattr(key, "lower"):
            key = key.lower()
        return dict.__getitem__(self, key)

    def __delitem__(self, key):
        if hasattr(key, "lower"):
            key = key.lower()
        dict.__delitem__(self, key)
