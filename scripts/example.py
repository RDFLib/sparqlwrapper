#!/usr/bin/python
# -*- coding: utf-8 -*-

from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, RDF

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
sparql.setQuery("""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?label
    WHERE { <http://dbpedia.org/resource/Asturias> rdfs:label ?label }
""")

# JSON example
print '\n\n*** JSON Example'
sparql.setReturnFormat(JSON)
results = sparql.query().convert()
for result in results["results"]["bindings"]:
    print result["label"]["value"]

# XML example
print '\n\n*** XML Example'
sparql.setReturnFormat(XML)
results = sparql.query().convert()
print results.toxml()

# N3 example
print '\n\n*** N3 Example'
sparql.setReturnFormat(N3)
results = sparql.query().convert()
print results

# RDF example
print '\n\n*** RDF Example'
sparql.setReturnFormat(RDF)
results = sparql.query().convert()
print results.serialize()

