#!/usr/bin/python
# -*- coding: utf-8 -*-

import inspect
import os
import sys

# prefer local copy to the one which is installed
# hack from http://stackoverflow.com/a/6098238/280539
_top_level_path = os.path.realpath(os.path.abspath(os.path.join(
    os.path.split(inspect.getfile(inspect.currentframe()))[0],
    ".."
)))
if _top_level_path not in sys.path:
    sys.path.insert(0, _top_level_path)
# end of hack

from SPARQLWrapper import SPARQLWrapper, RDFXML, N3, TURTLE, JSONLD
from rdflib import Graph

sparql = SPARQLWrapper("http://dbpedia.org/sparql")

sparql.setQuery("""
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX schema: <http://schema.org/>
    
    CONSTRUCT {
      ?lang a schema:Language ;
      schema:alternateName ?iso6391Code . 
    }
    WHERE {
      ?lang a dbo:Language ;
      dbo:iso6391Code ?iso6391Code .
    
      FILTER (STRLEN(?iso6391Code)=2) # to filter out non-valid values
    }
""")

# RDF/XML example
print '\n\n*** RDF/XML Example'
sparql.setReturnFormat(RDFXML)
results = sparql.query().convert()
print(results.serialize(format='xml'))

# N3 example
print '\n\n*** N3 Example'
sparql.setReturnFormat(N3)
results = sparql.query().convert()
g = Graph()
g.parse(data=results, format="n3")
print(g.serialize(format='n3'))

# Turtle example
print '\n\n*** TURTLE Example'
sparql.setReturnFormat(TURTLE)
results = sparql.query().convert()
g = Graph()
g.parse(data=results, format="turtle")
print(g.serialize(format='turtle'))

# JSONLD example
print '\n\n*** JSONLD Example'
sparql.setReturnFormat(JSONLD)
results = sparql.query().convert()
print(results.serialize(format='json-ld'))
