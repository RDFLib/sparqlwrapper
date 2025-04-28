#!/usr/bin/python
# -*- coding: utf-8 -*-

import inspect
import io
import json
import os
import sys
import unittest

from rdflib import Graph

# prefer local copy to the one which is installed
# hack from http://stackoverflow.com/a/6098238/280539
_top_level_path = os.path.realpath(
    os.path.abspath(
        os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0], "..")
    )
)
if _top_level_path not in sys.path:
    sys.path.insert(0, _top_level_path)
# end of hack

from SPARQLWrapper.main import main, parse_args
from SPARQLWrapper import POST

endpoint = "http://dbpedia.org/sparql"
testfile = os.path.join(os.path.dirname(__file__), "test.rq")
testquery = "SELECT DISTINCT ?x WHERE { ?x ?y ?z . } LIMIT 3"


def get_bindings(output):
    parsed_output = json.loads(output)
    return parsed_output["results"]["bindings"]


class SPARQLWrapperCLI_Test_Base(unittest.TestCase):
    def setUp(self):
        self.org_stdout, sys.stdout = sys.stdout, io.StringIO()
        self.org_stderr, sys.stderr = sys.stderr, io.StringIO()

    def tearDown(self):
        sys.stdout = self.org_stdout


class SPARQLWrapperCLIParser_Test(SPARQLWrapperCLI_Test_Base):
    def testHelp(self):
        with self.assertRaises(SystemExit) as cm:
            parse_args(["-h"])

        self.assertEqual(cm.exception.code, 0)
        self.assertEqual(sys.stdout.getvalue()[:5], "usage")

    def testVersion(self):
        with self.assertRaises(SystemExit) as cm:
            parse_args(["-V"])

        self.assertEqual(cm.exception.code, 0)
        self.assertEqual(sys.stdout.getvalue()[:3], "rqw")

    def testNoarg(self):
        with self.assertRaises(SystemExit) as cm:
            parse_args([])

        self.assertEqual(cm.exception.code, 2)
        self.assertIn(
            "rqw: error: one of the arguments -f/--file -Q/--query is required",
            sys.stderr.getvalue(),
        )

    def testQueryAndFile(self):
        with self.assertRaises(SystemExit) as cm:
            parse_args(["-Q", testquery, "-f", "-"])

        self.assertEqual(cm.exception.code, 2)
        self.assertIn(
            "rqw: error: argument -f/--file: not allowed with argument -Q/--query",
            sys.stderr.getvalue(),
        )

    def testInvalidFormat(self):
        with self.assertRaises(SystemExit) as cm:
            parse_args(["-Q", testquery, "-F", "jjssoonn"])

        self.assertEqual(cm.exception.code, 2)
        print(sys.stderr.getvalue())
        self.assertIn(
            "rqw: error: argument -F/--format: invalid choice: 'jjssoonn'",
            sys.stderr.getvalue(),
        )

    def testInvalidFile(self):
        with self.assertRaises(SystemExit) as cm:
            parse_args(["-f", "440044.rq"])

        self.assertEqual(cm.exception.code, 2)
        self.assertIn(
            "rqw: error: argument -f/--file: file '440044.rq' is not found",
            sys.stderr.getvalue(),
        )

class SPARQLWrapperCLI_Test(SPARQLWrapperCLI_Test_Base):

    def testQueryWithEndpoint(self):
        main(
            [
                "-Q",
                testquery,
                "-e",
                endpoint,
            ]
        )
        self.assertEqual(len(get_bindings(sys.stdout.getvalue())), 3)

    def testQueryWithFile(self):
        main(["-f", testfile, "-e", endpoint])
        self.assertEqual(len(get_bindings(sys.stdout.getvalue())), 3)

    def testQueryWithFileXML(self):
        main(["-f", testfile, "-e", endpoint, "-F", "xml"])
        self.assertIn(
            "<binding name=",
            sys.stdout.getvalue(),
        )

    def testQueryWithFileTurtle(self):
        main(["-f", testfile, "-e", endpoint, "-F", "turtle"])
        self.assertIn(
            "res:binding",
            sys.stdout.getvalue(),
        )

    def testQueryWithFileTurtleQuiet(self):
        main(
            [
                "-f",
                testfile,
                "-e",
                endpoint,
                "-F",
                "turtle",
                "-q",
            ]
        )
        self.assertIn(
            "res:binding",
            sys.stdout.getvalue(),
        )

    def testQueryWithFileN3(self):
        main(["-f", testfile, "-e", endpoint, "-F", "n3"])
        self.assertIn(
            "res:binding",
            sys.stdout.getvalue(),
        )

    def testQueryRDF(self):
        main(["-Q", "DESCRIBE <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>", "-e", endpoint, "-F", "rdf"])
        g = Graph()
        g.parse(data=sys.stdout.getvalue(), format="turtle")
        self.assertGreater(len(g), 0)

    def testQueryWithFileRDFXML(self):
        main(["-f", testfile, "-e", endpoint, "-F", "rdf+xml"])
        self.assertIn(
            "<binding name=",
            sys.stdout.getvalue(),
        )

    def testQueryWithFileCSV(self):
        main(["-f", testfile, "-e", endpoint, "-F", "csv"])
        self.assertIn(
            "pllabel",
            sys.stdout.getvalue(),
        )

    def testQueryWithFileTSV(self):
        main(["-f", testfile, "-e", endpoint, "-F", "tsv"])
        self.assertIn(
            "pllabel",
            sys.stdout.getvalue(),
        )

    def testQueryToLovFuseki(self):
        main(["-e", "https://lov.linkeddata.es/dataset/lov/sparql/", "-Q", testquery])
        self.assertEqual(len(get_bindings(sys.stdout.getvalue())), 3)

    def testQueryToRDF4J(self):
        main(
            [
                "-e",
                "http://vocabs.ands.org.au/repository/api/sparql/csiro_international-chronostratigraphic-chart_2018-revised-corrected",
                "-Q",
                testquery,
            ]
        )
        self.assertEqual(len(get_bindings(sys.stdout.getvalue())), 3)

    def testQueryToAllegroGraph(self):
        main(["-e", "https://mmisw.org/sparql", "-Q", testquery])
        self.assertEqual(len(get_bindings(sys.stdout.getvalue())), 3)

    def testQueryToGraphDBEnterprise(self):
        main(["-e", "http://factforge.net/repositories/ff-news", "-Q", testquery])
        self.assertEqual(len(get_bindings(sys.stdout.getvalue())), 3)

    def testQueryToStardog(self):
        main(["-e", "https://lindas.admin.ch/query", "-Q", testquery, "-m", POST])
        self.assertEqual(len(get_bindings(sys.stdout.getvalue())), 3)

    def testQueryToAgrovoc_AllegroGraph(self):
        main(["-e", "https://agrovoc.fao.org/sparql", "-Q", testquery])
        self.assertEqual(len(get_bindings(sys.stdout.getvalue())), 3)

    def testQueryToVirtuosoV7(self):
        main(["-e", "http://dbpedia.org/sparql", "-Q", testquery])
        self.assertEqual(len(get_bindings(sys.stdout.getvalue())), 3)

    def testQueryToBrazeGraph(self):
        main(["-e", "https://query.wikidata.org/sparql", "-Q", testquery])
        self.assertEqual(len(get_bindings(sys.stdout.getvalue())), 3)

    def testQueryToFuseki2V3_6(self):
        main(["-e", "https://agrovoc.uniroma2.it/sparql/", "-Q", testquery])
        self.assertEqual(len(get_bindings(sys.stdout.getvalue())), 3)

    def testQueryToFuseki2V3_8(self):
        main(["-e", "http://zbw.eu/beta/sparql/stw/query", "-Q", testquery])
        self.assertEqual(len(get_bindings(sys.stdout.getvalue())), 3)

    def testQueryTo4store(self):
        main(["-e", "http://rdf.chise.org/sparql", "-Q", testquery])
        self.assertEqual(len(get_bindings(sys.stdout.getvalue())), 3)
