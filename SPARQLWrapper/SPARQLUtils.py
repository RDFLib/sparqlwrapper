# -*- coding: utf8 -*-

"""

SPARQL Wrapper Utils

@authors: U{Ivan Herman<http://www.ivan-herman.net>}, U{Sergio Fernández<http://www.wikier.org>}, U{Carlos Tejo Alonso<http://www.dayures.net>}
@organization: U{World Wide Web Consortium<http://www.w3.org>} and U{Foundation CTIC<http://www.fundacionctic.org/>}.
@license: U{W3C SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/copyright-software">}

"""

import warnings

def deprecated(func):
    """
        This is a decorator which can be used to mark functions
        as deprecated. It will result in a warning being emmitted
        when the function is used.
        @see: http://code.activestate.com/recipes/391367/
    """
    def newFunc(*args, **kwargs):
        warnings.warn("Call to deprecated function %s." % func.__name__, category=DeprecationWarning, stacklevel=2)
        return func(*args, **kwargs)
    newFunc.__name__ = func.__name__
    newFunc.__doc__ = func.__doc__
    newFunc.__dict__.update(func.__dict__)
    return newFunc

