# -*- coding: utf8 -*-

"""

**SPARQLWrapper** is a simple Python wrapper around a `SPARQL <https://www.w3.org/TR/sparql11-overview/>`_ service to
remotelly execute your queries. It helps in creating the query
invokation and, possibly, convert the result into a more manageable
format.

"""

__version__ = "2.0.0"
"""The version of SPARQLWrapper"""

__agent__: str = f"sparqlwrapper {__version__} (rdflib.github.io/sparqlwrapper)"


from .SmartWrapper import SPARQLWrapper2
from .sparql_dataframe import get_sparql_dataframe
from .Wrapper import (
    ASK,
    BASIC,
    CONSTRUCT,
    CSV,
    DELETE,
    DESCRIBE,
    DIGEST,
    GET,
    INSERT,
    JSON,
    JSONLD,
    N3,
    POST,
    POSTDIRECTLY,
    RDF,
    RDFXML,
    SELECT,
    TSV,
    TURTLE,
    URLENCODED,
    XML,
    QueryResult,
    SPARQLWrapper,
)

__all__ = [
    "SPARQLWrapper2",
    "get_sparql_dataframe",
    "ASK",
    "BASIC",
    "CONSTRUCT",
    "CSV",
    "DELETE",
    "DESCRIBE",
    "DIGEST",
    "GET",
    "INSERT",
    "JSON",
    "JSONLD",
    "N3",
    "POST",
    "POSTDIRECTLY",
    "RDF",
    "RDFXML",
    "SELECT",
    "TSV",
    "TURTLE",
    "URLENCODED",
    "XML",
    "QueryResult",
    "SPARQLWrapper",
]
