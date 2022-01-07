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

endpoint = "http://ja.dbpedia.org/sparql"
testfile = os.path.join(os.path.dirname(__file__), 'test.rq')

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

    def testInvalidFormat(self):
        with self.assertRaises(SystemExit) as cm:
            parse_args(
                ["-Q", "SELECT ?s WHERE { ?s ?p ?o. } limit 1", "-F", "jjssoonn"]
            )

        self.assertEqual(cm.exception.code, 2)
        self.assertEqual(
            sys.stderr.getvalue().split("\n")[1],
            "rqw: error: argument -F/--format: invalid choice: 'jjssoonn' (choose from 'json', 'xml', 'turtle', 'n3', 'rdf', 'rdf+xml', 'csv', 'tsv')",
        )

    def testInvalidFile(self):
        with self.assertRaises(SystemExit) as cm:
            parse_args(["-f", "440044.rq"])

        self.assertEqual(cm.exception.code, 2)
        self.assertEqual(
            sys.stderr.getvalue().split("\n")[1],
            "rqw: error: argument -f/--file: invalid check_file value: '440044.rq'",
        )


class SPARQLWrapperCLI_Test(SPARQLWrapperCLI_Test_Base):
    def testQueryWithEndpoint(self):
        main(
            [
                "-Q",
                "SELECT ?s WHERE { ?s ?p ?o. } limit 1",
                "-e",
                endpoint,
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
        main(["-f", testfile, "-e", endpoint])

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
                                "value": "PARLOG"
                            }
                        }
                    ]
                }
            }
            """
            ),
        )

    def testQueryWithFileXML(self):
        main(["-f", testfile, "-e", endpoint, "-F", "xml"])

        self.assertEqual(
            sys.stdout.getvalue(),
            textwrap.dedent(
                """\
            <?xml version="1.0" ?><sparql xmlns="http://www.w3.org/2005/sparql-results#" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.w3.org/2001/sw/DataAccess/rf1/result2.xsd">
             <head>
              <variable name="pllabel"/>
             </head>
             <results distinct="false" ordered="true">
              <result>
               <binding name="pllabel"><literal xml:lang="ja">PARLOG</literal></binding>
              </result>
             </results>
            </sparql>
            """
            ),
        )

    def testQueryWithFileTurtle(self):
        main(["-f", testfile, "-e", endpoint, "-F", "turtle"])

        self.assertEqual(
            sys.stdout.getvalue(),
            textwrap.dedent(
                """\
            @prefix res: <http://www.w3.org/2005/sparql-results#> .
            @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
            _:_ a res:ResultSet .
            _:_ res:resultVariable "pllabel" .
            _:_ res:solution [
                  res:binding [ res:variable "pllabel" ; res:value "PARLOG"@ja ] ] .\n
            """
            ),
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
        self.assertEqual(sys.stderr.getvalue(), "")
        self.assertEqual(
            sys.stdout.getvalue(),
            textwrap.dedent(
                """\
            @prefix res: <http://www.w3.org/2005/sparql-results#> .
            @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
            _:_ a res:ResultSet .
            _:_ res:resultVariable "pllabel" .
            _:_ res:solution [
                  res:binding [ res:variable "pllabel" ; res:value "PARLOG"@ja ] ] .\n
            """
            ),
        )

    def testQueryWithFileN3(self):
        main(["-f", testfile, "-e", endpoint, "-F", "n3"])

        self.assertEqual(
            sys.stdout.getvalue(),
            textwrap.dedent(
                """\
            @prefix res: <http://www.w3.org/2005/sparql-results#> .\n
            [] a res:ResultSet ;
                res:resultVariable "pllabel" ;
                res:solution [ res:binding [ res:value "PARLOG"@ja ;
                                res:variable "pllabel" ] ] .\n\n
            """
            ),
        )

    # def testQueryWithFileRDF(self):
    #     main(["-f", testfile, "-e", endpoint, "-F", "rdf"])
    #
    #     self.assertEqual(
    #         sys.stdout.getvalue(),
    #         textwrap.dedent(
    #             """\
    #         """)
    #     )

    def testQueryWithFileRDFXML(self):
        main(["-f", testfile, "-e", endpoint, "-F", "rdf+xml"])

        self.assertEqual(
            sys.stdout.getvalue(),
            textwrap.dedent(
                """\
            <?xml version="1.0" ?><sparql xmlns="http://www.w3.org/2005/sparql-results#" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.w3.org/2001/sw/DataAccess/rf1/result2.xsd">
             <head>
              <variable name="pllabel"/>
             </head>
             <results distinct="false" ordered="true">
              <result>
               <binding name="pllabel"><literal xml:lang="ja">PARLOG</literal></binding>
              </result>
             </results>
            </sparql>
            """
            ),
        )

    def testQueryWithFileCSV(self):
        main(["-f", testfile, "-e", endpoint, "-F", "csv"])

        self.assertEqual(
            sys.stdout.getvalue(),
            textwrap.dedent(
                """\
                "pllabel"
                "PARLOG"\n
            """
            ),
        )

    def testQueryWithFileTSV(self):
        main(["-f", testfile, "-e", endpoint, "-F", "tsv"])

        self.assertEqual(
            sys.stdout.getvalue(),
            textwrap.dedent(
                """\
                "pllabel"
                "PARLOG"\n
            """
            ),
        )
