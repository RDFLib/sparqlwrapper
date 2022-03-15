from SPARQLWrapper import DIGEST, POST, SPARQLWrapper

sparql = SPARQLWrapper("https://example.org/sparql-auth")

sparql.setHTTPAuth(DIGEST)
sparql.setCredentials("login", "password")
sparql.setMethod(POST)

sparql.setQuery(
    """
WITH <http://example.graph>
INSERT
{ <http://dbpedia.org/resource/Asturias> rdfs:label "Asturies"@ast }
"""
)

results = sparql.query()
print(results.response.read())
