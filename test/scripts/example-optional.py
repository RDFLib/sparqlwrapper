#!/usr/bin/python
# -*- coding: utf-8 -*-

from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, RDF

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
sparql.setQuery("""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?person ?party
    WHERE { ?person <http://dbpedia.org/ontology/birthPlace> <http://dbpedia.org/resource/Asturias> 
            OPTIONAL { ?person <http://dbpedia.org/property/party> ?party }

   }

""")

# JSON example
print '\n\n*** JSON Example'
sparql.setReturnFormat(JSON)
results = sparql.query().convert()
for result in results["results"]["bindings"]:
    if result.has_key("party"):
        print "* " + result["person"]["value"] + " ** " + result["party"]["value"]
    else:
        print result["person"]["value"]
