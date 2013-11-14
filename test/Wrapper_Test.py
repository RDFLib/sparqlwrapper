# -*- coding: utf-8 -*-
import inspect
import os
import sys
from unittest import TestCase

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

    def testSetMethod(self):
        self.wrapper.setMethod(POST)
        request = self.wrapper.query().response  # possible due to mock above

        self.assertEqual("POST", request.get_method())

        self.wrapper.setMethod(GET)
        request = self.wrapper.query().response  # possible due to mock above

        self.assertEqual("GET", request.get_method())
