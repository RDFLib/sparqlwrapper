#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from typing import Literal
import pytest
from urllib.error import HTTPError

from SPARQLWrapper import (
    CSV,
    GET,
    JSON,
    JSONLD,
    N3,
    POST,
    RDFXML,
    TSV,
    TURTLE,
    XML,
    SPARQLWrapper,
)
from SPARQLWrapper.SPARQLExceptions import QueryBadFormed
from SPARQLWrapper.Wrapper import (
    _CSV,
    _RDF_JSONLD,
    _RDF_N3,
    _RDF_TURTLE,
    _RDF_XML,
    _SPARQL_JSON,
    _SPARQL_XML,
    _TSV,
    _XML,
    QueryResult,
)

try:
    from rdflib.graph import Dataset
except ImportError:
    from rdflib import Dataset

import warnings

warnings.simplefilter("always")
logging.basicConfig()

# Format groups for result checking
_SPARQL_SELECT_ASK_POSSIBLE = _SPARQL_XML + _SPARQL_JSON + _CSV + _TSV + _XML
_SPARQL_DESCRIBE_CONSTRUCT_POSSIBLE = _RDF_XML + _RDF_N3 + _XML + _RDF_JSONLD
# only used in test. Same as Wrapper._RDF_POSSIBLE

VIRTUOSO_7_20_3230_dbpedia = "https://dbpedia.org/sparql"
BLAZEGRAPH_WIKIDATA = "https://query.wikidata.org/sparql"
GRAPHDB_ENTERPRISE_8_9_0 = "http://factforge.net/repositories/ff-news" # http://factforge.net/
RDF4J_GEOSCIML = "http://vocabs.ands.org.au/repository/api/sparql/csiro_international-chronostratigraphic-chart_2018-revised-corrected"
ALLEGROGRAPH_AGROVOC = "https://agrovoc.fao.org/sparql"
ALLEGROGRAPH_4_14_1_MMI = "https://mmisw.org/sparql"  # AllegroServe/1.3.28 http://mmisw.org:10035/doc/release-notes.html
FUSEKI_LOV = "https://lov.linkeddata.es/dataset/lov/sparql"  # Fuseki - version 1.1.1 (Build date: 2014-10-02T16:36:17+0100)
FUSEKI2_3_8_0_STW = "http://zbw.eu/beta/sparql/stw/query"  # Fuseki 3.8.0 (Fuseki2)
STARDOG_LINDAS = "https://lindas.admin.ch/query"  # human UI https://lindas.admin.ch/sparql/
STORE4_1_1_4_CHISE = "http://rdf.chise.org/sparql"  # 4store SPARQL server v1.1.4

# Test parameters
@pytest.fixture(params=[
    VIRTUOSO_7_20_3230_dbpedia,
    GRAPHDB_ENTERPRISE_8_9_0,
    ALLEGROGRAPH_AGROVOC,
    ALLEGROGRAPH_4_14_1_MMI,
    BLAZEGRAPH_WIKIDATA,
    FUSEKI_LOV,
    RDF4J_GEOSCIML,
    STARDOG_LINDAS,
    STORE4_1_1_4_CHISE,
    FUSEKI2_3_8_0_STW,
])
def endpoint(request):
    return request.param


@pytest.fixture
def endpoint_config(endpoint):
    """Provide endpoint-specific configurations (prefixes and queries)"""
    if endpoint == GRAPHDB_ENTERPRISE_8_9_0:
        return {
            "prefixes": """
    PREFIX pubo: <http://ontology.ontotext.com/publishing#>
    PREFIX pub: <http://ontology.ontotext.com/taxonomy/>
    PREFIX dbr: <http://dbpedia.org/resource/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX ff-map: <http://factforge.net/ff2016-mapping/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
""",
            "select_query": """
    SELECT DISTINCT ?news ?title ?date
    {
        ?news ff-map:mentionsEntity dbr:IBM . # one can change the entity here
        ?news pubo:creationDate ?date ; pubo:title ?title .
        FILTER ( (?date > "2017-09-01"^^xsd:dateTime) && (?date < "2017-09-15"^^xsd:dateTime))
    } limit 100
""",
            "select_query_csv_tsv": """
    SELECT DISTINCT ?news ?title ?date
    {
        ?news ff-map:mentionsEntity dbr:IBM . # one can change the entity here
        ?news pubo:creationDate ?date ; pubo:title ?title .
        FILTER ( (?date > "2017-09-01"^^xsd:dateTime) && (?date < "2017-09-15"^^xsd:dateTime))
    } limit 100
""",
            "ask_query": """
    ASK { <https://weather.com/storms/typhoon/news/typhoon-talim-taiwan-japan-preps-impacts> a ?type }
""",
            "construct_query": """
    CONSTRUCT {
        _:v rdfs:label ?label .
        _:v rdfs:comment "this is only a mock node to test library"
    }
    WHERE {
        <http://dbpedia.org/resource/Asturias> rdfs:label ?label .
    }
""",
            "describe_query": """
    DESCRIBE <https://weather.com/storms/typhoon/news/typhoon-talim-taiwan-japan-preps-impacts>
"""
        }

    elif endpoint == ALLEGROGRAPH_AGROVOC:
        return {
            "prefixes": """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
""",
            "select_query": """
    SELECT ?label
    WHERE {
    <http://aims.fao.org/aos/agrovoc/c_aca7ac6d> skos:prefLabel ?label .
    }
""",
            "select_query_csv_tsv": """
    SELECT ?label ?created
    WHERE {
    <http://aims.fao.org/aos/agrovoc/c_aca7ac6d> skos:prefLabel ?label ;
        <http://purl.org/dc/terms/created> ?created
    }
""",
            "ask_query": """
    ASK { <http://aims.fao.org/aos/agrovoc/c_aca7ac6d> a ?type }
""",
            "construct_query": """
    CONSTRUCT {
        _:v skos:prefLabel ?label .
        _:v rdfs:comment "this is only a mock node to test library"
    }
    WHERE {
        <http://aims.fao.org/aos/agrovoc/c_aca7ac6d> skos:prefLabel ?label .
    }
""",
            "describe_query": """
    DESCRIBE <http://aims.fao.org/aos/agrovoc/c_aca7ac6d>
"""
        }

    elif endpoint == ALLEGROGRAPH_4_14_1_MMI:
        return {
            "prefixes": """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX ioosCat: <http://mmisw.org/ont/ioos/category/>
    PREFIX ioosPlat: <http://mmisw.org/ont/ioos/platform/>
""",
            "select_query": """
    SELECT ?p
    WHERE { ?p a ioosCat:Category }
    ORDER BY ?p
""",
            "select_query_csv_tsv": """
    SELECT DISTINCT ?cat ?platform ?definition
    WHERE {
        ?platform a ioosPlat:Platform .
        ?platform ioosPlat:Definition ?definition .
        ?cat skos:narrowMatch ?platform .
    }
    ORDER BY ?cat ?platform
""",
            "ask_query": """
    ASK { <http://mmisw.org/ont/ioos/platform/aircraft> a ?type }
""",
            "construct_query": """
    CONSTRUCT {
        _:v skos:prefLabel ?label .
        _:v rdfs:comment "this is only a mock node to test library"
    }
    WHERE {
        <http://mmisw.org/ont/ioos/platform/aircraft> rdfs:label ?label .
    }
""",
            "describe_query": """
    DESCRIBE <http://mmisw.org/ont/ioos/platform/aircraft>
"""
        }

    elif endpoint == BLAZEGRAPH_WIKIDATA:
        return {
            "prefixes": """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX entity: <http://www.wikidata.org/entity/>
""",
            "select_query": """
    SELECT ?predicate ?object WHERE {
        entity:Q3934 ?predicate ?object .
    } LIMIT 10
""",
            "select_query_csv_tsv": """
    SELECT ?predicate ?object WHERE {
        entity:Q3934 ?predicate ?object .
    } LIMIT 10
""",
            "ask_query": """
    ASK { <http://www.wikidata.org/entity/Q3934> rdfs:label "Asturias"@es }
""",
            "construct_query": """
    CONSTRUCT {
        _:v skos:prefLabel ?label .
        _:v rdfs:comment "this is only a mock node to test library"
    }
    WHERE {
        <http://www.wikidata.org/entity/Q3934> rdfs:label ?label .
        FILTER langMatches( lang(?label), "es" )
    }
""",
            "describe_query": """
    DESCRIBE <http://www.wikidata.org/entity/Q3934>
"""
        }

    elif endpoint == FUSEKI_LOV:
        return {
            "prefixes": """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX lov: <http://lov.linkeddata.es/dataset/lov/>
""",
            "select_query": """
    SELECT ?subject ?predicate ?object WHERE {
        ?subject ?predicate ?object .
    } LIMIT 10
""",
            "select_query_csv_tsv": """
    SELECT ?subject ?predicate ?object WHERE {
        ?subject ?predicate ?object .
    } LIMIT 10
""",
            "ask_query": """
    ASK { <http://lov.linkeddata.es/dataset/lov/vocabulary> a ?type }
""",
            "construct_query": """
    CONSTRUCT {
        _:v skos:prefLabel ?label .
        _:v rdfs:comment "this is only a mock node to test library"
    }
    WHERE {
        <http://lov.linkeddata.es/dataset/lov/vocabulary> rdfs:label ?label .
    }
""",
            "describe_query": """
    DESCRIBE <http://lov.linkeddata.es/dataset/lov/vocabulary>
"""
        }

    elif endpoint == RDF4J_GEOSCIML:
        return {
            "prefixes": """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
""",
            "select_query": """
    SELECT DISTINCT ?era ?label ?notation
    {
        ?era a <http://resource.geosciml.org/ontology/timescale/gts#GeochronologicEra> ;
        rdfs:label ?label ;
        skos:notation ?notation .
    } LIMIT 100
""",
            "select_query_csv_tsv": """
    SELECT DISTINCT ?era ?label ?notation
    {
        ?era a <http://resource.geosciml.org/ontology/timescale/gts#GeochronologicEra> ;
        rdfs:label ?label ;
        skos:notation ?notation .
    } LIMIT 100
""",
            "ask_query": """
    ASK { <http://resource.geosciml.org/classifier/ics/ischart/Jurassic> a ?type }
""",
            "construct_query": """
    CONSTRUCT {
        _:v rdfs:label ?label .
        _:v rdfs:comment "this is only a mock node to test library"
    }
    WHERE {
        <http://resource.geosciml.org/classifier/ics/ischart/Jurassic> rdfs:label ?label .
    }
""",
            "describe_query": """
    DESCRIBE <http://resource.geosciml.org/classifier/ics/ischart/Jurassic>
"""
        }

    elif endpoint == STARDOG_LINDAS:
        return {
            "prefixes": """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX lindas: <https://lindas.admin.ch/>
""",
            "select_query": """
    SELECT ?subject ?predicate ?object WHERE {
        ?subject ?predicate ?object .
    } LIMIT 10
""",
            "select_query_csv_tsv": """
    SELECT ?subject ?predicate ?object WHERE {
        ?subject ?predicate ?object .
    } LIMIT 10
""",
            "ask_query": """
    ASK { <https://lindas.admin.ch/resource/Example> a ?type }
""",
            "construct_query": """
    CONSTRUCT {
        _:v skos:prefLabel ?label .
        _:v rdfs:comment "this is only a mock node to test library"
    }
    WHERE {
        <https://lindas.admin.ch/resource/Example> rdfs:label ?label .
    }
""",
            "describe_query": """
    DESCRIBE <https://lindas.admin.ch/resource/Example>
"""
        }

    elif endpoint == STORE4_1_1_4_CHISE:
        return {
            "prefixes": """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
""",
            "select_query": """
    SELECT DISTINCT ?s WHERE {
         ?s a ?o .
    } LIMIT 100
""",
            "select_query_csv_tsv": """
    SELECT DISTINCT ?s ?o WHERE {
        ?s a ?o .
    } LIMIT 100
""",
            "ask_query": """
    ASK {
        ?type a <http://rdf.chise.org/rdf/type/character/ggg/super-abstract-character> .
    }
""",
            "construct_query": """
    CONSTRUCT {
        _:v rdfs:type ?type .
        _:v rdfs:comment "this is only a mock node to test library" .
    }
    WHERE {
        <http://www.chise.org/est/view/character/a2.ucs@bucs=0x5C08> rdfs:type ?type .
    }
""",
            "describe_query": """
    DESCRIBE <http://www.chise.org/est/view/character/a2.ucs@bucs=0x5C08>
"""
        }

    elif endpoint == FUSEKI2_3_8_0_STW:
        return {
            "prefixes": """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX stw: <http://zbw.eu/stw/>
""",
            "select_query": """
    SELECT ?subject ?predicate ?object WHERE {
        ?subject ?predicate ?object .
    } LIMIT 10
""",
            "select_query_csv_tsv": """
    SELECT ?subject ?predicate ?object WHERE {
        ?subject ?predicate ?object .
    } LIMIT 10
""",
            "ask_query": """
    ASK { <http://zbw.eu/stw/resource/Example> a ?type }
""",
            "construct_query": """
    CONSTRUCT {
        _:v skos:prefLabel ?label .
        _:v rdfs:comment "this is only a mock node to test library"
    }
    WHERE {
        <http://zbw.eu/stw/resource/Example> rdfs:label ?label .
    }
""",
            "describe_query": """
    DESCRIBE <http://zbw.eu/stw/resource/Example>
"""
        }

    else:
        return {
            "prefixes": """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
""",
            "select_query": """
    SELECT ?label
    WHERE {
    <http://dbpedia.org/resource/Asturias> rdfs:label ?label .
    }
""",
            "select_query_csv_tsv": """
    SELECT ?label ?wikiPageID
    WHERE {
    <http://dbpedia.org/resource/Asturias> rdfs:label ?label ;
        <http://dbpedia.org/ontology/wikiPageID> ?wikiPageID
    }
""",
            "ask_query": """
    ASK { <http://dbpedia.org/resource/Asturias> a ?type }
""",
            "construct_query": """
    CONSTRUCT {
        _:v rdfs:label ?label .
        _:v rdfs:comment "this is only a mock node to test library"
    }
    WHERE {
        <http://dbpedia.org/resource/Asturias> rdfs:label ?label .
    }
""",
            "describe_query": """
    DESCRIBE <http://dbpedia.org/resource/Asturias>
"""
        }


@pytest.fixture
def prefixes(endpoint_config):
    return endpoint_config["prefixes"]

@pytest.fixture
def select_query(endpoint_config):
    return endpoint_config["select_query"]

@pytest.fixture
def select_query_csv_tsv(endpoint_config):
    return endpoint_config["select_query_csv_tsv"]

@pytest.fixture
def ask_query(endpoint_config):
    return endpoint_config["ask_query"]

@pytest.fixture
def construct_query(endpoint_config):
    return endpoint_config["construct_query"]

@pytest.fixture
def describe_query(endpoint_config):
    return endpoint_config["describe_query"]


def query_sparql(endpoint_url, query, return_format, method, only_conneg=False) -> QueryResult | Literal[False]:
    """Generic function to make a SPARQL request and return the result"""
    sparql = SPARQLWrapper(endpoint_url)
    sparql.setQuery(query)
    sparql.setReturnFormat(return_format)
    sparql.setMethod(method)
    sparql.setOnlyConneg(only_conneg)
    try:
        result = sparql.query()
        return result
    except HTTPError as e:
        if e.code == 400:
            print("400 Bad Request, probably query is not well formed")
        elif e.code == 406:
            print("406 Not Acceptable, maybe query is not well formed")
        else:
            print(str(e))
        return False


# SELECT
@pytest.mark.parametrize("return_format", [XML, CSV, TSV, JSON, JSONLD, "foo"])
@pytest.mark.parametrize("method", [GET, POST])
@pytest.mark.parametrize("only_conneg", [True, False])
def test_select_query(endpoint, prefixes, select_query, select_query_csv_tsv, return_format, method, only_conneg):
    """Tests SELECT queries with various return formats and methods"""
    expected_type_map = {
        XML: "xml.dom.minidom.Document",
        CSV: bytes,
        TSV: bytes,
        JSON: dict,
        JSONLD: "xml.dom.minidom.Document", # Unexpected format defaults to XML
        "foo": "xml.dom.minidom.Document"   # Unknown format defaults to XML
    }
    expected_type = expected_type_map[return_format]

    if endpoint in [BLAZEGRAPH_WIKIDATA] and return_format in [CSV, TSV]:
        pytest.skip("Blazegraph does not support receiving unexpected 'format' values. csv/tsv is not a valid alias. Use content negotiation instead")
    if endpoint in [STARDOG_LINDAS] and return_format in [XML, "foo"] and not only_conneg:
        pytest.skip("Stardog fails when query params with XML return type")
    if endpoint in [GRAPHDB_ENTERPRISE_8_9_0, ALLEGROGRAPH_AGROVOC, FUSEKI_LOV, FUSEKI2_3_8_0_STW] and return_format == JSONLD:
        pytest.skip(f"{endpoint} does not support unexpected format for SELECT query type")
    if endpoint in [STORE4_1_1_4_CHISE, FUSEKI2_3_8_0_STW] and method == GET and return_format in ["foo", TSV, XML, JSONLD]:
        pytest.skip("HTTP Error 500: SPARQL protocol error, or does not support receiving unexpected output values")
    if endpoint in [STORE4_1_1_4_CHISE, FUSEKI2_3_8_0_STW] and method == POST:
        pytest.skip(f"{endpoint} fails with POST requests")
        # 4store EndPointInternalError: The endpoint returned the HTTP status code 500
        # Fuseki2 EndPointNotFound: EndPointNotFound: It was not possible to connect to the given endpoint: check it is correct.

    # Use CSV/TSV-specific query for those formats
    query = select_query_csv_tsv if return_format in [CSV, TSV] else select_query
    # Execute query and check result
    result = query_sparql(endpoint, prefixes + query, return_format, method, only_conneg)
    assert result is not False, "Query failed"

    # Check content type
    ct = result.info()["content-type"]
    if return_format == XML:
        assert any(one in ct for one in _SPARQL_XML), f"Unexpected content type: {ct}"
    elif return_format == CSV:
        assert any(one in ct for one in _CSV), f"Unexpected content type: {ct}"
    elif return_format == TSV:
        assert any(one in ct for one in _TSV), f"Unexpected content type: {ct}"
    elif return_format == JSON:
        assert any(one in ct for one in _SPARQL_JSON), f"Unexpected content type: {ct}"
    else:
        # Unknown format defaults to XML
        assert any(one in ct for one in _SPARQL_SELECT_ASK_POSSIBLE), f"Unexpected content type: {ct}"

    # Check result type
    results = result.convert()
    if isinstance(expected_type, str):
        assert results.__class__.__module__ + "." + results.__class__.__name__ == expected_type
    else:
        assert isinstance(results, expected_type)


# ASK
@pytest.mark.parametrize("return_format", [XML, CSV, TSV, JSON, N3, "foo"])
@pytest.mark.parametrize("method", [GET, POST])
@pytest.mark.parametrize("only_conneg", [True, False])
def test_ask_query(endpoint, prefixes, ask_query, return_format, method, only_conneg):
    """Tests ASK queries with various return formats and methods"""
    expected_type_map = {
        XML: "xml.dom.minidom.Document",
        CSV: bytes,
        TSV: bytes,
        JSON: dict,
        N3: "xml.dom.minidom.Document",   # Unexpected format defaults to XML
        "foo": "xml.dom.minidom.Document" # Unknown format defaults to XML
    }
    expected_type = expected_type_map[return_format]

    if endpoint in [ALLEGROGRAPH_4_14_1_MMI, GRAPHDB_ENTERPRISE_8_9_0, BLAZEGRAPH_WIKIDATA, RDF4J_GEOSCIML, STARDOG_LINDAS] and return_format in [CSV, TSV]:
        pytest.skip("CSV/TSV not supported currently for ASK query type")
    if endpoint in [STARDOG_LINDAS] and return_format in [XML, "foo"] and not only_conneg:
        pytest.skip("Stardog fails when query params with unknown return type")
    if endpoint in [VIRTUOSO_7_20_3230_dbpedia, GRAPHDB_ENTERPRISE_8_9_0, ALLEGROGRAPH_AGROVOC, FUSEKI_LOV, STORE4_1_1_4_CHISE, FUSEKI2_3_8_0_STW] and return_format in [N3]:
        pytest.skip("{endpoint} fails when unexpected return type")
    if endpoint in [STORE4_1_1_4_CHISE] and method == GET and return_format in ["foo", TSV, XML]:
        pytest.skip("HTTP Error 500: SPARQL protocol error, or does not support receiving unexpected output values")
    if endpoint in [STORE4_1_1_4_CHISE, FUSEKI2_3_8_0_STW] and (method == POST or return_format == N3):
        pytest.skip(f"{endpoint} fails with POST requests")
        # 4store EndPointInternalError: The endpoint returned the HTTP status code 500
        # Fuseki2 EndPointNotFound: EndPointNotFound: It was not possible to connect to the given endpoint: check it is correct.

    # Execute query and check result
    result = query_sparql(endpoint, prefixes + ask_query, return_format, method, only_conneg)
    assert result is not False, "Query failed"
    # Check content type
    ct = result.info()["content-type"]
    if return_format == XML:
        assert any(one in ct for one in _SPARQL_XML), f"Unexpected content type: {ct}"
    elif return_format == CSV:
        assert any(one in ct for one in _CSV), f"Unexpected content type: {ct}"
    elif return_format == TSV:
        assert any(one in ct for one in _TSV), f"Unexpected content type: {ct}"
    elif return_format == JSON:
        assert any(one in ct for one in _SPARQL_JSON), f"Unexpected content type: {ct}"
    else:
        # Unknown format defaults to XML
        assert any(one in ct for one in _SPARQL_SELECT_ASK_POSSIBLE), f"Unexpected content type: {ct}"

    # Check result type
    results = result.convert()
    if isinstance(expected_type, str):
        assert results.__class__.__module__ + "." + results.__class__.__name__ == expected_type
    else:
        assert isinstance(results, expected_type)


# CONSTRUCT
@pytest.mark.parametrize("return_format", [XML, RDFXML, TURTLE, N3, JSONLD, "foo"])
@pytest.mark.parametrize("method", [GET, POST])
@pytest.mark.parametrize("only_conneg", [True, False])
def test_construct_query(endpoint, prefixes, construct_query, return_format, method, only_conneg):
    """Tests CONSTRUCT queries with various return formats and methods"""
    expected_type_map = {
        XML: Dataset,
        RDFXML: Dataset,
        TURTLE: bytes,
        N3: bytes,
        JSONLD: Dataset,
        "foo": Dataset  # Unknown format defaults to RDFXML
    }
    expected_type = expected_type_map[return_format]

    if endpoint in [ALLEGROGRAPH_4_14_1_MMI] and return_format == JSONLD:
        pytest.skip(f"{endpoint} JSON-LD is not supported currently")
    if endpoint in [BLAZEGRAPH_WIKIDATA] and not only_conneg and return_format in [TURTLE, JSONLD, N3]:
        pytest.skip(f"{endpoint} Blazegraph does not support receiving unexpected 'format' values. Use content negotiation instead")
    if endpoint in [BLAZEGRAPH_WIKIDATA, ALLEGROGRAPH_AGROVOC, STORE4_1_1_4_CHISE, FUSEKI2_3_8_0_STW] and not only_conneg and return_format in [N3, RDFXML]:
        pytest.skip(f"{endpoint} Allegrograph fails when query params with unexpected N3 or RDFXML return type")
    if endpoint in [STORE4_1_1_4_CHISE] and method == GET and return_format in ["foo", TSV, XML, TURTLE]:
        pytest.skip("HTTP Error 500: SPARQL protocol error, or does not support receiving unexpected output values")
    if endpoint in [STORE4_1_1_4_CHISE] and return_format in [JSONLD]:
        pytest.skip("4store do not stupport JSON-LD")
    if endpoint in [STORE4_1_1_4_CHISE, FUSEKI2_3_8_0_STW] and method == POST:
        pytest.skip(f"{endpoint} fails with POST requests")
        # 4store EndPointInternalError: The endpoint returned the HTTP status code 500
        # Fuseki2 EndPointNotFound: EndPointNotFound: It was not possible to connect to the given endpoint: check it is correct.

    # Execute query and check result
    result = query_sparql(endpoint, prefixes + construct_query, return_format, method, only_conneg)
    assert result is not False, "Query failed"

    # Check content type
    ct = result.info()["content-type"]
    if return_format in [XML, RDFXML]:
        assert any(one in ct for one in _RDF_XML), f"Unexpected content type: {ct}"
    elif return_format == TURTLE:
        assert any(one in ct for one in _RDF_TURTLE), f"Unexpected content type: {ct}"
    elif return_format == N3:
        assert any(one in ct for one in _RDF_N3), f"Unexpected content type: {ct}"
    elif return_format == JSONLD:
        assert any(one in ct for one in _RDF_JSONLD), f"Unexpected content type: {ct}"
    else:
        # Unknown format
        assert any(one in ct for one in _SPARQL_DESCRIBE_CONSTRUCT_POSSIBLE), f"Unexpected content type: {ct}"

    # Check result type
    results = result.convert()
    assert isinstance(results, expected_type)


# DESCRIBE
@pytest.mark.parametrize("return_format", [XML, RDFXML, TURTLE, N3, JSONLD, CSV, "foo"])
@pytest.mark.parametrize("method", [GET, POST])
@pytest.mark.parametrize("only_conneg", [True, False])
def test_describe_query(endpoint, prefixes, describe_query, return_format, method, only_conneg):
    """Tests DESCRIBE queries with various return formats and methods"""
    expected_type_map = {
        XML: Dataset,
        RDFXML: Dataset,
        TURTLE: bytes,
        N3: bytes,
        JSONLD: Dataset,
        CSV: Dataset,   # Unexpected format defaults to RDFXML
        "foo": Dataset  # Unknown format defaults to RDFXML
    }
    expected_type = expected_type_map[return_format]

    if endpoint in [ALLEGROGRAPH_4_14_1_MMI] and return_format == JSONLD:
        pytest.skip(f"{endpoint} JSON-LD is not supported currently for AllegroGraph")
    if endpoint in [BLAZEGRAPH_WIKIDATA] and not only_conneg and return_format in [TURTLE, JSONLD, N3]:
        pytest.skip(f"{endpoint} Blazegraph does not support receiving unexpected 'format' values. Use content negotiation instead")
    if endpoint in [STORE4_1_1_4_CHISE] and method == GET and return_format in ["foo", N3, XML, TURTLE, JSONLD]:
        pytest.skip("4store only works with RDFXML when using GET with describe apparently")
    if endpoint in [VIRTUOSO_7_20_3230_dbpedia] and return_format in [JSONLD] and method == POST and not only_conneg:
        pytest.skip("{endpoint} fails when asked for JSON-LD + POST + query params")
    if endpoint in [FUSEKI2_3_8_0_STW, STORE4_1_1_4_CHISE] and return_format in [RDFXML] and method == GET and not only_conneg:
        pytest.skip("{endpoint} fails when asked for RDFXML + GET + query params")
    if endpoint in [ALLEGROGRAPH_AGROVOC] and return_format in [N3, RDFXML] and not only_conneg:
        pytest.skip("{endpoint} fails when asked for RDFXML/N3 + query params")
    if endpoint in [FUSEKI2_3_8_0_STW] and return_format in [N3]:
        pytest.skip("{endpoint} Fuseki2 fails when n3 asked")
    if endpoint in [STORE4_1_1_4_CHISE, FUSEKI2_3_8_0_STW] and method == POST:
        pytest.skip(f"{endpoint} fails with POST requests")
        # 4store EndPointInternalError: The endpoint returned the HTTP status code 500
        # Fuseki2 EndPointNotFound: EndPointNotFound: It was not possible to connect to the given endpoint: check it is correct.
    if endpoint in [VIRTUOSO_7_20_3230_dbpedia, GRAPHDB_ENTERPRISE_8_9_0, ALLEGROGRAPH_AGROVOC, FUSEKI_LOV, RDF4J_GEOSCIML, STARDOG_LINDAS, STORE4_1_1_4_CHISE, FUSEKI2_3_8_0_STW] and return_format in [CSV]:
        # TODO: is it all of them?
        pytest.skip("{endpoint} fails when unexpected return type")

    # Execute query and check result
    result = query_sparql(endpoint, prefixes + describe_query, return_format, method, only_conneg)
    assert result is not False, "Query failed"

    # Check content type
    ct = result.info()["content-type"]
    if return_format in [XML, RDFXML]:
        assert any(one in ct for one in _RDF_XML), f"Unexpected content type: {ct}"
    elif return_format == TURTLE:
        assert any(one in ct for one in _RDF_TURTLE), f"Unexpected content type: {ct}"
    elif return_format == N3:
        assert any(one in ct for one in _RDF_N3), f"Unexpected content type: {ct}"
    elif return_format == JSONLD:
        assert any(one in ct for one in _RDF_JSONLD), f"Unexpected content type: {ct}"
    else:
        # Unknown format
        assert any(one in ct for one in _SPARQL_DESCRIBE_CONSTRUCT_POSSIBLE), f"Unexpected content type: {ct}"

    # Check result type
    results = result.convert()
    assert isinstance(results, expected_type)


def test_keep_alive(endpoint):
    """Tests that the keep-alive feature works"""
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery("SELECT * WHERE {?s ?p ?o} LIMIT 10")
    sparql.setReturnFormat(JSON)
    sparql.setMethod(GET)
    sparql.setUseKeepAlive()
    # Should not raise an exception
    sparql.query()
    sparql.query()


# Special case tests
def test_query_bad_formed(endpoint):
    """Tests that malformed queries raise proper exceptions"""
    if endpoint in [FUSEKI_LOV, STARDOG_LINDAS]:
        pytest.skip(f"Skipping test for {endpoint}. ")
        # Fuseki returns 200 instead of 400 (error code present in the returned text response)
        # Stardog returns <200> code AND a MalformedQuery Error
    with pytest.raises(QueryBadFormed):
        query_sparql(endpoint, """
    PREFIX prop: <http://dbpedia.org/property/>
    PREFIX res: <http://dbpedia.org/resource/>
    FROM <http://dbpedia.org/sparql?default-graph-uri=http%3A%2F%2Fdbpedia.org&should-sponge=&query=%0D%0ACONSTRUCT+%7B%0D%0A++++%3Chttp%3A%2F%2Fdbpedia.org%2Fresource%2FBudapest%3E+%3Fp+%3Fo.%0D%0A%7D%0D%0AWHERE+%7B%0D%0A++++%3Chttp%3A%2F%2Fdbpedia.org%2Fresource%2FBudapest%3E+%3Fp+%3Fo.%0D%0A%7D%0D%0A&format=application%2Frdf%2Bxml>
    SELECT ?lat ?long
    WHERE {
        res:Budapest prop:latitude ?lat;
        prop:longitude ?long.
    }
    """, XML, GET)

def test_query_many_prefixes(endpoint) -> None:
    """Tests that queries with many prefixes work"""
    # if endpoint in [STARDOG_LINDAS, STORE4_1_1_4_CHISE]:
    #     pytest.skip(f"Skipping test for {endpoint} as it doesn't support many prefixes")
    result = query_sparql(endpoint, """
    PREFIX conf: <http://richard.cyganiak.de/2007/pubby/config.rdf#>
    PREFIX meta: <http://example.org/metadata#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX dc: <http://purl.org/dc/elements/1.1/>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
    PREFIX dbpedia: <http://dbpedia.org/resource/>
    PREFIX o: <http://dbpedia.org/ontology/>
    PREFIX p: <http://dbpedia.org/property/>
    PREFIX yago: <http://dbpedia.org/class/yago/>
    PREFIX units: <http://dbpedia.org/units/>
    PREFIX geonames: <http://www.geonames.org/ontology#>
    PREFIX prv: <http://purl.org/net/provenance/ns#>
    PREFIX prvTypes: <http://purl.org/net/provenance/types#>
    PREFIX foo: <http://purl.org/foo>

    SELECT * WHERE {
        ?subject ?predicate ?object .
    } LIMIT 10
    """, XML, GET)
    print(result)
    assert result is False or isinstance(result, QueryResult), "Query with many prefixes failed"
    # NOTE: original unittest was not checking anything, so it would only fail if uncaught exception


# https://www.w3.org/TR/2013/REC-sparql11-query-20130321/#iriRefs
# A prefix declared with the PREFIX keyword may not be re-declared in the same query.
def test_query_duplicated_prefix(endpoint):
    """Tests that queries with duplicated prefixes work"""
    if endpoint in [GRAPHDB_ENTERPRISE_8_9_0, RDF4J_GEOSCIML, BLAZEGRAPH_WIKIDATA]:
        pytest.skip(f"Skipping test for {endpoint} as it doesn't support duplicated prefixes")
    result = query_sparql(endpoint, """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?s ?p ?o WHERE {
        ?s ?p ?o .
    } LIMIT 10
    """, XML, GET)
    assert result is False or isinstance(result, QueryResult), "Query with duplicated prefixes failed"


def test_query_with_comma_in_curie_1(endpoint):
    """Tests queries with commas in CURIEs"""
    if endpoint in [VIRTUOSO_7_20_3230_dbpedia, STORE4_1_1_4_CHISE]:
        pytest.skip(f"Skipping test for {endpoint}. Returns a QueryBadFormed Error. See #94")
    result = query_sparql(endpoint, """
    PREFIX dbpedia: <http://dbpedia.org/resource/>
    SELECT ?article ?title WHERE {
        ?article ?relation dbpedia:Victoria\\,\\_British\\_Columbia .
        ?article <http://xmlns.com/foaf/0.1/isPrimaryTopicOf> ?title
    }
    """, XML, GET)
    assert result is False or isinstance(result, QueryResult), "Query with comma in CURIE failed"

def test_query_with_comma_in_uri(endpoint):
    """Tests queries with commas in URIs"""
    result = query_sparql(endpoint, """
    SELECT ?article ?title WHERE {
        ?article ?relation <http://dbpedia.org/resource/Category:Victoria,_British_Columbia> .
        ?article <http://xmlns.com/foaf/0.1/isPrimaryTopicOf> ?title
    }
    """, XML, GET)
    assert result is False or isinstance(result, QueryResult), "Query with comma in URI failed unexpectedly"

# Skipped by all endpoints anyway
# def test_query_with_comma_in_curie_2(endpoint):
#     """Tests queries with commas in CURIEs with colons"""
#     if endpoint in [VIRTUOSO_7_20_3230_dbpedia, GRAPHDB_ENTERPRISE_8_9_0, ALLEGROGRAPH_ON_HOLD_AGROVOC, ALLEGROGRAPH_4_14_1_MMI, BLAZEGRAPH_WIKIDATA, RDF4J_GEOSCIML, STARDOG_LINDAS, STORE4_1_1_4_CHISE, FUSEKI2_3_8_0_STW]:
#         pytest.skip(f"Skipping test for {endpoint}. Returns a QueryBadFormed Error. See #94")
#     result = query_sparql(endpoint, """
#     PREFIX dbpedia: <http://dbpedia.org/resource/>
#     SELECT ?article ?title WHERE {
#         ?article ?relation dbpedia:Category\:Victoria\,\_British\_Columbia .
#         ?article <http://xmlns.com/foaf/0.1/isPrimaryTopicOf> ?title
#     }
#     """, XML, GET)
#     assert result is not False, "Query with comma in CURIE with colon failed"

# def test_query_bad_formed_var_not_defined(endpoint):
#     if endpoint not in [RDF4J_GEOSCIML]:
#         pytest.skip(f"Skipping test for {endpoint} as it doesn't throw QueryBadFormed for var not defined")
#     with pytest.raises(QueryBadFormed):
#         query_sparql(endpoint, """
#         PREFIX prop: <http://dbpedia.org/property/>
#     PREFIX res: <http://dbpedia.org/resource/>
#     SELECT ?lat ?not_defined
#     WHERE {
#         res:Budapest prop:latitude ?lat .
#     }
#     """, XML, GET)
