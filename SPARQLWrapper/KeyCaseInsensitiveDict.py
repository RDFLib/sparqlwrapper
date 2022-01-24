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

from typing import Dict, Iterator, MutableMapping, TypeVar

K = str
V = TypeVar("V")


class KeyCaseInsensitiveDict(MutableMapping[K, V]):
    """
    A simple implementation of a key case-insensitive dictionary
    """

    def __init__(self, d: Dict[K, V] = {}) -> None:
        """
        :param dict d: The source dictionary.
        """
        self.data: Dict[K, V] = d

    def __setitem__(self, key: K, value: V) -> None:
        if isinstance(key, str):
            key = key.lower()
        self.data[key] = value

    def __getitem__(self, key: K) -> V:
        if isinstance(key, str):
            key = key.lower()
        return self.data[key]

    def __delitem__(self, key: K) -> None:
        if isinstance(key, str):
            key = key.lower()
        del self.data[key]

    def __len__(self) -> int:
        return len(self.data)

    def __iter__(self) -> Iterator[K]:
        return iter(self.data)
