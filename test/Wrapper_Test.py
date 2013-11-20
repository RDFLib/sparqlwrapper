# -*- coding: utf-8 -*-
import inspect
import os
import sys
from unittest import TestCase
from urlparse import urlparse
from urllib2 import Request
from cgi import parse_qs

# prefer local copy to the one which is installed
# hack from http://stackoverflow.com/a/6098238/280539
_top_level_path = os.path.realpath(os.path.abspath(os.path.join(
    os.path.split(inspect.getfile(inspect.currentframe()))[0],
    ".."
)))
if _top_level_path not in sys.path:
    sys.path.insert(0, _top_level_path)
# end of hack

from SPARQLWrapper import SPARQLWrapper, XML, GET, POST, JSON, SELECT
from SPARQLWrapper.Wrapper import QueryResult, QueryBadFormed, EndPointNotFound, EndPointInternalError


# we don't want to let Wrapper do real web-requests. so, we are…
# constructing a simple Mock!
from urllib2 import HTTPError
from StringIO import StringIO

import SPARQLWrapper.Wrapper as _victim


class FakeResult(object):
    def __init__(self, request):
        self.request = request


def urlopener(request):
    return FakeResult(request)


def urlopener_error_generator(code):
    def urlopener_error(request):
        raise HTTPError(request.get_full_url, code, '', {}, StringIO(''))

    return urlopener_error
# DONE


class SPARQLWrapper_Test(TestCase):
    def setUp(self):
        self.wrapper = SPARQLWrapper(endpoint='http://example.org/sparql/')
        _victim.urllib2.urlopen = urlopener

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
        self.assertEqual(
            ['http://example.org/default'],
            wrapper.parameters.get('default-graph-uri'),
            'default graph is set'
        )

    def testReset(self):
        self.wrapper.setMethod(POST)
        self.wrapper.setQuery('CONSTRUCT WHERE {?a ?b ?c}')
        self.wrapper.setReturnFormat(JSON)
        self.wrapper.addParameter('a', 'b')

        self.wrapper.resetQuery()

        self.assertEqual(GET, self.wrapper.method)
        self.assertEqual('SELECT * WHERE{ ?s ?p ?o }', self.wrapper.queryString)
        self.assertEqual(SELECT, self.wrapper.queryType)
        self.assertEqual(XML, self.wrapper.returnFormat)
        self.assertEqual({}, self.wrapper.parameters)

    def testSetReturnFormat(self):
        self.wrapper.setReturnFormat('nonexistent format')
        self.assertEqual(XML, self.wrapper.query().requestedFormat)

        self.wrapper.setReturnFormat(JSON)
        self.assertEqual(JSON, self.wrapper.query().requestedFormat)

    def testAddParameter(self):
        self.assertFalse(self.wrapper.addParameter('query', 'dummy'))
        self.assertTrue(self.wrapper.addParameter('param1', 'value1'))
        self.assertTrue(self.wrapper.addParameter('param1', 'value2'))
        self.assertTrue(self.wrapper.addParameter('param2', 'value2'))

        request = self.wrapper.query().response.request  # possible due to mock above
        pieces_str = urlparse(request.get_full_url()).query
        pieces = parse_qs(pieces_str)

        self.assertTrue('param1' in pieces)
        self.assertEqual(['value1', 'value2'], pieces['param1'])
        self.assertTrue('param2' in pieces)
        self.assertEqual(['value2'], pieces['param2'])
        self.assertNotEqual(['dummy'], 'query')

    def testSetCredentials(self):
        request = self.wrapper.query().response.request  # possible due to mock above

        self.assertFalse(request.has_header('Authorization'))

        self.wrapper.setCredentials('login', 'password')
        request = self.wrapper.query().response.request  # possible due to mock above

        self.assertTrue(request.has_header('Authorization'))
        # TODO: test for header-value using some external decoder implementation

    def testClearParameter(self):
        self.wrapper.addParameter('param1', 'value1')
        self.wrapper.addParameter('param1', 'value2')
        self.wrapper.addParameter('param2', 'value2')

        self.assertFalse(self.wrapper.clearParameter('query'))
        self.assertTrue(self.wrapper.clearParameter('param1'))

        request = self.wrapper.query().response.request  # possible due to mock above
        pieces_str = urlparse(request.get_full_url()).query
        pieces = parse_qs(pieces_str)

        self.assertFalse('param1' in pieces)
        self.assertTrue('param2' in pieces)
        self.assertEqual(['value2'], pieces['param2'])

    def testSetMethod(self):
        self.wrapper.setMethod(POST)
        request = self.wrapper.query().response.request  # possible due to mock above

        self.assertEqual("POST", request.get_method())

        self.wrapper.setMethod(GET)
        request = self.wrapper.query().response.request  # possible due to mock above

        self.assertEqual("GET", request.get_method())

    def testIsSparqlUpdateRequest(self):
        self.wrapper.setQuery('DELETE WHERE {?s ?p ?o}')
        self.assertTrue(self.wrapper.isSparqlUpdateRequest())

        self.wrapper.setQuery("""
        PREFIX example: <http://example.org/SELECT/>
        BASE <http://example.org/SELECT>
        DELETE WHERE {?s ?p ?o}
        """)
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

    def testQuery(self):
        qr = self.wrapper.query()
        self.assertTrue(isinstance(qr, QueryResult))

        request = qr.response.request  # possible due to mock above
        self.assertTrue(isinstance(request, Request))

        _victim.urllib2.urlopen = urlopener_error_generator(400)
        try:
            self.wrapper.query()
            self.fail('should have raised exception')
        except QueryBadFormed, e:
            #  TODO: check exception-format
            pass
        except:
            self.fail('got wrong exception')

        _victim.urllib2.urlopen = urlopener_error_generator(404)
        try:
            self.wrapper.query()
            self.fail('should have raised exception')
        except EndPointNotFound, e:
            #  TODO: check exception-format
            pass
        except:
            self.fail('got wrong exception')

        _victim.urllib2.urlopen = urlopener_error_generator(500)
        try:
            self.wrapper.query()
            self.fail('should have raised exception')
        except EndPointInternalError, e:
            #  TODO: check exception-format
            pass
        except:
            self.fail('got wrong exception')

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


class QueryResult_Test(TestCase):
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

            def next(self):
                self.next_called = True

        result = FakeResponse()

        qr = QueryResult(result)
        qr.geturl()
        qr.__iter__()
        qr.next()

        self.assertTrue(result.geturl_called)
        self.assertTrue(result.iter_called)
        self.assertTrue(result.next_called)

        info = qr.info()
        self.assertTrue(result.info_called)
        self.assertEqual('value', info.__getitem__('KEY'), 'keys should be case-insensitive')
