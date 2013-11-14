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

from SPARQLWrapper import SPARQLWrapper, XML


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
