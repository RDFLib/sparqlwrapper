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

from collections import UserDict
from collections.abc import Hashable, Mapping
from typing import TypeVar

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


class KeyCaseInsensitiveDict(UserDict[K, V]):
    """
    A simple implementation of a key case-insensitive dictionary
    """

    def __init__(self, initdict: Mapping[K, V] = {}) -> None:
        """
        :param dict d: The source dictionary.
        """
        super().__init__(initdict)

    def __setitem__(self, key: K, value: V) -> None:
        if isinstance(key, str):
            key = key.lower()
        super().__setitem__(key, value)

    def __getitem__(self, key: K) -> V:
        if isinstance(key, str):
            key = key.lower()
        return super().__getitem__(key)

    def __delitem__(self, key: K) -> None:
        if isinstance(key, str):
            key = key.lower()
        super().__delitem__(key)
