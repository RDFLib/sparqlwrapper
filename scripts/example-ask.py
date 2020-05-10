#!/usr/bin/python
# -*- coding: utf-8 -*-

from SPARQLWrapper import SPARQLWrapper, JSON, XML, CSV, TSV

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
sparql.setQuery("""
    ASK WHERE { 
        <http://dbpedia.org/resource/Asturias> rdfs:label "Asturias"@es
    }    
""")

# JSON example
print('\n\n*** JSON Example')
sparql.setReturnFormat(JSON)
results = sparql.query().convert()
print(results)

# XML example
print('\n\n*** XML Example')
sparql.setReturnFormat(XML)
results = sparql.query().convert()
print(results.toxml())

# CSV example
print('\n\n*** CSV Example')
sparql.setReturnFormat(CSV)
results = sparql.query().convert()
print(results)

# TSV example
print('\n\n*** TSV Example')
sparql.setReturnFormat(TSV)
results = sparql.query().convert()
print(results)
