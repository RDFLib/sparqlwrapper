# -*- coding: utf-8 -*-
import inspect
import io
import os
import sys
import textwrap
import unittest

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


class SPARQLWrapper_Test(unittest.TestCase):
    def setUp(self):
        self.org_stdout, sys.stdout = sys.stdout, io.StringIO()
        self.org_stderr, sys.stderr = sys.stderr, io.StringIO()

    def tearDown(self):
        sys.stdout = self.org_stdout

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
        self.assertEqual(
            sys.stderr.getvalue().split("\n")[1],
            "rqw: error: one of the arguments -f/--file -Q/--query is required",
        )

    def testQueryAndFile(self):
        with self.assertRaises(SystemExit) as cm:
            parse_args(["-Q", "SELECT ?s WHERE { ?s ?p ?o. } limit 1", "-f", "-"])

        self.assertEqual(cm.exception.code, 2)
        self.assertEqual(
            sys.stderr.getvalue().split("\n")[1],
            "rqw: error: argument -f/--file: not allowed with argument -Q/--query",
        )

    def testQueryWithEndpoint(self):
        main(
            [
                "-Q",
                "SELECT ?s WHERE { ?s ?p ?o. } limit 1",
                "-e",
                "http://ja.dbpedia.org/sparql",
            ]
        )

        self.assertEqual(
            sys.stdout.getvalue(),
            textwrap.dedent(
                """\
            {
                "head": {
                    "link": [],
                    "vars": [
                        "s"
                    ]
                },
                "results": {
                    "distinct": false,
                    "ordered": true,
                    "bindings": [
                        {
                            "s": {
                                "type": "uri",
                                "value": "http://www.openlinksw.com/virtrdf-data-formats#default-iid"
                            }
                        }
                    ]
                }
            }
            """
            ),
        )

    def testQueryWithFile(self):
        main(["-f", "test.rq", "-e", "http://ja.dbpedia.org/sparql"])

        self.assertEqual(
            sys.stdout.getvalue(),
            textwrap.dedent(
                """\
            {
                "head": {
                    "link": [],
                    "vars": [
                        "pllabel"
                    ]
                },
                "results": {
                    "distinct": false,
                    "ordered": true,
                    "bindings": [
                        {
                            "pllabel": {
                                "type": "literal",
                                "xml:lang": "ja",
                                "value": "ABC (\\u30d7\\u30ed\\u30b0\\u30e9\\u30df\\u30f3\\u30b0\\u8a00\\u8a9e)"
                            }
                        }
                    ]
                }
            }
            """
            ),
        )
