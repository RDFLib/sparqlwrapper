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
        wrapper = SPARQLWrapper(endpoint='http://example.org/sparql/')

        wrapper.setMethod(POST)
        wrapper.setQuery('CONSTRUCT WHERE {?a ?b ?c}')
        wrapper.setReturnFormat(JSON)
        wrapper.addParameter('a', 'b')

        wrapper.resetQuery()

        self.assertEqual(GET, wrapper.method)
        self.assertEqual('SELECT * WHERE{ ?s ?p ?o }', wrapper.queryString)
        self.assertEqual(SELECT, wrapper.queryType)
        self.assertEqual(XML, wrapper.returnFormat)
        self.assertEqual({}, wrapper.parameters)

    def testSetMethod(self):
        wrapper = SPARQLWrapper(endpoint='http://example.org/sparql/')
        wrapper.setMethod(POST)

        qr = wrapper.query()
        request = qr.response

        self.assertEqual("POST", request.get_method())

        wrapper.setMethod(GET)

        qr = wrapper.query()
        request = qr.response

        self.assertEqual("GET", request.get_method())
