# -*- coding: utf8 -*-

"""

**SPARQLWrapper** is a simple Python wrapper around a `SPARQL <https://www.w3.org/TR/sparql11-overview/>`_ service to
remotelly execute your queries. It helps in creating the query
invokation and, possibly, convert the result into a more manageable
format.

"""

__version__ = "1.9.0.dev0"
"""The version of SPARQLWrapper"""

__agent__ = "sparqlwrapper %s (rdflib.github.io/sparqlwrapper)" % __version__


from .Wrapper import SPARQLWrapper
from .Wrapper import XML, JSON, TURTLE, N3, JSONLD, RDF, RDFXML, CSV, TSV
from .Wrapper import GET, POST
from .Wrapper import SELECT, CONSTRUCT, ASK, DESCRIBE, INSERT, DELETE
from .Wrapper import URLENCODED, POSTDIRECTLY
from .Wrapper import BASIC, DIGEST

from .SmartWrapper import SPARQLWrapper2
from .sparql_dataframe import get_sparql_dataframe
