#!/usr/bin/python
# -*- coding: utf-8 -*-

from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://agrovoc.uniroma2.it:3030/agrovoc/sparql")

query = """
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?conceptAGROVOC ?conceptGEMET ?label
WHERE {
    ?conceptAGROVOC rdf:type skos:Concept ;
                    skos:prefLabel ?label;
                    skos:inScheme <http://voc.landportal.info/landterms> .
    FILTER (lang(?label) = 'en')

    SERVICE <http://semantic.eea.europa.eu/sparql> { 
            ?conceptGEMET skos:prefLabel ?label ; 
            skos:inScheme <http://www.eionet.europa.eu/gemet/gemetThesaurus> .
    } 
}
"""
sparql.setQuery(query)
sparql.setReturnFormat(JSON)

results = sparql.query().print_results()
