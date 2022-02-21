# -*- coding: utf-8 -*-

"""
A simple implementation of a key case-insensitive dictionary.
..
  Developers involved:
  * Ivan Herman <http://www.ivan-herman.net>
  * Sergio Fernández <http://www.wikier.org>
  * Carlos Tejo Alonso <http://www.dayures.net>
  * Alexey Zakhlestin <https://indeyets.ru/>
  Organizations involved:
  * `World Wide Web Consortium <http://www.w3.org>`_
  * `Foundation CTIC <http://www.fundacionctic.org/>`_
  :license: `W3C® Software notice and license <http://www.w3.org/Consortium/Legal/copyright-software>`_
"""

from typing import Dict, Mapping, TypeVar

_V = TypeVar("_V")

class KeyCaseInsensitiveDict(Dict[str, _V]):
    """
    A simple implementation of a key case-insensitive dictionary
    """

    def __init__(self, d: Mapping[str, _V]={}) -> None:
        """
        :param dict d: The source dictionary.
        """
        for k, v in d.items():
            self[k] = v

    def __setitem__(self, key: str, value: _V) -> None:
        if hasattr(key, "lower"):
            key = key.lower()
        dict.__setitem__(self, key, value)

    def __getitem__(self, key: str) -> _V:
        if hasattr(key, "lower"):
            key = key.lower()
        return dict.__getitem__(self, key)

    def __delitem__(self, key: str) -> None:
        if hasattr(key, "lower"):
            key = key.lower()
        dict.__delitem__(self, key)
