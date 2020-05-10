# -*- coding: utf-8 -*-
#!/usr/bin/python

import inspect
import os
import sys
import unittest

# prefer local copy to the one which is installed
# hack from http://stackoverflow.com/a/6098238/280539
_top_level_path = os.path.realpath(os.path.abspath(os.path.join(
    os.path.split(inspect.getfile(inspect.currentframe()))[0],
    ".."
)))
if _top_level_path not in sys.path:
    sys.path.insert(0, _top_level_path)
# end of hack

import warnings
warnings.simplefilter("always")

try:
    from rdflib.graph import ConjunctiveGraph
except ImportError:
    from rdflib import ConjunctiveGraph

from SPARQLWrapper import SPARQLWrapper, XML, RDFXML, RDF, N3, TURTLE, JSONLD, JSON, CSV, TSV, POST, GET
from SPARQLWrapper.Wrapper import _SPARQL_XML, _SPARQL_JSON, _XML, _RDF_XML, _RDF_N3, _RDF_TURTLE, _RDF_JSONLD, _CSV, _TSV
from SPARQLWrapper.SPARQLExceptions import QueryBadFormed

_SPARQL_SELECT_ASK_POSSIBLE = _SPARQL_XML + _SPARQL_JSON + _CSV + _TSV + _XML # only used in test
_SPARQL_DESCRIBE_CONSTRUCT_POSSIBLE = _RDF_XML + _RDF_N3 + _XML + _RDF_JSONLD # only used in test. Same as Wrapper._RDF_POSSIBLE

from urllib.error import HTTPError

import logging
logging.basicConfig()

endpoint = "http://sparql.agroportal.lirmm.fr/sparql/" # 4store SPARQL server v1.1.5-122-g1788d29

prefixes = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
"""

selectQuery = """
    SELECT DISTINCT ?s WHERE {
         ?s a ?o .
         VALUES ?o {<http://id.agrisemantics.org/vocab#Organism>}
    } LIMIT 100
"""

selectQueryCSV_TSV = """
    SELECT DISTINCT ?s ?o WHERE {
         ?s a ?o .
         VALUES ?o {<http://id.agrisemantics.org/vocab#Organism>}
    } LIMIT 100
 """
askQuery = """
    ASK { <http://id.agrisemantics.org/gacs/C29647> a ?type }
"""

constructQuery = """
    CONSTRUCT {
        _:v skos:prefLabel ?label .
        _:v rdfs:comment "this is only a mock node to test library"
    }
    WHERE {
        <http://id.agrisemantics.org/gacs/C29647> skos:prefLabel ?label .
    }
"""

describeQuery = """
    DESCRIBE <http://id.agrisemantics.org/gacs/C29647>
"""

queryBadFormed = """
    PREFIX prop: <http://dbpedia.org/property/>
    PREFIX res: <http://dbpedia.org/resource/>
    FROM <http://dbpedia.org/sparql?default-graph-uri=http%3A%2F%2Fdbpedia.org&should-sponge=&query=%0D%0ACONSTRUCT+%7B%0D%0A++++%3Chttp%3A%2F%2Fdbpedia.org%2Fresource%2FBudapest%3E+%3Fp+%3Fo.%0D%0A%7D%0D%0AWHERE+%7B%0D%0A++++%3Chttp%3A%2F%2Fdbpedia.org%2Fresource%2FBudapest%3E+%3Fp+%3Fo.%0D%0A%7D%0D%0A&format=application%2Frdf%2Bxml>
    SELECT ?lat ?long
    WHERE {
        res:Budapest prop:latitude ?lat;
        prop:longitude ?long.
    }
"""

queryManyPrefixes = """
    PREFIX conf: <http://richard.cyganiak.de/2007/pubby/config.rdf#>
    PREFIX meta: <http://example.org/metadata#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX dc: <http://purl.org/dc/elements/1.1/>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
    PREFIX dbpedia: <http://dbpedia.org/resource/>
    PREFIX o: <http://dbpedia.org/ontology/>
    PREFIX p: <http://dbpedia.org/property/>
    PREFIX yago: <http://dbpedia.org/class/yago/>
    PREFIX units: <http://dbpedia.org/units/>
    PREFIX geonames: <http://www.geonames.org/ontology#>
    PREFIX prv: <http://purl.org/net/provenance/ns#>
    PREFIX prvTypes: <http://purl.org/net/provenance/types#>
    PREFIX foo: <http://purl.org/foo>

    SELECT ?label
    WHERE {
        <http://dbpedia.org/resource/Asturias> rdfs:label ?label .
    }
"""

queryDuplicatedPrefix = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?s ?p ?o WHERE {
        ?s ?p ?o .
    } LIMIT 10
"""

queryWithCommaInCurie_1 = """
    PREFIX dbpedia: <http://dbpedia.org/resource/>
    SELECT ?article ?title WHERE {
        ?article ?relation dbpedia:Victoria\\,\\_British\\_Columbia .
        ?article <http://xmlns.com/foaf/0.1/isPrimaryTopicOf> ?title
    }
"""

queryWithCommaInCurie_2 = """
    PREFIX dbpedia: <http://dbpedia.org/resource/>
    SELECT ?article ?title WHERE {
        ?article ?relation dbpedia:Category\:Victoria\,\_British\_Columbia .
        ?article <http://xmlns.com/foaf/0.1/isPrimaryTopicOf> ?title
    }
"""

queryWithCommaInUri = """
    SELECT ?article ?title WHERE {
        ?article ?relation <http://dbpedia.org/resource/Category:Victoria,_British_Columbia> .
        ?article <http://xmlns.com/foaf/0.1/isPrimaryTopicOf> ?title
    }
"""

class SPARQLWrapperTests(unittest.TestCase):

    def __generic(self, query, returnFormat, method, onlyConneg=False): # 4store uses URL parameters or conneg.
        sparql = SPARQLWrapper(endpoint)
        sparql.setQuery(prefixes + query)
        sparql.setReturnFormat(returnFormat)
        sparql.setMethod(method)
        sparql.setOnlyConneg(onlyConneg)
        try:
            result = sparql.query()
        except HTTPError:
            # An ugly way to get the exception, but the only one that works
            # both on Python 2.5 and Python 3.
            e = sys.exc_info()[1]
            if e.code == 400:
                sys.stdout.write("400 Bad Request, probably query is not well formed")
            elif e.code == 406:
                sys.stdout.write("406 Not Acceptable, maybe query is not well formed")
            else:
                sys.stdout.write(str(e))
            sys.stdout.write("\n")
            return False
        else:
            return result


################################################################################
################################################################################

################
#### SELECT ####
################

    def testSelectByGETinXML(self):
        result = self.__generic(selectQuery, XML, GET)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_XML], ct
        results = result.convert()
        self.assertEqual(results.__class__.__module__, "xml.dom.minidom")
        self.assertEqual(results.__class__.__name__, "Document")

    def testSelectByGETinXML_Conneg(self):
        result = self.__generic(selectQuery, XML, GET, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_XML], ct
        results = result.convert()
        self.assertEqual(results.__class__.__module__, "xml.dom.minidom")
        self.assertEqual(results.__class__.__name__, "Document")

    def testSelectByPOSTinXML(self):
        result = self.__generic(selectQuery, XML, POST)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_XML], ct
        results = result.convert()
        self.assertEqual(results.__class__.__module__, "xml.dom.minidom")
        self.assertEqual(results.__class__.__name__, "Document")

    def testSelectByPOSTinXML_Conneg(self):
        result = self.__generic(selectQuery, XML, POST, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_XML], ct
        results = result.convert()
        self.assertEqual(results.__class__.__module__, "xml.dom.minidom")
        self.assertEqual(results.__class__.__name__, "Document")

    def testSelectByGETinCSV(self):
        result = self.__generic(selectQueryCSV_TSV, CSV, GET)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _CSV], ct
        results = result.convert()
        self.assertEqual(type(results), bytes)

    def testSelectByGETinCSV_Conneg(self):
        result = self.__generic(selectQueryCSV_TSV, CSV, GET, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _CSV], ct
        results = result.convert()
        self.assertEqual(type(results), bytes)

    def testSelectByPOSTinCSV(self):
        result = self.__generic(selectQueryCSV_TSV, CSV, POST)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _CSV], ct
        results = result.convert()
        self.assertEqual(type(results), bytes)

    def testSelectByPOSTinCSV_Conneg(self):
        result = self.__generic(selectQueryCSV_TSV, CSV, POST, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _CSV], ct
        results = result.convert()
        self.assertEqual(type(results), bytes)

    @unittest.skip("4store does not support receiving unexpected output values (check Wrapper code for TSV URL generation)")
    def testSelectByGETinTSV(self):
        result = self.__generic(selectQueryCSV_TSV, TSV, GET)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _TSV], ct
        results = result.convert()
        self.assertEqual(type(results), bytes)

    def testSelectByGETinTSV_Conneg(self):
        result = self.__generic(selectQueryCSV_TSV, TSV, GET, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _TSV], ct
        results = result.convert()
        self.assertEqual(type(results), bytes)

    def testSelectByPOSTinTSV(self):
        result = self.__generic(selectQueryCSV_TSV, TSV, POST)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _TSV], ct
        results = result.convert()
        self.assertEqual(type(results), bytes)

    def testSelectByPOSTinTSV_Conneg(self):
        result = self.__generic(selectQueryCSV_TSV, TSV, POST, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _TSV], ct
        results = result.convert()
        self.assertEqual(type(results), bytes)

    def testSelectByGETinJSON(self):
        result = self.__generic(selectQuery, JSON, GET)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_JSON], ct
        results = result.convert()
        self.assertEqual(type(results), dict)

    def testSelectByGETinJSON_Conneg(self):
        result = self.__generic(selectQuery, JSON, GET, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_JSON], ct
        results = result.convert()
        self.assertEqual(type(results), dict)

    def testSelectByPOSTinJSON(self):
        result = self.__generic(selectQuery, JSON, POST)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_JSON], ct
        results = result.convert()
        self.assertEqual(type(results), dict)

    def testSelectByPOSTinJSON_Conneg(self):
        result = self.__generic(selectQuery, JSON, POST, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_JSON], ct
        results = result.convert()
        self.assertEqual(type(results), dict)

    # Asking for an unexpected return format for SELECT queryType (n3 is not supported, and it is not a valid alias).
    # Set by default None (and sending */*).
    # For a SELECT query type, the default return mimetype (if Accept: */* is sent) is application/sparql-results+xml
    @unittest.skip("4store does not support receiving unexpected output values (n3 is not a valid alias)")
    def testSelectByGETinN3_Unexpected(self):
        result = self.__generic(selectQuery, N3, GET)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_SELECT_ASK_POSSIBLE], ct
        results = result.convert()
        self.assertEqual(results.__class__.__module__, "xml.dom.minidom")
        self.assertEqual(results.__class__.__name__, "Document")

    # Asking for an unexpected return format for SELECT queryType (n3 is not supported, and it is not a valid alias).
    # Set by default None (and sending */*).
    # For a SELECT query type, the default return mimetype (if Accept: */* is sent) is application/sparql-results+xml
    def testSelectByGETinN3_Unexpected_Conneg(self):
        result = self.__generic(selectQuery, N3, GET, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_SELECT_ASK_POSSIBLE], ct
        results = result.convert()
        self.assertEqual(results.__class__.__module__, "xml.dom.minidom")
        self.assertEqual(results.__class__.__name__, "Document")

    # Asking for an unexpected return format for SELECT queryType (n3 is not supported, and it is not a valid alias).
    # Set by default None (and sending */*).
    # For a SELECT query type, the default return mimetype (if Accept: */* is sent) is application/sparql-results+xml
    def testSelectByPOSTinN3_Unexpected(self):
        result = self.__generic(selectQuery, N3, POST)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_SELECT_ASK_POSSIBLE], ct
        results = result.convert()
        self.assertEqual(results.__class__.__module__, "xml.dom.minidom")
        self.assertEqual(results.__class__.__name__, "Document")

    # Asking for an unexpected return format for SELECT queryType (n3 is not supported, and it is not a valid alias).
    # Set by default None (and sending */*).
    # For a SELECT query type, the default return mimetype (if Accept: */* is sent) is application/sparql-results+xml
    def testSelectByPOSTinN3_Unexpected_Conneg(self):
        result = self.__generic(selectQuery, N3, POST, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_SELECT_ASK_POSSIBLE], ct
        results = result.convert()
        self.assertEqual(results.__class__.__module__, "xml.dom.minidom")
        self.assertEqual(results.__class__.__name__, "Document")

    @unittest.skip("4store does not support receiving unexpected output values (json-ld is not a valid alias)")
    def testSelectByGETinJSONLD_Unexpected(self):
        result = self.__generic(selectQuery, JSONLD, GET)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_SELECT_ASK_POSSIBLE], ct
        results = result.convert()
        self.assertEqual(results.__class__.__module__, "xml.dom.minidom")
        self.assertEqual(results.__class__.__name__, "Document")

    # Asking for an unexpected return format for SELECT queryType (json-ld is not supported, it is not a valid alias).
    # Set by default None (and sending */*).
    # For a SELECT query type, the default return mimetype (if Accept: */* is sent) is application/sparql-results+xml
    def testSelectByGETinJSONLD_Unexpected_Conneg(self):
        result = self.__generic(selectQuery, JSONLD, GET, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_SELECT_ASK_POSSIBLE], ct
        results = result.convert()
        self.assertEqual(results.__class__.__module__, "xml.dom.minidom")
        self.assertEqual(results.__class__.__name__, "Document")

    # Asking for an unexpected return format for SELECT queryType (json-ld is not supported, it is not a valid alias).
    # Set by default None (and sending */*).
    # For a SELECT query type, the default return mimetype (if Accept: */* is sent) is application/sparql-results+xml
    def testSelectByPOSTinJSONLD_Unexpected(self):
        result = self.__generic(selectQuery, JSONLD, POST)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_SELECT_ASK_POSSIBLE], ct
        results = result.convert()
        self.assertEqual(results.__class__.__module__, "xml.dom.minidom")
        self.assertEqual(results.__class__.__name__, "Document")

    # Asking for an unexpected return format for SELECT queryType (json-ld is not supported, it is not a valid alias).
    # Set by default None (and sending */*).
    # For a SELECT query type, the default return mimetype (if Accept: */* is sent) is application/sparql-results+xml
    def testSelectByPOSTinJSONLD_Unexpected_Conneg(self):
        result = self.__generic(selectQuery, JSONLD, POST, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_SELECT_ASK_POSSIBLE], ct
        results = result.convert()
        self.assertEqual(results.__class__.__module__, "xml.dom.minidom")
        self.assertEqual(results.__class__.__name__, "Document")

    # Asking for an unknown return format for SELECT queryType (XML is sent)
    # For a SELECT query type, the default return mimetype (if Accept: */* is sent) is application/sparql-results+xml
    def testSelectByGETinUnknow(self):
        result = self.__generic(selectQuery, "foo", GET)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_SELECT_ASK_POSSIBLE], ct
        results = result.convert()
        self.assertEqual(results.__class__.__module__, "xml.dom.minidom")
        self.assertEqual(results.__class__.__name__, "Document")

    # Asking for an unknown return format for SELECT queryType (XML is sent)
    # For a SELECT query type, the default return mimetype (if Accept: */* is sent) is application/sparql-results+xml
    def testSelectByGETinUnknow_Conneg(self):
        result = self.__generic(selectQuery, "foo", GET, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_SELECT_ASK_POSSIBLE], ct
        results = result.convert()
        self.assertEqual(results.__class__.__module__, "xml.dom.minidom")
        self.assertEqual(results.__class__.__name__, "Document")

    # Asking for an unknown return format for SELECT queryType (XML is sent)
    # For a SELECT query type, the default return mimetype (if Accept: */* is sent) is application/sparql-results+xml
    def testSelectByPOSTinUnknow(self):
        result = self.__generic(selectQuery, "bar", POST)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_SELECT_ASK_POSSIBLE], ct
        results = result.convert()
        self.assertEqual(results.__class__.__module__, "xml.dom.minidom")
        self.assertEqual(results.__class__.__name__, "Document")

    # Asking for an unknown return format for SELECT queryType (XML is sent)
    # For a SELECT query type, the default return mimetype (if Accept: */* is sent) is application/sparql-results+xml
    def testSelectByPOSTinUnknow_Conneg(self):
        result = self.__generic(selectQuery, "bar", POST, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_SELECT_ASK_POSSIBLE], ct
        results = result.convert()
        self.assertEqual(results.__class__.__module__, "xml.dom.minidom")
        self.assertEqual(results.__class__.__name__, "Document")

################################################################################
################################################################################

#############
#### ASK ####
#############

    def testAskByGETinXML(self):
        result = self.__generic(askQuery, XML, GET)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_XML], ct
        results = result.convert()
        self.assertEqual(results.__class__.__module__, "xml.dom.minidom")
        self.assertEqual(results.__class__.__name__, "Document")

    def testAskByGETinXML_Conneg(self):
        result = self.__generic(askQuery, XML, GET, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_XML], ct
        results = result.convert()
        self.assertEqual(results.__class__.__module__, "xml.dom.minidom")
        self.assertEqual(results.__class__.__name__, "Document")

    def testAskByPOSTinXML(self):
        result = self.__generic(askQuery, XML, POST)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_XML], ct
        results = result.convert()
        self.assertEqual(results.__class__.__module__, "xml.dom.minidom")
        self.assertEqual(results.__class__.__name__, "Document")

    def testAskByPOSTinXML_Conneg(self):
        result = self.__generic(askQuery, XML, POST, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_XML], ct
        results = result.convert()
        self.assertEqual(results.__class__.__module__, "xml.dom.minidom")
        self.assertEqual(results.__class__.__name__, "Document")

    def testAskByGETinCSV(self):
        result = self.__generic(askQuery, CSV, GET)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _CSV], ct
        results = result.convert()
        self.assertEqual(type(results), bytes)

    def testAskByGETinCSV_Conneg(self):
        result = self.__generic(askQuery, CSV, GET, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _CSV], ct
        results = result.convert()
        self.assertEqual(type(results), bytes)

    def testAskByPOSTinCSV(self):
        result = self.__generic(askQuery, CSV, POST)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _CSV], ct
        results = result.convert()
        self.assertEqual(type(results), bytes)

    def testAskByPOSTinCSV_Conneg(self):
        result = self.__generic(askQuery, CSV, POST, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _CSV], ct
        results = result.convert()
        self.assertEqual(type(results), bytes)

    @unittest.skip("TSV is supported for 4store, but it returns a text/plain instead of text/tab-separated-values")
    def testAskByGETinTSV(self):
        result = self.__generic(askQuery, TSV, GET)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _TSV], ct
        results = result.convert()
        self.assertEqual(type(results), bytes)

    def testAskByGETinTSV_Conneg(self):
        result = self.__generic(askQuery, TSV, GET, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _TSV], ct
        results = result.convert()
        self.assertEqual(type(results), bytes)

    def testAskByPOSTinTSV(self):
        result = self.__generic(askQuery, TSV, POST)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _TSV], ct
        results = result.convert()
        self.assertEqual(type(results), bytes)

    def testAskByPOSTinTSV_Conneg(self):
        result = self.__generic(askQuery, TSV, POST, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _TSV], ct
        results = result.convert()
        self.assertEqual(type(results), bytes)

    def testAskByGETinJSON(self):
        result = self.__generic(askQuery, JSON, GET)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_JSON], ct
        results = result.convert()
        self.assertEqual(type(results), dict)

    def testAskByGETinJSON_Conneg(self):
        result = self.__generic(askQuery, JSON, GET, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_JSON], ct
        results = result.convert()
        self.assertEqual(type(results), dict)

    def testAskByPOSTinJSON(self):
        result = self.__generic(askQuery, JSON, POST)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_JSON], ct
        results = result.convert()
        self.assertEqual(type(results), dict)

    def testAskByPOSTinJSON_Conneg(self):
        result = self.__generic(askQuery, JSON, POST, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_JSON], ct
        results = result.convert()
        self.assertEqual(type(results), dict)

    @unittest.skip("4store does not support receiving unexpected output values (n3 is not a valid alias)")
    def testAskByGETinN3_Unexpected(self):
        result = self.__generic(askQuery, N3, GET)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_SELECT_ASK_POSSIBLE], ct
        results = result.convert()
        self.assertEqual(results.__class__.__module__, "xml.dom.minidom")
        self.assertEqual(results.__class__.__name__, "Document")

    # Asking for an unexpected return format for ASK queryType (n3 is not supported, it is not a valid alias).
    # Set by default None (and sending */*).
    # For an ASK query type, the default return mimetype (if Accept: */* is sent) is application/sparql-results+xml
    def testAskByGETinN3_Unexpected_Conneg(self):
        result = self.__generic(askQuery, N3, GET, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_SELECT_ASK_POSSIBLE], ct
        results = result.convert()
        self.assertEqual(results.__class__.__module__, "xml.dom.minidom")
        self.assertEqual(results.__class__.__name__, "Document")

    # Asking for an unexpected return format for ASK queryType (json-ld is not supported, it is not a valid alias).
    # Set by default None (and sending */*).
    # For an ASK query type, the default return mimetype (if Accept: */* is sent) is application/sparql-results+xml
    def testAskByPOSTinN3_Unexpected(self):
        result = self.__generic(askQuery, N3, POST)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_SELECT_ASK_POSSIBLE], ct
        results = result.convert()
        self.assertEqual(results.__class__.__module__, "xml.dom.minidom")
        self.assertEqual(results.__class__.__name__, "Document")

    # Asking for an unexpected return format for ASK queryType (n3 is not supported, it is not a valid alias).
    # Set by default None (and sending */*).
    # For an ASK query type, the default return mimetype (if Accept: */* is sent) is application/sparql-results+xml
    def testAskByPOSTinN3_Unexpected_Conneg(self):
        result = self.__generic(askQuery, N3, POST, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_SELECT_ASK_POSSIBLE], ct
        results = result.convert()
        self.assertEqual(results.__class__.__module__, "xml.dom.minidom")
        self.assertEqual(results.__class__.__name__, "Document")

    @unittest.skip("4store does not support receiving unexpected output values (json-ld is not a valid alias)")
    def testAskByGETinJSONLD_Unexpected(self):
        result = self.__generic(askQuery, JSONLD, GET)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_SELECT_ASK_POSSIBLE], ct
        results = result.convert()
        self.assertEqual(results.__class__.__module__, "xml.dom.minidom")
        self.assertEqual(results.__class__.__name__, "Document")

    # Asking for an unexpected return format for ASK queryType (json-ld is not supported, it is not a valid alias).
    # Set by default None (and sending */*).
    # For an ASK query type, the default return mimetype (if Accept: */* is sent) is application/sparql-results+xml
    def testAskByGETinJSONLD_Unexpected_Conneg(self):
        result = self.__generic(askQuery, JSONLD, GET, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_SELECT_ASK_POSSIBLE], ct
        results = result.convert()
        self.assertEqual(results.__class__.__module__, "xml.dom.minidom")
        self.assertEqual(results.__class__.__name__, "Document")

    # Asking for an unexpected return format for ASK queryType (json-ld is not supported, it is not a valid alias).
    # Set by default None (and sending */*).
    # For an ASK query type, the default return mimetype (if Accept: */* is sent) is application/sparql-results+xml
    def testAskByPOSTinJSONLD_Unexpected(self):
        result = self.__generic(askQuery, JSONLD, POST)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_SELECT_ASK_POSSIBLE], ct
        results = result.convert()
        self.assertEqual(results.__class__.__module__, "xml.dom.minidom")
        self.assertEqual(results.__class__.__name__, "Document")

    # Asking for an unexpected return format for ASK queryType (json-ld is not supported, it is not a valid alias).
    # Set by default None (and sending */*).
    # For an ASK query type, the default return mimetype (if Accept: */* is sent) is application/sparql-results+xml
    def testAskByPOSTinJSONLD_Unexpected_Conneg(self):
        result = self.__generic(askQuery, JSONLD, POST, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_SELECT_ASK_POSSIBLE], ct
        results = result.convert()
        self.assertEqual(results.__class__.__module__, "xml.dom.minidom")
        self.assertEqual(results.__class__.__name__, "Document")

    # asking for an unknown return format for ASK queryType (XML is sent)
    # For an ASK query type, the default return mimetype (if Accept: */* is sent) is application/sparql-results+xml
    def testAskByGETinUnknow(self):
        result = self.__generic(askQuery, "foo", GET)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_SELECT_ASK_POSSIBLE], ct
        results = result.convert()
        self.assertEqual(results.__class__.__module__, "xml.dom.minidom")
        self.assertEqual(results.__class__.__name__, "Document")

    # Asking for an unknown return format for ASK queryType (XML is sent)
    # For an ASK query type, the default return mimetype (if Accept: */* is sent) is application/sparql-results+xml
    def testAskByGETinUnknow_Conneg(self):
        result = self.__generic(askQuery, "foo", GET, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_SELECT_ASK_POSSIBLE], ct
        results = result.convert()
        self.assertEqual(results.__class__.__module__, "xml.dom.minidom")
        self.assertEqual(results.__class__.__name__, "Document")

    # Asking for an unknown return format for ASK queryType (XML is sent)
    # For an ASK query type, the default return mimetype (if Accept: */* is sent) is application/sparql-results+xml
    def testAskByPOSTinUnknow(self):
        result = self.__generic(askQuery, "bar", POST)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_SELECT_ASK_POSSIBLE], ct
        results = result.convert()
        self.assertEqual(results.__class__.__module__, "xml.dom.minidom")
        self.assertEqual(results.__class__.__name__, "Document")

    # Asking for an unknown return format for ASK queryType (XML is sent)
    # For an ASK query type, the default return mimetype (if Accept: */* is sent) is application/sparql-results+xml
    def testAskByPOSTinUnknow_Conneg(self):
        result = self.__generic(askQuery, "bar", POST, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_SELECT_ASK_POSSIBLE], ct
        results = result.convert()
        self.assertEqual(results.__class__.__module__, "xml.dom.minidom")
        self.assertEqual(results.__class__.__name__, "Document")

################################################################################
################################################################################

###################
#### CONSTRUCT ####
###################

    def testConstructByGETinXML(self):
        result = self.__generic(constructQuery, XML, GET)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_XML], ct
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    def testConstructByGETinXML_Conneg(self):
        result = self.__generic(constructQuery, XML, GET, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_XML], ct
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    def testConstructByPOSTinXML(self):
        result = self.__generic(constructQuery, XML, POST)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_XML], ct
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    def testConstructByPOSTinXML_Conneg(self):
        result = self.__generic(constructQuery, XML, POST, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_XML], ct
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    @unittest.skip("4store does not support receiving unexpected output values (rdf+xml is not a valid alias)")
    def testConstructByGETinRDFXML(self):
        result = self.__generic(constructQuery, RDFXML, GET)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_XML], ct
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    # rdf+xml is not a valid alias
    def testConstructByGETinRDFXML_Conneg(self):
        result = self.__generic(constructQuery, RDFXML, GET, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_XML], ct
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    def testConstructByPOSTinRDFXML(self):
        result = self.__generic(constructQuery, RDFXML, POST)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_XML], ct
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    # rdf+xml is not a valid alias
    def testConstructByPOSTinRDFXML_Conneg(self):
        result = self.__generic(constructQuery, RDFXML, POST, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_XML], ct
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    # turtle is not a valid alias ('text' is the one used)
    @unittest.skip("4store does not support receiving unexpected output values (turtle is not a valid alias)")
    def testConstructByGETinTURTLE(self):
        result = self.__generic(constructQuery, TURTLE, GET)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_TURTLE], ct
        results = result.convert()
        self.assertEqual(type(results), bytes)

    # turtle is not a valid alias ('text' is the one used)
    # Working with Content Negotiation
    def testConstructByGETinTURTLE_Conneg(self):
        result = self.__generic(constructQuery, TURTLE, GET, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_TURTLE], ct
        results = result.convert()
        self.assertEqual(type(results), bytes)

    # turtle is not a valid alias ('text' is the one used)
    # But it returns text/turtle
    def testConstructByPOSTinTURTLE(self):
        result = self.__generic(constructQuery, TURTLE, POST)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_TURTLE], ct
        results = result.convert()
        self.assertEqual(type(results), bytes)

    # turtle is not a valid alias ('text' is the one used)
    # Working with Content Negotiation
    def testConstructByPOSTinTURTLE_Conneg(self):
        result = self.__generic(constructQuery, TURTLE, POST, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_TURTLE], ct
        results = result.convert()
        self.assertEqual(type(results), bytes)

    @unittest.skip("4store does not support receiving unexpected output values (n3 is not a valid alias)")
    def testConstructByGETinN3(self):
        result = self.__generic(constructQuery, N3, GET)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_N3], ct
        results = result.convert()
        self.assertEqual(type(results), bytes)

    # Returns text/turtle
    def testConstructByGETinN3_Conneg(self):
        result = self.__generic(constructQuery, N3, GET, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_N3], ct
        results = result.convert()
        self.assertEqual(type(results), bytes)

    def testConstructByPOSTinN3(self):
        result = self.__generic(constructQuery, N3, POST)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_N3], ct
        results = result.convert()
        self.assertEqual(type(results), bytes)

    # Returns text/turtle
    def testConstructByPOSTinN3_Conneg(self):
        result = self.__generic(constructQuery, N3, POST, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_N3], ct
        results = result.convert()
        self.assertEqual(type(results), bytes)

    @unittest.skip("JSON-LD is not currently supported")
    def testConstructByGETinJSONLD(self):
        result = self.__generic(constructQuery, JSONLD, GET)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_JSONLD], ct
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    @unittest.skip("JSON-LD is not currently supported")
    def testConstructByGETinJSONLD_Conneg(self):
        result = self.__generic(constructQuery, JSONLD, GET, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_JSONLD], ct
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    @unittest.skip("JSON-LD is not currently supported")
    def testConstructByPOSTinJSONLD(self):
        result = self.__generic(constructQuery, JSONLD, POST)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_JSONLD], ct
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    @unittest.skip("JSON-LD is not currently supported")
    def testConstructByPOSTinJSONLD_Conneg(self):
        result = self.__generic(constructQuery, JSONLD, POST, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_JSONLD], ct
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    # Asking for an unexpected return format for CONSTRUCT queryType.
    # For a CONSTRUCT query type, the default return mimetype (if Accept: */* is sent) is application/rdf+xml
    @unittest.skip("4store returns text/turtle instead of the expected default application/rdf+xml")
    def testConstructByGETinCSV_Unexpected(self):
        result = self.__generic(constructQuery, CSV, GET)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_DESCRIBE_CONSTRUCT_POSSIBLE]
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    # Asking for an unexpected return format for CONSTRUCT queryType.
    # For a CONSTRUCT query type, the default return mimetype (if Accept: */* is sent) is application/rdf+xml
    def testConstructByGETinCSV_Unexpected_Conneg(self):
        result = self.__generic(constructQuery, CSV, GET, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_DESCRIBE_CONSTRUCT_POSSIBLE]
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    # Asking for an unexpected return format for CONSTRUCT queryType.
    # For a CONSTRUCT query type, the default return mimetype (if Accept: */* is sent) is application/rdf+xml
    def testConstructByPOSTinCSV_Unexpected(self):
        result = self.__generic(constructQuery, CSV, POST)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_DESCRIBE_CONSTRUCT_POSSIBLE]
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    # Asking for an unexpected return format for CONSTRUCT queryType.
    # For a CONSTRUCT query type, the default return mimetype (if Accept: */* is sent) is application/rdf+xml
    def testConstructByPOSTinCSV_Unexpected_Conneg(self):
        result = self.__generic(constructQuery, CSV, POST, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_DESCRIBE_CONSTRUCT_POSSIBLE]
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    # Asking for an unexpected return format for CONSTRUCT queryType.
    # For a CONSTRUCT query type, the default return mimetype (if Accept: */* is sent) is application/rdf+xml
    @unittest.skip("4store returns text/turtle instead of the expected default application/rdf+xml")
    def testConstructByGETinJSON_Unexpected(self):
        result = self.__generic(constructQuery, JSON, GET)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_DESCRIBE_CONSTRUCT_POSSIBLE]
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    def testConstructByGETinJSON_Unexpected_Conneg(self):
        result = self.__generic(constructQuery, JSON, GET , onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_DESCRIBE_CONSTRUCT_POSSIBLE]
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    # Asking for an unexpected return format for CONSTRUCT queryType.
    # For a CONSTRUCT query type, the default return mimetype (if Accept: */* is sent) is application/rdf+xml
    def testConstructByPOSTinJSON_Unexpected(self):
        result = self.__generic(constructQuery, JSON, POST)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_DESCRIBE_CONSTRUCT_POSSIBLE]
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    # Asking for an unexpected return format for CONSTRUCT queryType.
    # For a CONSTRUCT query type, the default return mimetype (if Accept: */* is sent) is application/rdf+xml
    def testConstructByPOSTinJSON_Unexpected_Conneg(self):
        result = self.__generic(constructQuery, JSON, POST, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_DESCRIBE_CONSTRUCT_POSSIBLE]
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    # Asking for an unknown return format for CONSTRUCT queryType (XML is sent)
    # For a CONSTRUCT query type, the default return mimetype (if Accept: */* is sent) is application/rdf+xml
    def testConstructByGETinUnknow(self):
        result = self.__generic(constructQuery, "foo", GET)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_DESCRIBE_CONSTRUCT_POSSIBLE], ct
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    # Asking for an unknown return format for CONSTRUCT queryType (XML is sent)
    # For a CONSTRUCT query type, the default return mimetype (if Accept: */* is sent) is application/rdf+xml
    def testConstructByGETinUnknow_Conneg(self):
        result = self.__generic(constructQuery, "foo", GET, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_DESCRIBE_CONSTRUCT_POSSIBLE], ct
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    # Asking for an unknown return format for CONSTRUCT queryType (XML is sent)
    # For a CONSTRUCT query type, the default return mimetype (if Accept: */* is sent) is application/rdf+xml
    def testConstructByPOSTinUnknow(self):
        result = self.__generic(constructQuery, "bar", POST)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_DESCRIBE_CONSTRUCT_POSSIBLE], ct
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    # Asking for an unknown return format for CONSTRUCT queryType (XML is sent)
    # For a CONSTRUCT query type, the default return mimetype (if Accept: */* is sent) is application/rdf+xml
    def testConstructByPOSTinUnknow_Conneg(self):
        result = self.__generic(constructQuery, "bar", POST, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_DESCRIBE_CONSTRUCT_POSSIBLE], ct
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

################################################################################
################################################################################

##################
#### DESCRIBE ####
##################

    def testDescribeByGETinXML(self):
        result = self.__generic(describeQuery, XML, GET)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_XML], ct
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    def testDescribeByGETinXML_Conneg(self):
        result = self.__generic(describeQuery, XML, GET, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_XML], ct
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    def testDescribeByPOSTinXML(self):
        result = self.__generic(describeQuery, XML, POST)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_XML], ct
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    def testDescribeByPOSTinXML_Conneg(self):
        result = self.__generic(describeQuery, XML, POST, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_XML], ct
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    # rdf+xml is not a valid alias
    @unittest.skip("4store does not support receiving unexpected output values (rdf+xml is not a valid alias)")
    def testDescribeByGETinRDFXML(self):
        result = self.__generic(describeQuery, RDFXML, GET)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_XML], ct
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    # rdf+xml is not a valid alias
    def testDescribeByGETinRDFXML_Conneg(self):
        result = self.__generic(describeQuery, RDFXML, GET, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_XML], ct
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    # rdf+xml is not a valid alias
    def testDescribeByPOSTinRDFXML(self):
        result = self.__generic(describeQuery, RDFXML, POST)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_XML], ct
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    # rdf+xml is not a valid alias
    def testDescribeByPOSTinRDFXML_Conneg(self):
        result = self.__generic(describeQuery, RDFXML, POST, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_XML], ct
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    # turtle is not a valid alias ('text' is the one used)
    @unittest.skip("4store does not support receiving unexpected output values (turtle is not a valid alias)")
    def testDescribeByGETinTURTLE(self):
        result = self.__generic(describeQuery, TURTLE, GET)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_TURTLE], ct
        results = result.convert()
        self.assertEqual(type(results), bytes)

    # turtle is not a valid alias ('text' is the one used)
    def testDescribeByGETinTURTLE_Conneg(self):
        result = self.__generic(describeQuery, TURTLE, GET, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_TURTLE], ct
        results = result.convert()
        self.assertEqual(type(results), bytes)

    # turtle is not a valid alias ('text' is the one used)
    def testDescribeByPOSTinTURTLE(self):
        result = self.__generic(describeQuery, TURTLE, POST)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_TURTLE], ct
        results = result.convert()
        self.assertEqual(type(results), bytes)

    # turtle is not a valid alias ('text' is the one used)
    def testDescribeByPOSTinTURTLE_Conneg(self):
        result = self.__generic(describeQuery, TURTLE, POST, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_TURTLE], ct
        results = result.convert()
        self.assertEqual(type(results), bytes)

    @unittest.skip("4store does not support receiving unexpected output values (n3 is not a valid alias)")
    def testDescribeByGETinN3(self):
        result = self.__generic(describeQuery, N3, GET)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_N3], ct
        results = result.convert()
        self.assertEqual(type(results), bytes)

    # Returns text/turtle
    def testDescribeByGETinN3_Conneg(self):
        result = self.__generic(describeQuery, N3, GET, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_N3], ct
        results = result.convert()
        self.assertEqual(type(results), bytes)

    def testDescribeByPOSTinN3(self):
        result = self.__generic(describeQuery, N3, POST)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_N3], ct
        results = result.convert()
        self.assertEqual(type(results), bytes)

    # Returns text/turtle
    def testDescribeByPOSTinN3_Conneg(self):
        result = self.__generic(describeQuery, N3, POST, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_N3], ct
        results = result.convert()
        self.assertEqual(type(results), bytes)

    @unittest.skip("JSON-LD is not currently supported")
    def testDescribeByGETinJSONLD(self):
        result = self.__generic(describeQuery, JSONLD, GET)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_JSONLD], ct
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    @unittest.skip("JSON-LD is not currently supported")
    def testDescribeByGETinJSONLD_Conneg(self):
        result = self.__generic(describeQuery, JSONLD, GET, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_JSONLD], ct
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    @unittest.skip("JSON-LD is not currently supported")
    def testDescribeByPOSTinJSONLD(self):
        result = self.__generic(describeQuery, JSONLD, POST)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_JSONLD], ct
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    @unittest.skip("JSON-LD is not currently supported")
    def testDescribeByPOSTinJSONLD_Conneg(self):
        result = self.__generic(describeQuery, JSONLD, POST, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _RDF_JSONLD], ct
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    # Asking for an unexpected return format for DESCRIBE queryType.
    # For a DESCRIBE query type, the default return mimetype (if Accept: */* is sent) is application/rdf+xml
    @unittest.skip("4store returns text/csv instead of the expected default application/rdf+xml. AND the content of the response is a Turtle document. It MUST return an RDF graph [RDF-CONCEPTS] serialized, for example, in the RDF/XML syntax [RDF-XML], or an equivalent RDF graph serialization, for SPARQL Query forms DESCRIBE and CONSTRUCT). See http://www.w3.org/TR/sparql11-protocol/#query-success")
    def testDescribeByGETinCSV_Unexpected(self):
        result = self.__generic(describeQuery, CSV, GET)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_DESCRIBE_CONSTRUCT_POSSIBLE]
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    # Asking for an unexpected return format for DESCRIBE queryType.
    # For a DESCRIBE query type, the default return mimetype (if Accept: */* is sent) is application/rdf+xml
    def testDescribeByGETinCSV_Unexpected_Conneg(self):
        result = self.__generic(describeQuery, CSV, GET, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_DESCRIBE_CONSTRUCT_POSSIBLE]
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    # Asking for an unexpected return format for DESCRIBE queryType.
    # For a DESCRIBE query type, the default return mimetype (if Accept: */* is sent) is application/rdf+xml
    def testDescribeByPOSTinCSV_Unexpected(self):
        result = self.__generic(describeQuery, CSV, POST)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_DESCRIBE_CONSTRUCT_POSSIBLE]
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    # Asking for an unexpected return format for DESCRIBE queryType.
    # For a DESCRIBE query type, the default return mimetype (if Accept: */* is sent) is application/rdf+xml
    def testDescribeByPOSTinCSV_Unexpected_Conneg(self):
        result = self.__generic(describeQuery, CSV, POST, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_DESCRIBE_CONSTRUCT_POSSIBLE]
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    # Asking for an unexpected return format for DESCRIBE queryType.
    # For a DESCRIBE query type, the default return mimetype (if Accept: */* is sent) is application/rdf+xml
    @unittest.skip("4store returns application/sparql-results+json instead of the expected default application/rdf+xml. It MUST return an RDF graph [RDF-CONCEPTS] serialized, for example, in the RDF/XML syntax [RDF-XML], or an equivalent RDF graph serialization, for SPARQL Query forms DESCRIBE and CONSTRUCT). See http://www.w3.org/TR/sparql11-protocol/#query-success")
    def testDescribeByGETinJSON_Unexpected(self):
        result = self.__generic(describeQuery, JSON, GET)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_DESCRIBE_CONSTRUCT_POSSIBLE]
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    # Asking for an unexpected return format for DESCRIBE queryType.
    # For a DESCRIBE query type, the default return mimetype (if Accept: */* is sent) is application/rdf+xml
    def testDescribeByGETinJSON_Unexpected_Conneg(self):
        result = self.__generic(describeQuery, JSON, GET, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_DESCRIBE_CONSTRUCT_POSSIBLE]
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    # Asking for an unexpected return format for DESCRIBE queryType.
    # For a DESCRIBE query type, the default return mimetype (if Accept: */* is sent) is application/rdf+xml
    def testDescribeByPOSTinJSON_Unexpected(self):
        result = self.__generic(describeQuery, JSON, POST)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_DESCRIBE_CONSTRUCT_POSSIBLE]
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    # Asking for an unexpected return format for DESCRIBE queryType.
    # For a DESCRIBE query type, the default return mimetype (if Accept: */* is sent) is application/rdf+xml
    def testDescribeByPOSTinJSON_Unexpected_Conneg(self):
        result = self.__generic(describeQuery, JSON, POST, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_DESCRIBE_CONSTRUCT_POSSIBLE]
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    # Asking for an unknown return format for DESCRIBE queryType (XML is sent)
    # For a DESCRIBE query type, the default return mimetype (if Accept: */* is sent) is application/rdf+xml
    def testDescribeByGETinUnknow(self):
        result = self.__generic(describeQuery, "foo", GET)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_DESCRIBE_CONSTRUCT_POSSIBLE], ct
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    # Asking for an unknown return format for DESCRIBE queryType (XML is sent)
    # For a DESCRIBE query type, the default return mimetype (if Accept: */* is sent) is application/rdf+xml
    def testDescribeByGETinUnknow_Conneg(self):
        result = self.__generic(describeQuery, "foo", GET, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_DESCRIBE_CONSTRUCT_POSSIBLE], ct
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    # Asking for an unknown return format for DESCRIBE queryType (XML is sent)
    # For a DESCRIBE query type, the default return mimetype (if Accept: */* is sent) is application/rdf+xml
    def testDescribeByPOSTinUnknow(self):
        result = self.__generic(describeQuery, "bar", POST)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_DESCRIBE_CONSTRUCT_POSSIBLE], ct
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

    # Asking for an unknown return format for DESCRIBE queryType (XML is sent)
    # For a DESCRIBE query type, the default return mimetype (if Accept: */* is sent) is application/rdf+xml
    def testDescribeByPOSTinUnknow_Conneg(self):
        result = self.__generic(describeQuery, "bar", POST, onlyConneg=True)
        ct = result.info()["content-type"]
        assert True in [one in ct for one in _SPARQL_DESCRIBE_CONSTRUCT_POSSIBLE], ct
        results = result.convert()
        self.assertEqual(type(results), ConjunctiveGraph)

################################################################################
################################################################################

    def testQueryBadFormed(self):
        self.assertRaises(QueryBadFormed, self.__generic, queryBadFormed, XML, GET)

    def testQueryManyPrefixes(self):
        result = self.__generic(queryManyPrefixes, XML, GET)

    def testQueryDuplicatedPrefix(self):
        result = self.__generic(queryDuplicatedPrefix, XML, GET)

    def testKeepAlive(self):
        sparql = SPARQLWrapper(endpoint)
        sparql.setQuery('SELECT * WHERE {?s ?p ?o} LIMIT 10')
        sparql.setReturnFormat(JSON)
        sparql.setMethod(GET)
        sparql.setUseKeepAlive()

        sparql.query()
        sparql.query()

    @unittest.skip('Store 4. parser error: Failed to decode SPARQL ID "dbpedia:Victoria\". See #94')
    def testQueryWithComma_1(self):
        result = self.__generic(queryWithCommaInCurie_1, XML, GET)

    @unittest.skip('Store 4. parser error: Failed to decode SPARQL ID "dbpedia:Category\". See #94')
    def testQueryWithComma_2(self):
        result = self.__generic(queryWithCommaInCurie_2, XML, POST)

    def testQueryWithComma_3(self):
        result = self.__generic(queryWithCommaInUri, XML, GET)

if __name__ == "__main__":
    unittest.main()
