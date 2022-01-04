#!/usr/bin/env python

# -*- coding: utf-8 -*-

import argparse
import json
import os
import sys
from shutil import get_terminal_size

import rdflib  # type: ignore

from . import __version__
from .Wrapper import SPARQLWrapper, _allowedFormats


class SPARQLWrapperFormatter(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
):
    pass


def check_file(v):
    if os.path.isfile(v):
        return v
    elif v == "-":
        return "-"  # stdin
    else:
        raise OSError("file '%s' is not found" % v)


def choicesDescriptions():
    return "\n  - ".join(["allowed formats:"] + _allowedFormats)


def parse_args():
    """Parse arguments."""
    parser = argparse.ArgumentParser(
        prog="rqw",
        formatter_class=(
            lambda prog: SPARQLWrapperFormatter(
                prog,
                **{
                    "width": get_terminal_size(fallback=(120, 50)).columns,
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
        default="-",
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
    parser.add_argument("-q", "--quiet", action="store_true", help="supress warnings")
    parser.add_argument(
        "-V", "--version", action="version", version="%(prog)s {}".format(__version__)
    )
    return parser.parse_args()


def main():
    args = parse_args()
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
    sparql.setQuery(q)
    sparql.setReturnFormat(args.format)
    results = sparql.query().convert()

    if args.format == "json":
        print(json.dumps(results, indent=4))
    elif args.format in ("xml", "rdf+xml", "json-ld"):
        print(results.toxml())  # type: ignore
    elif args.format == "n3":
        g = rdflib.Graph()
        g.parse(data=results, format="n3")  # type: ignore
        print(g.serialize(format="n3"))
    elif args.format in ("csv", "tsv", "turtle"):
        print(results.decode("utf-8"))  # type: ignore
    else:
        print(results)


if __name__ == "__main__":
    main()
