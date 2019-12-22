# -*- coding: utf8 -*-

u"""

**SPARQLWrapper** is a simple Python wrapper around a `SPARQL <https://www.w3.org/TR/sparql11-overview/>`_ service to
remotelly execute your queries. It helps in creating the query
invokation and, possibly, convert the result into a more manageable
format.

"""

__version__ = "1.8.5"
"""The version of SPARQLWrapper"""

__authors__ = "Ivan Herman, Sergio Fernández, Carlos Tejo Alonso, Alexey Zakhlestin"
"""The primary authors of SPARQLWrapper"""

__license__ = "W3C® SOFTWARE NOTICE AND LICENSE, http://www.w3.org/Consortium/Legal/copyright-software"
"""The license governing the use and distribution of SPARQLWrapper"""

__url__ = "http://rdflib.github.io/sparqlwrapper"
"""The URL for SPARQLWrapper's homepage"""

__contact__ = "rdflib-dev@googlegroups.com"
"""Mail list to contact to other people RDFLib and SPARQLWrappers folks and developers"""

__date__ = "2019-04-18"
"""Last update"""

__agent__ = "sparqlwrapper %s (rdflib.github.io/sparqlwrapper)" % __version__


from Wrapper import SPARQLWrapper
from Wrapper import XML, JSON, TURTLE, N3, JSONLD, RDF, RDFXML, CSV, TSV
from Wrapper import GET, POST
from Wrapper import SELECT, CONSTRUCT, ASK, DESCRIBE, INSERT, DELETE
from Wrapper import URLENCODED, POSTDIRECTLY
from Wrapper import BASIC, DIGEST

from SmartWrapper import SPARQLWrapper2
