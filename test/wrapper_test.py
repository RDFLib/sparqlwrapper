# -*- coding: utf-8 -*-
import inspect
import os
import sys

import logging

import unittest
import urllib.request, urllib.error, urllib.parse
from urllib.parse import urlparse, parse_qsl, parse_qs
from urllib.request import Request
import time

logging.basicConfig()

# prefer local copy to the one which is installed
# hack from http://stackoverflow.com/a/6098238/280539
_top_level_path = os.path.realpath(os.path.abspath(os.path.join(
    os.path.split(inspect.getfile(inspect.currentframe()))[0],
    ".."
)))
if _top_level_path not in sys.path:
    sys.path.insert(0, _top_level_path)
# end of hack

# we don't want to let Wrapper do real web-requests. so, we are…
# constructing a simple Mock!
from urllib.error import HTTPError

from io import StringIO
import warnings
warnings.simplefilter("always")

import SPARQLWrapper.Wrapper as _victim

from SPARQLWrapper import SPARQLWrapper
from SPARQLWrapper import XML, GET, POST, JSON, JSONLD, N3, TURTLE, RDF, SELECT, INSERT, RDFXML, CSV, TSV
from SPARQLWrapper import URLENCODED, POSTDIRECTLY
from SPARQLWrapper import BASIC, DIGEST
from SPARQLWrapper.Wrapper import QueryResult, QueryBadFormed, EndPointNotFound, EndPointInternalError, Unauthorized, URITooLong


class FakeResult(object):
    def __init__(self, request):
        self.request = request


def urlopener(request):
    return FakeResult(request)


def urlopener_error_generator(code):
    def urlopener_error(request):
        raise HTTPError(request.get_full_url, code, '', {}, StringIO(''))

    return urlopener_error


def urlopener_check_data_encoding(request):
    if isinstance(request.data, str):
        raise TypeError
# DONE

class SPARQLWrapper_Test(unittest.TestCase):

    @staticmethod
    def _get_request(wrapper):
        return wrapper.query().response.request  # possible due to mock above

    @staticmethod
    def _get_parameters_from_request(request):
        if request.get_method() == 'GET':
            pieces_str = urlparse(request.get_full_url()).query
        else:
            pieces_str = request.data.decode('ascii')

        return parse_qs(pieces_str)

    @staticmethod
    def _get_request_parameters(wrapper):
        request = SPARQLWrapper_Test._get_request(wrapper)
        parameters = SPARQLWrapper_Test._get_parameters_from_request(request)

        return parameters

    @staticmethod
    def _get_request_parameters_as_bytes(wrapper):
        request = SPARQLWrapper_Test._get_request(wrapper)
        parameters = SPARQLWrapper_Test._get_parameters_from_request(request)

        result = {}
        for k, vs in parameters.items():
            result[k] = [v.encode('utf-8') for v in vs]
        return result

    @classmethod
    def setUpClass(cls):
        urllib.request._opener = None # clear value. Due to the order of test execution, the value of urllib.request._opener contains, for instance, keepalive.keepalive.HTTPHandler

    def setUp(self):
        self.wrapper = SPARQLWrapper(endpoint='http://example.org/sparql')
        _victim.urlopener = urlopener

    def testConstructor(self):
        try:
            SPARQLWrapper()
            self.fail("SPARQLWrapper constructor should fail without arguments")
        except TypeError:
            pass

        wrapper = SPARQLWrapper(endpoint='http://example.org/sparql/')

        self.assertEqual(XML, wrapper.returnFormat, 'default return format is XML')
        self.assertTrue(
            wrapper.agent.startswith('sparqlwrapper'),
            'default user-agent should start with "sparqlwrapper"'
        )

        wrapper = SPARQLWrapper(endpoint='http://example.org/sparql/', returnFormat='wrongformat')
        self.assertEqual(XML, wrapper.returnFormat, 'default return format is XML')

        wrapper = SPARQLWrapper(endpoint='http://example.org/sparql/', defaultGraph='http://example.org/default')
        parameters = self._get_request_parameters(wrapper)
        self.assertEqual(
            ['http://example.org/default'],
            parameters.get('default-graph-uri'),
            'default graph is set'
        )

    def testReset(self):
        self.wrapper.setMethod(POST)
        self.wrapper.setQuery('CONSTRUCT WHERE {?a ?b ?c}')
        self.wrapper.setReturnFormat(N3)
        self.wrapper.addParameter('a', 'b')
        self.wrapper.setOnlyConneg(True)

        request = self._get_request(self.wrapper)
        parameters = self._get_parameters_from_request(request)
        onlyConneg = self.wrapper.onlyConneg

        self.assertEqual('POST', request.get_method())
        self.assertTrue(parameters['query'][0].startswith('CONSTRUCT'))
        self.assertTrue('rdf+n3' in request.get_header('Accept'))
        self.assertTrue('a' in parameters)
        self.assertTrue(onlyConneg)

        self.wrapper.resetQuery()

        request = self._get_request(self.wrapper)
        parameters = self._get_parameters_from_request(request)
        onlyConneg = self.wrapper.onlyConneg

        self.assertEqual('GET', request.get_method())
        self.assertTrue(parameters['query'][0].startswith('SELECT'))
        self.assertFalse('rdf+n3' in request.get_header('Accept'))
        self.assertTrue('sparql-results+xml' in request.get_header('Accept'))
        self.assertFalse('a' in parameters)
        self.assertFalse('a' in parameters)
        self.assertTrue(onlyConneg)

    def testSetReturnFormat(self):
        with warnings.catch_warnings(record=True) as w:
            self.wrapper.setReturnFormat('nonexistent format')
            self.assertEqual(1, len(w), "Warning due to non expected format")

        self.assertEqual(XML, self.wrapper.query().requestedFormat)

        self.wrapper.setReturnFormat(JSON)
        self.assertEqual(JSON, self.wrapper.query().requestedFormat)

        try:
            import rdflib_jsonld
            self.wrapper.setReturnFormat(JSONLD)
            self.assertEqual(JSONLD, self.wrapper.query().requestedFormat)
        except ImportError:
            self.assertRaises(ValueError, self.wrapper.setReturnFormat, JSONLD)

    def testsSupportsReturnFormat(self):
        self.assertTrue(self.wrapper.supportsReturnFormat(XML))
        self.assertTrue(self.wrapper.supportsReturnFormat(JSON))
        self.assertTrue(self.wrapper.supportsReturnFormat(TURTLE))
        self.assertTrue(self.wrapper.supportsReturnFormat(N3))
        self.assertTrue(self.wrapper.supportsReturnFormat(RDF))
        self.assertTrue(self.wrapper.supportsReturnFormat(RDFXML))
        self.assertTrue(self.wrapper.supportsReturnFormat(CSV))
        self.assertTrue(self.wrapper.supportsReturnFormat(TSV))
        self.assertFalse(self.wrapper.supportsReturnFormat('nonexistent format'))

        try:
            import rdflib_jsonld
            self.assertTrue(self.wrapper.supportsReturnFormat(JSONLD))
        except ImportError:
            self.assertFalse(self.wrapper.supportsReturnFormat(JSONLD))


    def testAddParameter(self):
        self.assertFalse(self.wrapper.addParameter('query', 'dummy'))
        self.assertTrue(self.wrapper.addParameter('param1', 'value1'))
        self.assertTrue(self.wrapper.addParameter('param1', 'value2'))
        self.assertTrue(self.wrapper.addParameter('param2', 'value2'))

        pieces = self._get_request_parameters(self.wrapper)

        self.assertTrue('param1' in pieces)
        self.assertEqual(['value1', 'value2'], pieces['param1'])
        self.assertTrue('param2' in pieces)
        self.assertEqual(['value2'], pieces['param2'])
        self.assertNotEqual(['dummy'], 'query')

    def testSetCredentials(self):
        request = self._get_request(self.wrapper)
        self.assertFalse(request.has_header('Authorization'))

        self.wrapper.setCredentials('login', 'password')
        request = self._get_request(self.wrapper)
        self.assertTrue(request.has_header('Authorization'))

        # expected header for login:password
        # should succeed for python 3 since pull request #72
        self.assertEqual("Basic bG9naW46cGFzc3dvcmQ=", request.get_header('Authorization'))

    def testAddCustomHttpHeader(self):
        request = self._get_request(self.wrapper)
        self.assertFalse(request.has_header('Foo'))

        # Add new header field name
        self.wrapper.addCustomHttpHeader('Foo', 'bar')
        request = self._get_request(self.wrapper)
        self.assertTrue(request.has_header('Foo'))
        self.assertEqual("bar", request.get_header('Foo'))

        # Override a new field name
        self.wrapper.addCustomHttpHeader('Foo', 'bar')
        request = self._get_request(self.wrapper)
        self.assertTrue(request.has_header('Foo'))
        self.assertEqual("bar", request.get_header('Foo'))
        self.wrapper.addCustomHttpHeader('Foo', 'bar_2')
        request = self._get_request(self.wrapper)
        self.assertTrue(request.has_header('Foo'))
        self.assertEqual("bar_2", request.get_header('Foo'))

        # Override header field name
        self.wrapper.addCustomHttpHeader('User-agent', 'Another UA')
        request = self._get_request(self.wrapper)
        self.assertEqual("Another UA", request.get_header('User-agent'))

    def testClearCustomHttpHeader(self):
        request = self._get_request(self.wrapper)
        self.assertFalse(request.has_header('Foo'))

        # Add new header field name
        self.wrapper.addCustomHttpHeader('Foo_1', 'bar_1')
        self.wrapper.addCustomHttpHeader('Foo_2', 'bar_2')
        self.wrapper.addCustomHttpHeader('Foo_3', 'bar_3')


        self.assertFalse(self.wrapper.clearCustomHttpHeader('Foo_4'))
        self.assertTrue(self.wrapper.clearCustomHttpHeader('Foo_3'))

        customHttpHeaders = self.wrapper.customHttpHeaders

        self.assertTrue('Foo_1' in customHttpHeaders)
        self.assertTrue('Foo_2' in customHttpHeaders)
        self.assertEqual('bar_1', customHttpHeaders['Foo_1'])
        self.assertEqual('bar_2', customHttpHeaders['Foo_2'])

        self.assertFalse(self.wrapper.clearCustomHttpHeader('Foo_3'), 'already cleaned')


    def testSetHTTPAuth(self):
        self.assertRaises(TypeError, self.wrapper.setHTTPAuth, 123)
        self.wrapper.setCredentials('login', 'password')
        request = self._get_request(self.wrapper)
        self.assertTrue(request.has_header('Authorization'))
        self.assertIsNone(urllib.request._opener)

        self.wrapper.setHTTPAuth(DIGEST)
        self.assertIsNone(urllib.request._opener)
        request = self._get_request(self.wrapper)
        self.assertFalse(request.has_header('Authorization'))
        self.assertEqual(self.wrapper.http_auth, DIGEST)
        self.assertIsInstance(urllib.request._opener, urllib.request.OpenerDirector)

        self.wrapper.setHTTPAuth(DIGEST)
        self.wrapper.setCredentials('login', 'password')
        request = self._get_request(self.wrapper)
        self.assertEqual(self.wrapper.http_auth, DIGEST)
        self.assertEqual(self.wrapper.user, "login")
        self.assertEqual(self.wrapper.passwd, "password")
        self.assertEqual(self.wrapper.realm, "SPARQL")
        self.assertNotEqual(self.wrapper.realm, "SPARQL Endpoint")

        self.wrapper.setHTTPAuth(DIGEST)
        self.wrapper.setCredentials('login', 'password', realm="SPARQL Endpoint")
        request = self._get_request(self.wrapper)
        self.assertEqual(self.wrapper.http_auth, DIGEST)
        self.assertEqual(self.wrapper.user, "login")
        self.assertEqual(self.wrapper.passwd, "password")
        self.assertEqual(self.wrapper.realm, "SPARQL Endpoint")
        self.assertNotEqual(self.wrapper.realm, "SPARQL")

        self.assertRaises(ValueError, self.wrapper.setHTTPAuth, 'OAuth')

        self.wrapper.http_auth = "OAuth"
        self.assertRaises(NotImplementedError, self._get_request, self.wrapper)

    def testSetQuery(self):
        self.wrapper.setQuery('PREFIX example: <http://example.org/INSERT/> SELECT * WHERE {?s ?p ?v}')
        self.assertEqual(SELECT, self.wrapper.queryType)

        self.wrapper.setQuery('PREFIX e: <http://example.org/> INSERT {e:a e:b e:c}')
        self.assertEqual(INSERT, self.wrapper.queryType)

        self.wrapper.setQuery("""#CONSTRUCT {?s ?p ?o}
                                   SELECT ?s ?p ?o
                                   WHERE {?s ?p ?o}""")
        self.assertEqual(SELECT, self.wrapper.queryType)

        with warnings.catch_warnings(record=True) as w:
            self.wrapper.setQuery('UNKNOWN {e:a e:b e:c}')
            self.assertEqual(SELECT, self.wrapper.queryType, 'unknown queries result in SELECT')

    def testSetQueryEncodingIssues(self):
        #further details from issue #35
        query = 'INSERT DATA { <urn:michel> <urn:says> "これはテストです" }'
        query_bytes = query.encode('utf-8')

        self.wrapper.setMethod(POST)
        self.wrapper.setRequestMethod(POSTDIRECTLY)

        self.wrapper.setQuery(query)
        request = self._get_request(self.wrapper)
        self.assertEqual(query_bytes, request.data)

        self.wrapper.setQuery(query_bytes)
        request = self._get_request(self.wrapper)
        self.assertEqual(query_bytes, request.data)

        self.wrapper.setRequestMethod(URLENCODED)

        self.wrapper.setQuery(query)
        parameters = self._get_request_parameters_as_bytes(self.wrapper)
        self.assertEqual(query_bytes, parameters['update'][0])

        self.wrapper.setQuery(query_bytes)
        parameters = self._get_request_parameters_as_bytes(self.wrapper)
        self.assertEqual(query_bytes, parameters['update'][0])

        try:
            self.wrapper.setQuery(query.encode('sjis'))
            self.fail()
        except UnicodeDecodeError:
            self.assertTrue(True)

        try:
            self.wrapper.setQuery({'foo': 'bar'})
            self.fail()
        except TypeError:
            self.assertTrue(True)

    def testSetTimeout(self):
        self.wrapper.setTimeout(10)
        self.assertEqual(10, self.wrapper.timeout)

        self.wrapper.resetQuery()
        self.assertEqual(None, self.wrapper.timeout)

    def testClearParameter(self):
        self.wrapper.addParameter('param1', 'value1')
        self.wrapper.addParameter('param1', 'value2')
        self.wrapper.addParameter('param2', 'value2')

        self.assertFalse(self.wrapper.clearParameter('query'))
        self.assertTrue(self.wrapper.clearParameter('param1'))

        pieces = self._get_request_parameters(self.wrapper)

        self.assertFalse('param1' in pieces)
        self.assertTrue('param2' in pieces)
        self.assertEqual(['value2'], pieces['param2'])

        self.assertFalse(self.wrapper.clearParameter('param1'), 'already cleaned')

    def testSetMethod(self):
        self.wrapper.setMethod(POST)
        request = self._get_request(self.wrapper)

        self.assertEqual("POST", request.get_method())

        self.wrapper.setMethod(GET)
        request = self._get_request(self.wrapper)

        self.assertEqual("GET", request.get_method())

    def testSetRequestMethod(self):
        self.assertEqual(URLENCODED, self.wrapper.requestMethod)

        self.wrapper.setRequestMethod(POSTDIRECTLY)
        self.assertEqual(POSTDIRECTLY, self.wrapper.requestMethod)

    def testIsSparqlUpdateRequest(self):
        self.wrapper.setQuery('DELETE WHERE {?s ?p ?o}')
        self.assertTrue(self.wrapper.isSparqlUpdateRequest())

        self.wrapper.setQuery('DELETE DATA { <urn:john> <urn:likes> <urn:surfing> }')
        self.assertTrue(self.wrapper.isSparqlUpdateRequest())

        self.wrapper.setQuery("""
        PREFIX example: <http://example.org/SELECT/>
        BASE <http://example.org/SELECT>
        DELETE WHERE {?s ?p ?o}
        """)
        self.assertTrue(self.wrapper.isSparqlUpdateRequest())

        self.wrapper.setQuery('WITH <urn:graph> DELETE DATA { <urn:john> <urn:likes> <urn:surfing> }')
        self.assertTrue(self.wrapper.isSparqlUpdateRequest())

        self.wrapper.setQuery('INSERT DATA { <urn:john> <urn:likes> <urn:surfing> }')
        self.assertTrue(self.wrapper.isSparqlUpdateRequest())

        self.wrapper.setQuery('WITH <urn:graph> INSERT DATA { <urn:john> <urn:likes> <urn:surfing> }')
        self.assertTrue(self.wrapper.isSparqlUpdateRequest())

        self.wrapper.setQuery('CREATE GRAPH <urn:graph>')
        self.assertTrue(self.wrapper.isSparqlUpdateRequest())

        self.wrapper.setQuery('CLEAR GRAPH <urn:graph>')
        self.assertTrue(self.wrapper.isSparqlUpdateRequest())

        self.wrapper.setQuery('DROP GRAPH <urn:graph>')
        self.assertTrue(self.wrapper.isSparqlUpdateRequest())

        self.wrapper.setQuery('MOVE GRAPH <urn:graph1> TO GRAPH <urn:graph2>')
        self.assertTrue(self.wrapper.isSparqlUpdateRequest())

        self.wrapper.setQuery('LOAD <http://localhost/file.rdf> INTO GRAPH <urn:graph>')
        self.assertTrue(self.wrapper.isSparqlUpdateRequest())

        self.wrapper.setQuery('COPY <urn:graph1> TO GRAPH <urn:graph2>')
        self.assertTrue(self.wrapper.isSparqlUpdateRequest())

        self.wrapper.setQuery('ADD <urn:graph1> TO GRAPH <urn:graph2>')
        self.assertTrue(self.wrapper.isSparqlUpdateRequest())

    def testIsSparqlQueryRequest(self):
        self.wrapper.setQuery('SELECT * WHERE {?s ?p ?o}')
        self.assertTrue(self.wrapper.isSparqlQueryRequest())

        self.wrapper.setQuery("""
        PREFIX example: <http://example.org/DELETE/>
        BASE <http://example.org/MODIFY>
        ASK WHERE {?s ?p ?o}
        """)
        self.assertTrue(self.wrapper.isSparqlQueryRequest())
        self.assertFalse(self.wrapper.isSparqlUpdateRequest())

    def testQuery(self):
        qr = self.wrapper.query()
        self.assertTrue(isinstance(qr, QueryResult))

        request = qr.response.request  # possible due to mock above
        self.assertTrue(isinstance(request, Request))

        parameters = self._get_parameters_from_request(request)
        self.assertTrue('query' in parameters)
        self.assertTrue('update' not in parameters)

        self.wrapper.setMethod(POST)
        self.wrapper.setQuery('PREFIX e: <http://example.org/> INSERT {e:a e:b e:c}')
        parameters = self._get_request_parameters(self.wrapper)
        self.assertTrue('update' in parameters)
        self.assertTrue('query' not in parameters)
        #_returnFormatSetting = ["format", "output", "results"]
        self.assertTrue('format' not in parameters)
        self.assertTrue('output' not in parameters)
        self.assertTrue('results' not in parameters)

        _victim.urlopener = urlopener_error_generator(400)
        try:
            self.wrapper.query()
            self.fail('should have raised exception')
        except QueryBadFormed as e:
            #  TODO: check exception-format
            pass
        except:
            self.fail('got wrong exception')

        _victim.urlopener = urlopener_error_generator(401)
        try:
            self.wrapper.query()
            self.fail('should have raised exception')
        except Unauthorized as e:
            #  TODO: check exception-format
            pass
        except:
            self.fail('got wrong exception')

        _victim.urlopener = urlopener_error_generator(404)
        try:
            self.wrapper.query()
            self.fail('should have raised exception')
        except EndPointNotFound as e:
            #  TODO: check exception-format
            pass
        except:
            self.fail('got wrong exception')

        _victim.urlopener = urlopener_error_generator(414)
        try:
            self.wrapper.query()
            self.fail('should have raised exception')
        except URITooLong as e:
            #  TODO: check exception-format
            pass
        except:
            self.fail('got wrong exception')

        _victim.urlopener = urlopener_error_generator(500)
        try:
            self.wrapper.query()
            self.fail('should have raised exception')
        except EndPointInternalError as e:
            #  TODO: check exception-format
            pass
        except:
            self.fail('got wrong exception')

        _victim.urlopener = urlopener_error_generator(999)
        try:
            self.wrapper.query()
            self.fail('should have raised exception')
        except HTTPError as e:
            #  TODO: check exception-format
            pass
        except:
            self.fail('got wrong exception')

    def testQueryEncoding(self):
        query = 'INSERT DATA { <urn:michel> <urn:says> "é" }'

        wrapper = SPARQLWrapper('http://example.com:3030/example')
        wrapper.setMethod(POST)
        wrapper.setRequestMethod(URLENCODED)
        wrapper.setQuery(query)

        _victim.urlopener = urlopener_check_data_encoding
        wrapper.query()

    def testQueryAndConvert(self):
        _oldQueryResult = _victim.QueryResult

        class FakeQueryResult(object):
            def __init__(self, result):
                pass

            def convert(self):
                return True

        try:
            _victim.QueryResult = FakeQueryResult
            result = self.wrapper.queryAndConvert()
            self.assertEqual(True, result)
        finally:
            _victim.QueryResult = _oldQueryResult

    def testComments(self):
        # see issue #32
        self.wrapper.setQuery("""
# this is a comment
select * where { ?s ?p ?o }
""")
        self.assertTrue(self.wrapper.isSparqlQueryRequest())

    def testHashInPrefixes(self):
        # see issue #77
        self.wrapper.setQuery("""
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
select * where { ?s ?p ?o }
""")
        self.assertTrue(self.wrapper.isSparqlQueryRequest())

    def testHashInPrefixComplex(self):
        # see issue #77
        self.wrapper.setQuery("""
PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
PREFIX weather: <http://hal.zamia.org/weather/>
PREFIX dbo:     <http://dbpedia.org/ontology/> 
PREFIX dbr:     <http://dbpedia.org/resource/> 
PREFIX dbp:     <http://dbpedia.org/property/> 
PREFIX xml:     <http://www.w3.org/XML/1998/namespace> 
PREFIX xsd:     <http://www.w3.org/2001/XMLSchema#> 

SELECT DISTINCT ?location ?cityid ?timezone ?label
WHERE {
  ?location weather:cityid ?cityid .
  ?location weather:timezone ?timezone .
  ?location rdfs:label ?label .
}
""")
        self.assertTrue(self.wrapper.isSparqlQueryRequest())

    def testHashWithNoComments(self):
        # see issue #77
        query = """
PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT *
WHERE {
  ?s ?p ?o .
}
"""
        parsed_query = self.wrapper._cleanComments(query)
        self.assertEqual(query, parsed_query)

    def testCommentBeginningLine(self):
        # see issue #77
        query = """
PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
# a comment
SELECT *
WHERE {
  ?s ?p ?o .
}
"""
        expected_parsed_query = """
PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT *
WHERE {
  ?s ?p ?o .
}
"""
        parsed_query = self.wrapper._cleanComments(query)
        self.assertEqual(expected_parsed_query, parsed_query)

    def testCommentEmtpyLine(self):
        # see issue #77
        query = """
PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
     # a comment
SELECT *
WHERE {
  ?s ?p ?o .
}
"""
        expected_parsed_query = """
PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT *
WHERE {
  ?s ?p ?o .
}
"""
        parsed_query = self.wrapper._cleanComments(query)
        self.assertEqual(expected_parsed_query, parsed_query)

    def testCommentsFirstLine(self):
        # see issue #77
        query = """#CONSTRUCT {?s ?p ?o}
                                   SELECT ?s ?p ?o
                                   WHERE {?s ?p ?o}"""
        expected_parsed_query = """

                                   SELECT ?s ?p ?o
                                   WHERE {?s ?p ?o}"""

        parsed_query = self.wrapper._cleanComments(query)
        self.assertEqual(expected_parsed_query, parsed_query)

    @unittest.skip("issue #80")
    def testCommentAfterStatements(self):
        # see issue #77
        query = """
PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT *
WHERE {     # this is the where condition
  ?s ?p ?o .
}
"""
        expected_parsed_query = """
PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT *
WHERE {
  ?s ?p ?o .
}
"""
        parsed_query = self.wrapper._cleanComments(query)
        self.assertEqual(expected_parsed_query, parsed_query)

    def testSingleLineQueryLine(self):
        # see issue #74
        query = "prefix whatever: <http://example.org/blah#> ASK { ?s ?p ?o }"
        parsed_query = self.wrapper._cleanComments(query)
        self.assertEqual(query, parsed_query)

        self.wrapper.setQuery(query)
        self.assertTrue(self.wrapper.isSparqlQueryRequest())

    def testOnlyConneg(self):
        # see issue #82
        query = "prefix whatever: <http://example.org/blah#> ASK { ?s ?p ?o }"
        self.wrapper.setOnlyConneg(False)
        self.wrapper.setQuery(query)
        request = self._get_request(self.wrapper)
        request_params = dict(parse_qsl(urlparse(request.get_full_url()).query))
        for returnFormatSetting in ["format", "output", "results"]: # Obviously _returnFormatSetting is not accessible from SPARQLWrapper, so we copy&paste the possible values
            self.assertTrue(returnFormatSetting in request_params, "URL parameter '%s' was not sent, and it was expected" %returnFormatSetting)

        #ONLY Content Negotiation
        self.wrapper.resetQuery()
        self.wrapper.setOnlyConneg(True)
        self.wrapper.setQuery(query)
        request = self._get_request(self.wrapper)
        request_params = dict(parse_qsl(urlparse(request.get_full_url()).query))
        for returnFormatSetting in ["format", "output", "results"]: # Obviously _returnFormatSetting is not accessible from SPARQLWrapper, so we copy&paste the possible values
            self.assertFalse(returnFormatSetting in request_params, "URL parameter '%s' was sent, and it was not expected (only Content Negotiation)" %returnFormatSetting)


class QueryResult_Test(unittest.TestCase):

    def testConstructor(self):
        qr = QueryResult('result')
        self.assertEqual('result', qr.response)
        try:
            format = qr.requestedFormat
            self.fail('format is not supposed to be set')
        except:
            pass

        qr = QueryResult(('result', 'format'))
        self.assertEqual('result', qr.response)
        self.assertEqual('format', qr.requestedFormat)

    def testProxyingToResponse(self):
        class FakeResponse(object):
            def __init__(self):
                self.geturl_called = False
                self.info_called = False
                self.iter_called = False
                self.next_called = False

            def geturl(self):
                self.geturl_called = True

            def info(self):
                self.info_called = True
                return {"key": "value"}

            def __iter__(self):
                self.iter_called = True

            def __next__(self):
                self.next_called = True

        result = FakeResponse()

        qr = QueryResult(result)
        qr.geturl()
        qr.__iter__()
        next(qr)

        self.assertTrue(result.geturl_called)
        self.assertTrue(result.iter_called)
        self.assertTrue(result.next_called)

        info = qr.info()
        self.assertTrue(result.info_called)
        self.assertEqual('value', info.__getitem__('KEY'), 'keys should be case-insensitive')

    def testConvert(self):
        class FakeResponse(object):
            def __init__(self, content_type):
                self.content_type = content_type

            def info(self):
                return {"Content-type": self.content_type}

            def read(self, len):
                return ''

        def _mime_vs_type(mime, requested_type):
            """
            :param mime: mimetype/Content-Type of the response
            :param requested_type: requested mimetype (alias)
            :return: number of warnings produced by combo
            """
            with warnings.catch_warnings(record=True) as w:
                qr = QueryResult((FakeResponse(mime), requested_type))

                try:
                    qr.convert()
                except:
                    pass

                return len(w)

        # In the cases of "application/ld+json" and "application/rdf+xml", the
        # RDFLib raised a warning because the manually created QueryResult has no real
        # response value (implemented a fake read).
        # "WARNING:rdflib.term:  does not look like a valid URI, trying to serialize this will break."
        self.assertEqual(0, _mime_vs_type("application/sparql-results+xml", XML))
        self.assertEqual(0, _mime_vs_type("application/sparql-results+json", JSON))
        self.assertEqual(0, _mime_vs_type("text/n3", N3))
        self.assertEqual(0, _mime_vs_type("text/turtle", TURTLE))
        self.assertEqual(0, _mime_vs_type("application/turtle", TURTLE))
        self.assertEqual(0, _mime_vs_type("application/ld+json", JSON)) # Warning
        self.assertEqual(0, _mime_vs_type("application/ld+json", JSONLD)) # Warning
        self.assertEqual(0, _mime_vs_type("application/rdf+xml", XML)) # Warning
        self.assertEqual(0, _mime_vs_type("application/rdf+xml", RDF)) # Warning
        self.assertEqual(0, _mime_vs_type("application/rdf+xml", RDFXML)) # Warning
        self.assertEqual(0, _mime_vs_type("text/csv", CSV))
        self.assertEqual(0, _mime_vs_type("text/tab-separated-values", TSV))
        self.assertEqual(0, _mime_vs_type("application/xml", XML))

        self.assertEqual(1, _mime_vs_type("application/x-foo-bar", XML), "invalid mime")

        self.assertEqual(1, _mime_vs_type("application/sparql-results+xml", N3))
        self.assertEqual(1, _mime_vs_type("application/sparql-results+json", XML))
        self.assertEqual(1, _mime_vs_type("text/n3", JSON))
        self.assertEqual(1, _mime_vs_type("text/turtle", XML))
        self.assertEqual(1, _mime_vs_type("application/ld+json", XML))  # Warning
        self.assertEqual(1, _mime_vs_type("application/ld+json", N3))  # Warning
        self.assertEqual(1, _mime_vs_type("application/rdf+xml", JSON))  # Warning
        self.assertEqual(1, _mime_vs_type("application/rdf+xml", N3))  # Warning

    def testPrint_results(self):
        """
        print_results() is only allowed for JSON return format.
        """
        class FakeResponse(object):
            def __init__(self, content_type):
                self.content_type = content_type

            def info(self):
                return {"Content-type": self.content_type}

            def read(self, len):
                return ''

        def _print_results(mime):
            """
            :param mime: mimetype/Content-Type of the response
            :return: number of warnings produced by combo
            """
            with warnings.catch_warnings(record=True) as w:
                qr = QueryResult(FakeResponse(mime))

                try:
                    qr.print_results()
                except:
                    pass

                return len(w)

        self.assertEqual(0, _print_results("application/sparql-results+json"))
        self.assertEqual(0, _print_results("application/json"))
        self.assertEqual(0, _print_results("text/javascript"))
        self.assertEqual(0, _print_results("application/javascript"))

        self.assertEqual(1, _print_results("application/sparql-results+xml"))
        self.assertEqual(1, _print_results("application/xml"))
        self.assertEqual(1, _print_results("application/rdf+xml"))

        self.assertEqual(1, _print_results("application/turtle"))
        self.assertEqual(1, _print_results("text/turtle"))

        self.assertEqual(1, _print_results("text/rdf+n3"))
        self.assertEqual(1, _print_results("application/n-triples"))
        self.assertEqual(1, _print_results("application/n3"))
        self.assertEqual(1, _print_results("text/n3"))

        self.assertEqual(1, _print_results("text/csv"))

        self.assertEqual(1, _print_results("text/tab-separated-values"))

        self.assertEqual(1, _print_results("application/ld+json"))
        self.assertEqual(1, _print_results("application/x-json+ld"))

        self.assertEqual(2, _print_results("application/x-foo-bar"))


class QueryType_Time_Test(unittest.TestCase):

    def testQueries(self):
        sparql = SPARQLWrapper("http://example.org/sparql")

        queries = []

        queries.append("""
    PREFIX a: <http://dbpedia.org/a>
    PREFIX b: <http://dbpedia.org/b>
    PREFIX c: <http://dbpedia.org/c>
    PREFIX d: <http://dbpedia.org/d>
    PREFIX e: <http://dbpedia.org/e>
    PREFIX f: <http://dbpedia.org/f>
    PREFIX g: <http://dbpedia.org/g>
    PREFIX h: <http://dbpedia.org/h>
    FROM <http://dbpedia.org>
    SELECT ?s ?p ?o WHERE {
        ?s ?p ?o.
    }""")

        queries.append("""PREFIX a: <http://dbpedia.org/a>
    PREFIX b: <http://dbpedia.org/b>
    PREFIX c: <http://dbpedia.org/c>
    PREFIX d: <http://dbpedia.org/d>
    PREFIX e: <http://dbpedia.org/e>
    PREFIX f: <http://dbpedia.org/f>
    PREFIX g: <http://dbpedia.org/g>
    PREFIX h: <http://dbpedia.org/h>
    FROM <http://dbpedia.org>
    SELECT ?s ?p ?o WHERE {
        ?s ?p ?o.
    }""")

        queries.append("""PREFIX a: <http://dbpedia.org/a>
PREFIX b: <http://dbpedia.org/b>
PREFIX c: <http://dbpedia.org/c>
PREFIX d: <http://dbpedia.org/d>
PREFIX e: <http://dbpedia.org/e>
PREFIX f: <http://dbpedia.org/f>
PREFIX g: <http://dbpedia.org/g>
PREFIX h: <http://dbpedia.org/h>
FROM <http://dbpedia.org>
SELECT ?s ?p ?o WHERE {
    ?s ?p ?o.
}""")


        queries.append("""PREFIX a: <http://dbpedia.org/a>
PREFIX b: <http://dbpedia.org/b>
PREFIX c: <http://dbpedia.org/c>
PREFIX d: <http://dbpedia.org/d>
PREFIX e: <http://dbpedia.org/e>
PREFIX f: <http://dbpedia.org/f>
PREFIX g: <http://dbpedia.org/g>
PREFIX h: <http://dbpedia.org/h>
SELECT ?s ?p ?o WHERE {
    ?s ?p ?o.
}""")


        queries.append("""
    PREFIX a: <http://dbpedia.org/a>
    PREFIX b: <http://dbpedia.org/b>
    PREFIX c: <http://dbpedia.org/c>
    PREFIX d: <http://dbpedia.org/d>
    PREFIX e: <http://dbpedia.org/e>
    PREFIX f: <http://dbpedia.org/f>
    PREFIX g: <http://dbpedia.org/g>
    PREFIX h: <http://dbpedia.org/h>
    SELECT ?s ?p ?o WHERE {
        ?s ?p ?o.
    }""")


        queries.append("""
    FROM <http://dbpedia.org>
    SELECT ?s ?p ?o WHERE {
        ?s ?p ?o.
    }""")


        queries.append("""
    PREFIX a: <http://dbpedia.org/a>
    PREFIX b: <http://dbpedia.org/b>
    PREFIX c: <http://dbpedia.org/c>
    PREFIX d: <http://dbpedia.org/d>
    PREFIX e: <http://dbpedia.org/e>
    PREFIX f: <http://dbpedia.org/f>
    PREFIX g: <http://dbpedia.org/g>
    PREFIX h: <http://dbpedia.org/h>
    PREFIX a: <http://dbpedia.org/a>
    PREFIX b: <http://dbpedia.org/b>
    PREFIX c: <http://dbpedia.org/c>
    PREFIX d: <http://dbpedia.org/d>
    PREFIX e: <http://dbpedia.org/e>
    PREFIX f: <http://dbpedia.org/f>
    PREFIX g: <http://dbpedia.org/g>
    PREFIX h: <http://dbpedia.org/h>
    PREFIX a: <http://dbpedia.org/a>
    PREFIX b: <http://dbpedia.org/b>
    PREFIX c: <http://dbpedia.org/c>
    PREFIX d: <http://dbpedia.org/d>
    PREFIX e: <http://dbpedia.org/e>
    PREFIX f: <http://dbpedia.org/f>
    PREFIX g: <http://dbpedia.org/g>
    PREFIX h: <http://dbpedia.org/h>
    FROM <http://dbpedia.org>
    SELECT ?s ?p ?o WHERE {
        ?s ?p ?o.
    }""")

        queries.append("""PREFIX a: <http://dbpedia.org/a>
    PREFIX b: <http://dbpedia.org/b>
    PREFIX c: <http://dbpedia.org/c>
    PREFIX d: <http://dbpedia.org/d>
    PREFIX e: <http://dbpedia.org/e>
    PREFIX f: <http://dbpedia.org/f>
    PREFIX g: <http://dbpedia.org/g>
    PREFIX h: <http://dbpedia.org/h>
    PREFIX a: <http://dbpedia.org/a>
    PREFIX b: <http://dbpedia.org/b>
    PREFIX c: <http://dbpedia.org/c>
    PREFIX d: <http://dbpedia.org/d>
    PREFIX e: <http://dbpedia.org/e>
    PREFIX f: <http://dbpedia.org/f>
    PREFIX g: <http://dbpedia.org/g>
    PREFIX h: <http://dbpedia.org/h>
    PREFIX a: <http://dbpedia.org/a>
    PREFIX b: <http://dbpedia.org/b>
    PREFIX c: <http://dbpedia.org/c>
    PREFIX d: <http://dbpedia.org/d>
    PREFIX e: <http://dbpedia.org/e>
    PREFIX f: <http://dbpedia.org/f>
    PREFIX g: <http://dbpedia.org/g>
    PREFIX h: <http://dbpedia.org/h>
    FROM <http://dbpedia.org>
    SELECT ?s ?p ?o WHERE {
        ?s ?p ?o.
    }""")

        for query in queries:
            start_time = time.time()
            sparql.setQuery(query)
            self.assertTrue((time.time()-start_time)<0.001) # less than 0.001 second


if __name__ == "__main__":
    unittest.main()
