from SPARQLWrapper import SPARQLWrapper, RDFXML, N3, TURTLE, JSONLD
from rdflib import Graph

sparql = SPARQLWrapper("http://dbpedia.org/sparql")

sparql.setQuery("""
    DESCRIBE <http://dbpedia.org/resource/Asturias>
""")

# RDF/XML example
print('\n\n*** RDF/XML Example')
sparql.setReturnFormat(RDFXML)
results = sparql.query().convert()
print(results.serialize(format='xml'))

# N3 example
print('\n\n*** N3 Example')
sparql.setReturnFormat(N3)
results = sparql.query().convert()
g = Graph()
g.parse(data=results, format="n3")
print(g.serialize(format='n3'))

# Turtle example
print('\n\n*** TURTLE Example')
sparql.setReturnFormat(TURTLE)
results = sparql.query().convert()
g = Graph()
g.parse(data=results, format="turtle")
print(g.serialize(format='turtle'))

# JSONLD example
print('\n\n*** JSONLD Example')
sparql.setReturnFormat(JSONLD)
results = sparql.query().convert()
print(results.serialize(format='json-ld'))
