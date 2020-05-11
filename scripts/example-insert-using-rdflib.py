from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDFS

g = Graph()
asturias = URIRef("http://dbpedia.org/resource/Asturias")
g.add( (asturias, RDFS.label, Literal('Asturies', lang="ast") ) )
g.add( (asturias, RDFS.label, Literal('Asturias', lang="es") ) )
g.add( (asturias, RDFS.label, Literal('Asturien', lang="de") ) )

###############################################################################
triples = ""
for subject,predicate,obj in g:
    triples = triples + subject.n3() + " " + predicate.n3() + " " + obj.n3() + " . \n"

query = """WITH <http://example.graph>
INSERT {"""+ triples + """}"""
###############################################################################

from SPARQLWrapper import SPARQLWrapper, POST, DIGEST
  
sparql = SPARQLWrapper("https://example.org/sparql-auth")
sparql.setHTTPAuth(DIGEST)
sparql.setCredentials("login", "password")
sparql.setMethod(POST)
sparql.setQuery(query)

results = sparql.query()
print(results.response.read())
