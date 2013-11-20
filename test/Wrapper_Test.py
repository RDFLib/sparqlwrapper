# -*- coding: utf-8 -*-
import inspect
import os
import sys
from unittest import TestCase
from urlparse import urlparse
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


# we don't want to let Wrapper do real web-requests. so, we are…
# constructing a simple Mock!
import SPARQLWrapper.Wrapper as _victim


def urlopener(request):
    return request
_victim.urllib2.urlopen = urlopener
# DONE


class SPARQLWrapper_Test(TestCase):
    def setUp(self):
        self.wrapper = SPARQLWrapper(endpoint='http://example.org/sparql/')

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

        request = self.wrapper.query().response  # possible due to mock above
        pieces_str = urlparse(request.get_full_url()).query
        pieces = parse_qs(pieces_str)

        self.assertTrue('param1' in pieces)
        self.assertEqual(['value1', 'value2'], pieces['param1'])
        self.assertTrue('param2' in pieces)
        self.assertEqual(['value2'], pieces['param2'])
        self.assertNotEqual(['dummy'], 'query')

    def testClearParameter(self):
        self.wrapper.addParameter('param1', 'value1')
        self.wrapper.addParameter('param1', 'value2')
        self.wrapper.addParameter('param2', 'value2')

        self.assertFalse(self.wrapper.clearParameter('query'))
        self.assertTrue(self.wrapper.clearParameter('param1'))

        request = self.wrapper.query().response  # possible due to mock above
        pieces_str = urlparse(request.get_full_url()).query
        pieces = parse_qs(pieces_str)

        self.assertFalse('param1' in pieces)
        self.assertTrue('param2' in pieces)
        self.assertEqual(['value2'], pieces['param2'])

    def testSetMethod(self):
        self.wrapper.setMethod(POST)
        request = self.wrapper.query().response  # possible due to mock above

        self.assertEqual("POST", request.get_method())

        self.wrapper.setMethod(GET)
        request = self.wrapper.query().response  # possible due to mock above

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
