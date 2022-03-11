#!/usr/bin/env python

# -*- coding: utf-8 -*-

import argparse
import json
import os
import shutil
import sys
import xml
from typing import List, Optional

import rdflib

from . import __version__
from .Wrapper import SPARQLWrapper, _allowedAuth, _allowedFormats, _allowedRequests


class SPARQLWrapperFormatter(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
):
    pass


def check_file(v: str) -> str:
    if os.path.isfile(v):
        return v
    elif v == "-":
        return "-"  # stdin
    else:
        raise argparse.ArgumentTypeError("file '%s' is not found" % v)


def choicesDescriptions() -> str:
    d = "\n  - ".join(["allowed FORMAT:"] + _allowedFormats)
    d += "\n  - ".join(["\n\nallowed METHOD:"] + _allowedRequests)
    d += "\n  - ".join(["\n\nallowed AUTH:"] + _allowedAuth)
    return d


def parse_args(test: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse arguments."""
    parser = argparse.ArgumentParser(
        prog="rqw",
        formatter_class=(
            lambda prog: SPARQLWrapperFormatter(
                prog,
                **{
                    "width": shutil.get_terminal_size(fallback=(120, 50)).columns,
                    "max_help_position": 30,
                },
            )
        ),
        description="sparqlwrapper CLI",
        epilog=choicesDescriptions(),
    )
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "-f",
        "--file",
        metavar="FILE",
        type=check_file,
        help="query with sparql file (stdin: -)",
    )
    input_group.add_argument("-Q", "--query", metavar="QUERY", help="query with string")
    parser.add_argument(
        "-F",
        "--format",
        default="json",
        metavar="FORMAT",
        choices=_allowedFormats,
        help="response format",
    )
    parser.add_argument(
        "-e",
        "--endpoint",
        metavar="URI",
        help="sparql endpoint",
        default="http://dbpedia.org/sparql",
    )
    parser.add_argument(
        "-m",
        "--method",
        metavar="METHOD",
        choices=_allowedRequests,
        help="request method",
    )
    parser.add_argument(
        "-a", "--auth", metavar="AUTH", choices=_allowedAuth, help="HTTP auth"
    )
    parser.add_argument(
        "-u", "--username", metavar="ID", default="guest", help="username for auth"
    )
    parser.add_argument(
        "-p", "--password", metavar="PW", default="", help="password for auth"
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="supress warnings")
    parser.add_argument(
        "-V", "--version", action="version", version="%(prog)s {}".format(__version__)
    )
    if test is None:
        return parser.parse_args()
    else:
        return parser.parse_args(test)


def main(test: Optional[List[str]] = None) -> None:
    args = parse_args(test)
    if args.quiet:
        import warnings

        warnings.filterwarnings("ignore")

    q = ""
    if args.query is not None:
        q = args.query
    elif args.file == "-":
        q = sys.stdin.read()
    else:
        q = open(args.file, "r").read()

    sparql = SPARQLWrapper(
        args.endpoint,
        agent=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/96.0.4664.110 Safari/537.36"
        ),
    )
    if args.auth is not None:
        sparql.setHTTPAuth(args.auth)
        sparql.setCredentials(args.username, args.password)
    if args.method is not None:
        sparql.setMethod(args.method)
    sparql.setQuery(q)
    sparql.setReturnFormat(args.format)
    results = sparql.query().convert()

    if isinstance(results, dict):
        # "json"
        print(json.dumps(results, indent=4))
    elif isinstance(results, xml.dom.minidom.Document):
        # "xml"
        print(results.toxml())
    elif isinstance(results, bytes):
        # "csv", "tsv", "turtle", "n3"
        print(results.decode("utf-8"))
    elif isinstance(results, rdflib.graph.ConjunctiveGraph):
        # "rdf"
        print(results.serialize())
    else:
        # unknown type
        raise TypeError(f"Unsupported result of type {type(results)}: {results!r}")


if __name__ == "__main__":
    main()
