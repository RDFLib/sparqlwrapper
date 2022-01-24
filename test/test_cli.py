#!/usr/bin/python
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
from SPARQLWrapper import POST

endpoint = "http://ja.dbpedia.org/sparql"
testfile = os.path.join(os.path.dirname(__file__), "test.rq")
testquery = "SELECT DISTINCT ?x WHERE { ?x ?y ?z . } LIMIT 1"


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
            parse_args(["-Q", testquery, "-f", "-"])

        self.assertEqual(cm.exception.code, 2)
        self.assertEqual(
            sys.stderr.getvalue().split("\n")[1],
            "rqw: error: argument -f/--file: not allowed with argument -Q/--query",
        )

    def testInvalidFormat(self):
        with self.assertRaises(SystemExit) as cm:
            parse_args(["-Q", testquery, "-F", "jjssoonn"])

        self.assertEqual(cm.exception.code, 2)
        self.assertEqual(
            sys.stderr.getvalue().split("\n")[1],
            "rqw: error: argument -F/--format: invalid choice: 'jjssoonn' (choose from 'json', 'xml', 'turtle', 'n3', 'rdf', 'rdf+xml', 'csv', 'tsv', 'json-ld')",
        )

    def testInvalidFile(self):
        with self.assertRaises(SystemExit) as cm:
            parse_args(["-f", "440044.rq"])

        self.assertEqual(cm.exception.code, 2)
        self.assertEqual(
            sys.stderr.getvalue().split("\n")[1],
            "rqw: error: argument -f/--file: file '440044.rq' is not found",
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

        self.assertEqual(
            sys.stdout.getvalue(),
            textwrap.dedent(
                """\
            {
                "head": {
                    "link": [],
                    "vars": [
                        "x"
                    ]
                },
                "results": {
                    "distinct": false,
                    "ordered": true,
                    "bindings": [
                        {
                            "x": {
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
            @prefix res: <http://www.w3.org/2005/sparql-results#> .
            @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
            _:_ a res:ResultSet .
            _:_ res:resultVariable "pllabel" .
            _:_ res:solution [
                  res:binding [ res:variable "pllabel" ; res:value "PARLOG"@ja ] ] .\n
            """
            ),
        )

    def testQueryRDF(self):
        main(["-Q", "DESCRIBE <http://ja.wikipedia.org/wiki/SPARQL>", "-e", endpoint, "-F", "rdf"])

        self.assertEqual(
            sys.stdout.getvalue(),
            textwrap.dedent(
                """\
            @prefix dc: <http://purl.org/dc/elements/1.1/> .
            @prefix foaf: <http://xmlns.com/foaf/0.1/> .

            <http://ja.dbpedia.org/resource/SPARQL> foaf:isPrimaryTopicOf <http://ja.wikipedia.org/wiki/SPARQL> .

            <http://ja.wikipedia.org/wiki/SPARQL> a foaf:Document ;
                dc:language "ja" ;
                foaf:primaryTopic <http://ja.dbpedia.org/resource/SPARQL> .


            """
            ),
        )

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

    def testQueryToLovFuseki(self):
        main(["-e", "https://lov.linkeddata.es/dataset/lov/sparql/", "-Q", testquery])
        self.assertEqual(
            sys.stdout.getvalue(),
            textwrap.dedent(
                """\
            {
                "head": {
                    "vars": [
                        "x"
                    ]
                },
                "results": {
                    "bindings": [
                        {
                            "x": {
                                "type": "uri",
                                "value": "http://www.w3.org/2002/07/owl#someValuesFrom"
                            }
                        }
                    ]
                }
            }
            """
            ),
        )

    def testQueryToRDF4J(self):
        main(
            [
                "-e",
                "http://vocabs.ands.org.au/repository/api/sparql/csiro_international-chronostratigraphic-chart_2018-revised-corrected",
                "-Q",
                testquery,
            ]
        )
        self.assertEqual(
            sys.stdout.getvalue(),
            textwrap.dedent(
                """\
            {
                "head": {
                    "vars": [
                        "x"
                    ]
                },
                "results": {
                    "bindings": [
                        {
                            "x": {
                                "type": "uri",
                                "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
                            }
                        }
                    ]
                }
            }
            """
            ),
        )

    def testQueryToAllegroGraph(self):
        main(["-e", "https://mmisw.org/sparql", "-Q", testquery])
        self.assertEqual(
            sys.stdout.getvalue(),
            textwrap.dedent(
                """\
            {
                "head": {
                    "vars": [
                        "x"
                    ]
                },
                "results": {
                    "bindings": [
                        {
                            "x": {
                                "type": "uri",
                                "value": "https://mmisw.org/ont/~mjuckes/cmip_variables_alpha/rsdcs4co2"
                            }
                        }
                    ]
                }
            }
            """
            ),
        )

    def testQueryToGraphDBEnterprise(self):
        main(["-e", "http://factforge.net/repositories/ff-news", "-Q", testquery])
        self.assertEqual(
            sys.stdout.getvalue(),
            textwrap.dedent(
                """\
            {
                "head": {
                    "vars": [
                        "x"
                    ]
                },
                "results": {
                    "bindings": [
                        {
                            "x": {
                                "type": "uri",
                                "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
                            }
                        }
                    ]
                }
            }
            """
            ),
        )

    def testQueryToStardog(self):
        main(["-e", "https://lindas.admin.ch/query", "-Q", testquery, "-m", POST])
        self.assertEqual(
            sys.stdout.getvalue(),
            textwrap.dedent(
                """\
            {
                "head": {
                    "vars": [
                        "x"
                    ]
                },
                "results": {
                    "bindings": [
                        {
                            "x": {
                                "type": "uri",
                                "value": "http://classifications.data.admin.ch/canton/bl"
                            }
                        }
                    ]
                }
            }
            """
            ),
        )

    def testQueryToAgrovoc_AllegroGraph(self):
        main(["-e", "https://agrovoc.fao.org/sparql", "-Q", testquery])
        self.assertEqual(
            sys.stdout.getvalue(),
            textwrap.dedent(
                """\
            {
                "head": {
                    "vars": [
                        "x"
                    ]
                },
                "results": {
                    "bindings": [
                        {
                            "x": {
                                "type": "uri",
                                "value": "http://aims.fao.org/aos/agrovoc/"
                            }
                        }
                    ]
                }
            }
            """
            ),
        )

    def testQueryToVirtuosoV8(self):
        main(["-e", "http://dbpedia-live.openlinksw.com/sparql", "-Q", testquery])
        self.assertEqual(
            sys.stdout.getvalue(),
            textwrap.dedent(
                """\
            {
                "head": {
                    "link": [],
                    "vars": [
                        "x"
                    ]
                },
                "results": {
                    "distinct": false,
                    "ordered": true,
                    "bindings": [
                        {
                            "x": {
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

    def testQueryToVirtuosoV7(self):
        main(["-e", "http://dbpedia.org/sparql", "-Q", testquery])
        self.assertEqual(
            sys.stdout.getvalue(),
            textwrap.dedent(
                """\
            {
                "head": {
                    "link": [],
                    "vars": [
                        "x"
                    ]
                },
                "results": {
                    "distinct": false,
                    "ordered": true,
                    "bindings": [
                        {
                            "x": {
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

    def testQueryToBrazeGraph(self):
        main(["-e", "https://query.wikidata.org/sparql", "-Q", testquery])
        self.assertEqual(
            sys.stdout.getvalue(),
            textwrap.dedent(
                """\
            {
                "head": {
                    "vars": [
                        "x"
                    ]
                },
                "results": {
                    "bindings": [
                        {
                            "x": {
                                "type": "uri",
                                "value": "http://wikiba.se/ontology#Dump"
                            }
                        }
                    ]
                }
            }
            """
            ),
        )

    def testQueryToFuseki2V3_6(self):
        main(["-e", "https://agrovoc.uniroma2.it/sparql/", "-Q", testquery])
        self.assertEqual(
            sys.stdout.getvalue(),
            textwrap.dedent(
                """\
            {
                "head": {
                    "vars": [
                        "x"
                    ]
                },
                "results": {
                    "bindings": [
                        {
                            "x": {
                                "type": "uri",
                                "value": "http://aims.fao.org/aos/agrovoc/"
                            }
                        }
                    ]
                }
            }
            """
            ),
        )

    def testQueryToFuseki2V3_8(self):
        main(["-e", "http://zbw.eu/beta/sparql/stw/query", "-Q", testquery])
        self.assertEqual(
            sys.stdout.getvalue(),
            textwrap.dedent(
                """\
            {
                "head": {
                    "vars": [
                        "x"
                    ]
                },
                "results": {
                    "bindings": [
                        {
                            "x": {
                                "type": "uri",
                                "value": "http://www.w3.org/2004/02/skos/core"
                            }
                        }
                    ]
                }
            }
            """
            ),
        )

    def testQueryTo4store(self):
        main(["-e", "http://rdf.chise.org/sparql", "-Q", testquery])
        self.assertEqual(
            sys.stdout.getvalue(),
            textwrap.dedent(
                """\
            {
                "head": {
                    "vars": [
                        "x"
                    ]
                },
                "results": {
                    "bindings": [
                        {
                            "x": {
                                "type": "bnode",
                                "value": "b1f4d352f000000fc"
                            }
                        }
                    ]
                }
            }
            """
            ),
        )
