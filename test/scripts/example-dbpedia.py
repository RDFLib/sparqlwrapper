#!/usr/bin/python
# -*- coding: utf-8 -*-

from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://dbpedia.org/sparql")

sparql.setQuery("""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?label
    WHERE { <http://dbpedia.org/resource/Asturias> rdfs:label ?label }
""")
sparql.setReturnFormat(JSON)
results = sparql.query()
results.print_results()

print

sparql.setQuery("""
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dbpo: <http://dbpedia.org/property/>
SELECT ?subdivision ?label 
WHERE { 
  <http://dbpedia.org/resource/Asturias> dbpo:subdivisionName ?subdivision .
  ?subdivision rdfs:label ?label .
}
""")
sparql.setReturnFormat(JSON)
results = sparql.query()
results.print_results()

