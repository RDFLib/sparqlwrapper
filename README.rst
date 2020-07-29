.. image:: docs/source/SPARQLWrapper-250.png

=======================================
SPARQL Endpoint interface to Python
=======================================

|Build Status| |PyPi version|

About
=====

**SPARQLWrapper** is a simple Python wrapper around a `SPARQL <https://www.w3.org/TR/sparql11-overview/>`_ service to
remotely execute your queries. It helps in creating the query
invokation and, possibly, convert the result into a more manageable
format.

Installation & Distribution
===========================

You can install SPARQLWrapper from PyPi::

   $ pip install sparqlwrapper

You can install SPARQLWrapper from GitHub::

   $ pip install git+https://github.com/rdflib/sparqlwrapper#egg=sparqlwrapper

You can install SPARQLWrapper from Debian::

   $ sudo apt-get install python-sparqlwrapper
   
.. note::

   Be aware that there could be a gap between the latest version of SPARQLWrapper
   and the version available as Debian package.

Also, the source code of the package can be downloaded 
in ``.zip`` and ``.tar.gz`` formats from `GitHub SPARQLWrapper releases <https://github.com/RDFLib/sparqlwrapper/releases>`_.
Documentation is included in the distribution.


How to use
==========


First steps
-----------

The simplest usage of this module looks as follows (using the default, ie, `XML return format <http://www.w3.org/TR/rdf-sparql-XMLres/>`_, and special URI for the
SPARQL Service)::

 from SPARQLWrapper import SPARQLWrapper
 
 queryString = "SELECT * WHERE { ?s ?p ?o. }"
 sparql = SPARQLWrapper("http://example.org/sparql")
 
 sparql.setQuery(queryString)
 
 try :
    ret = sparql.query()
    # ret is a stream with the results in XML, see <http://www.w3.org/TR/rdf-sparql-XMLres/>
 except :
    deal_with_the_exception()

If ``SPARQLWrapper("http://example.org/sparql",returnFormat=SPARQLWrapper.JSON)`` was used, the result would be in
`JSON format <http://www.w3.org/TR/rdf-sparql-json-res/>`_ instead of XML.


SELECT example
--------------

.. code:: python

   from SPARQLWrapper import SPARQLWrapper, JSON

   sparql = SPARQLWrapper("http://dbpedia.org/sparql")
   sparql.setQuery("""
       PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
       SELECT ?label
       WHERE { <http://dbpedia.org/resource/Asturias> rdfs:label ?label }
   """)
   sparql.setReturnFormat(JSON)
   results = sparql.query().convert()

   for result in results["results"]["bindings"]:
       print(result["label"]["value"])
   
   print('---------------------------')
   
   for result in results["results"]["bindings"]:
       print('%s: %s' % (result["label"]["xml:lang"], result["label"]["value"]))

ASK example
-----------

.. code:: python

   from SPARQLWrapper import SPARQLWrapper, XML

   sparql = SPARQLWrapper("http://dbpedia.org/sparql")
   sparql.setQuery("""
       ASK WHERE { 
           <http://dbpedia.org/resource/Asturias> rdfs:label "Asturias"@es
       }    
   """)
   sparql.setReturnFormat(XML)
   results = sparql.query().convert()
   print(results.toxml())

CONSTRUCT example
-----------------

.. code:: python

   from SPARQLWrapper import SPARQLWrapper, RDFXML
   from rdflib import Graph

   sparql = SPARQLWrapper("http://dbpedia.org/sparql")

   sparql.setQuery("""
       PREFIX dbo: <http://dbpedia.org/ontology/>
       PREFIX schema: <http://schema.org/>
       
       CONSTRUCT {
         ?lang a schema:Language ;
         schema:alternateName ?iso6391Code . 
       }
       WHERE {
         ?lang a dbo:Language ;
         dbo:iso6391Code ?iso6391Code .
         FILTER (STRLEN(?iso6391Code)=2) # to filter out non-valid values
       }
   """)

   sparql.setReturnFormat(RDFXML)
   results = sparql.query().convert()
   print(results.serialize(format='xml'))

DESCRIBE example
----------------

.. code:: python

   from SPARQLWrapper import SPARQLWrapper, N3
   from rdflib import Graph

   sparql = SPARQLWrapper("http://dbpedia.org/sparql")

   sparql.setQuery("""
       DESCRIBE <http://dbpedia.org/resource/Asturias>
   """)

   sparql.setReturnFormat(N3)
   results = sparql.query().convert()
   g = Graph()
   g.parse(data=results, format="n3")
   print(g.serialize(format='n3'))

SPARQL UPDATE example
---------------------

.. code:: python

   from SPARQLWrapper import SPARQLWrapper, POST, DIGEST

   sparql = SPARQLWrapper("https://example.org/sparql-auth")

   sparql.setHTTPAuth(DIGEST)
   sparql.setCredentials("login", "password")
   sparql.setMethod(POST)

   sparql.setQuery("""
   WITH <http://example.graph>
   DELETE
   { <http://dbpedia.org/resource/Asturias> rdfs:label "Asturies"@ast }
   """)

   results = sparql.query()
   print results.response.read()
   
SPARQLWrapper2 example
----------------------

There is also a ``SPARQLWrapper2`` class that works with JSON SELECT
results only and wraps the results to make processing of average queries
a bit simpler.

.. code:: python

   from SPARQLWrapper import SPARQLWrapper2

   sparql = SPARQLWrapper2("http://dbpedia.org/sparql")
   sparql.setQuery("""
       PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
       SELECT ?label
       WHERE { <http://dbpedia.org/resource/Asturias> rdfs:label ?label }
   """)

   for result in sparql.query().bindings:
       print('%s: %s' % (result["label"].lang, result["label"].value))

Return formats
------------------------

The expected return formats differs from the query type (``SELECT``, ``ASK``, ``CONSTRUCT``, ``DESCRIBE``...).

.. note:: From the `SPARQL specification <https://www.w3.org/TR/sparql11-protocol/#query-success>`_, 
  *The response body of a successful query operation with a 2XX response is either:*

  * ``SELECT`` and ``ASK``: a SPARQL Results Document in XML, JSON, or CSV/TSV format.
  * ``DESCRIBE`` and ``CONSTRUCT``: an RDF graph serialized, for example, in the RDF/XML syntax, or an equivalent RDF graph serialization.

The package, though it does not contain a full SPARQL parser, makes an attempt to determine the query type
when the query is set. This should work in most of the cases (but there is a possibility to set this manually, in case something
goes wrong).

Automatic conversion of the results
-----------------------------------

To make processing somewhat easier, the package can do some conversions automatically from the return result. These are:

* for XML, the `xml.dom.minidom <http://docs.python.org/library/xml.dom.minidom.html>`_ is used to convert the result stream into a ``Python representation of a DOM tree``.
* for JSON, the `json <https://docs.python.org/library/json.html>`_ package to generate a ``Python dictionary``. Until version 1.3.1, the `simplejson <https://pypi.python.org/pypi/simplejson>`_ package was used.
* for CSV or TSV, a simple ``string``.
* For RDF/XML and JSON-LD, the `RDFLib <https://rdflib.readthedocs.io>`_ package is used to convert the result into a ``Graph`` instance.
* For RDF Turtle/N3, a simple ``string``.


There are two ways to generate this conversion:

* use ``ret.convert()`` in the return result from ``sparql.query()`` in the code above
* use ``sparql.queryAndConvert()`` to get the converted result right away if the intermediate stream is not used


For example, in the code below::

 try :
     sparql.setReturnFormat(SPARQLWrapper.JSON)
     ret = sparql.query()
     dict = ret.convert()
 except:
     deal_with_the_exception()


the value of ``dict`` is a Python dictionary of the query result, based on the `SPARQL Query Results JSON Format <http://www.w3.org/TR/rdf-sparql-json-res/>`_.


Partial interpretation of the results
-------------------------------------

A further help is to offer an extra, partial interpretation of the results, again to cover
most of the practical use cases.
Based on the `SPARQL Query Results JSON Format <http://www.w3.org/TR/rdf-sparql-json-res/>`_, the :class:`SPARQLWrapper.SmartWrapper.Bindings` class
can perform some simple steps in decoding the JSON return results. If :class:`SPARQLWrapper.SmartWrapper.SPARQLWrapper2`
is used instead of :class:`SPARQLWrapper.Wrapper.SPARQLWrapper`, this result format is generated. Note that this relies on a JSON format only,
ie, it has to be checked whether the SPARQL service can return JSON or not.

Here is a simple code that makes use of this feature::

 from SPARQLWrapper import SPARQLWrapper2
 
 queryString = "SELECT ?subj ?prop WHERE { ?subj ?prop ?o. }"
 
 sparql = SPARQLWrapper2("http://example.org/sparql")

 sparql.setQuery(queryString)
 try :
     ret = sparql.query()
     print ret.variables  # this is an array consisting of "subj" and "prop"
     for binding in ret.bindings :
         # each binding is a dictionary. Let us just print the results
         print "%s: %s (of type %s)" % ("s",binding[u"subj"].value,binding[u"subj"].type)
         print "%s: %s (of type %s)" % ("p",binding[u"prop"].value,binding[u"prop"].type)
 except:
     deal_with_the_exception()

To make this type of code even easier to realize, the ``[]`` and ``in`` operators are also implemented
on the result of :class:`SPARQLWrapper.SmartWrapper.Bindings`. This can be used to check and find a particular binding (ie, particular row
in the return value). This features becomes particularly useful when the ``OPTIONAL`` feature of SPARQL is used. For example::

 from SPARQLWrapper import SPARQLWrapper2
 
 queryString = "SELECT ?subj ?o ?opt WHERE { ?subj <http://a.b.c> ?o. OPTIONAL { ?subj <http://d.e.f> ?opt }}"
 
 sparql = SPARQLWrapper2("http://example.org/sparql")

 sparql.setQuery(queryString)
 try :
     ret = sparql.query()
     print ret.variables  # this is an array consisting of "subj", "o", "opt"
     if (u"subj",u"prop",u"opt") in ret :
        # there is at least one binding covering the optional "opt", too
        bindings = ret[u"subj",u"o",u"opt"]
        # bindings is an array of dictionaries with the full bindings
        for b in bindings :
            subj = b[u"subj"].value
            o    = b[u"o"].value
            opt  = b[u"opt"].value
            # do something nice with subj, o, and opt
     # another way of accessing to values for a single variable:
     # take all the bindings of the "subj"
     subjbind = ret.getValues(u"subj") # an array of Value instances
     ...
 except:
     deal_with_the_exception()


GET or POST
-----------

By default, all SPARQL services are invoked using HTTP **GET** verb. However, 
**POST** might be useful if the size of the query
extends a reasonable size; this can be set in the query instance.

Note that some combination may not work yet with all SPARQL processors
(e.g., there are implementations where **POST + JSON return** does not work). 
Hopefully, this problem will eventually disappear.


Database management systems
===========================

Introduction
------------

From `SPARQL 1.1 Specification <https://www.w3.org/TR/sparql11-protocol/#query-success>`_:

The response body of a successful query operation with a 2XX response is either:

- `SELECT` and `ASK`: a SPARQL Results Document in XML, JSON, or CSV/TSV format.
- `DESCRIBE` and `CONSTRUCT`: an **RDF graph serialized**, for example, in the RDF/XML syntax, or an equivalent RDF graph serialization.


The fact is that the **parameter key** for the choice of the **output format** is not defined.
Virtuoso uses `format`, joseki/fuseki uses `output`, rasqual seems to use `results`, etc...
Also, in some cases HTTP Content Negotiation can/must be used.


ClioPatria
----------
:Website: `The SWI-Prolog Semantic Web Server <http://cliopatria.swi-prolog.org/home>`_
:Documentation: Search 'sparql' in `<http://cliopatria.swi-prolog.org/help/http>`_.
:Uses: Parameters **and** Content Negotiation.
:Parameter key: ``format``.
:Parameter value: MUST be one of these values: ``rdf+xml``, ``json``, ``csv``, ``application/sparql-results+xml`` or ``application/sparql-results+json``.


OpenLink Virtuoso
-----------------
:Website: `OpenLink Virtuoso <http://virtuoso.openlinksw.com>`_
:Parameter key: ``format`` or ``output``.
:JSON-LD (application/ld+json): supported (in CONSTRUCT and DESCRIBE).

- Parameter value, like directly: "text/html" (HTML), "text/x-html+tr" (HTML (Faceted Browsing Links)), "application/vnd.ms-excel",
  "application/sparql-results+xml" (XML), "application/sparql-results+json" (JSON), "application/javascript" (Javascript), "text/turtle" (Turtle), "application/rdf+xml" (RDF/XML),
  "text/plain" (N-Triples), "text/csv" (CSV), "text/tab-separated-values" (TSV)
- Parameter value, like indirectly:
  "HTML" (alias text/html), "JSON" (alias application/sparql-results+json), "XML" (alias application/sparql-results+xml), "TURTLE" (alias text/rdf+n3), JavaScript (alias application/javascript)
  See `<http://virtuoso.openlinksw.com/dataspace/doc/dav/wiki/Main/VOSSparqlProtocol#Additional HTTP Response Formats -- SELECT>`_

- For a ``SELECT`` query type, the default return mimetype (if ``Accept: */*`` is sent) is ``application/sparql-results+xml``
- For a ``ASK`` query type, the default return mimetype (if ``Accept: */*`` is sent) is ``text/html``
- For a ``CONSTRUCT`` query type, the default return mimetype (if ``Accept: */*`` is sent) is ``text/turtle``
- For a ``DESCRIBE`` query type, the default return mimetype (if ``Accept: */*`` is sent) is ``text/turtle``


Fuseki
------
:Website: `Fuseki (formerly there was Joseki) <https://jena.apache.org/documentation/serving_data/>`_
:Uses: Parameters **and** Content Negotiation.
:Parameter key: ``format`` or ``output`` (`Fuseki 1 <https://github.com/apache/jena/blob/master/jena-fuseki1/src/main/java/org/apache/jena/fuseki/HttpNames.java>`_, `Fuseki 2 <https://github.com/apache/jena/blob/master/jena-arq/src/main/java/org/apache/jena/riot/web/HttpNames.java>`_).
:JSON-LD (application/ld+json): supported (in CONSTRUCT and DESCRIBE).

- `Fuseki 1 - Short names for "output=" : "json", "xml", "sparql", "text", "csv", "tsv", "thrift" <https://github.com/apache/jena/blob/master/jena-fuseki1/src/main/java/org/apache/jena/fuseki/servlets/ResponseResultSet.java>`_
- `Fuseki 2 - Short names for "output=" : "json", "xml", "sparql", "text", "csv", "tsv", "thrift" <https://github.com/apache/jena/blob/master/jena-fuseki2/jena-fuseki-core/src/main/java/org/apache/jena/fuseki/servlets/ResponseResultSet.java>`_
- If a non-expected short name is used, the server returns an "Error 400: Can't determine output serialization"
- Valid alias for SELECT and ASK: "json", "xml", csv", "tsv"
- Valid alias for DESCRIBE and CONSTRUCT: "json" (alias for json-ld ONLY in Fuseki 2), "xml"
- Valid mimetype for DESCRIBE and CONSTRUCT: "application/ld+json"
- Default return mimetypes: For a SELECT and ASK query types, the default return mimetype (if Accept: */* is sent) is application/sparql-results+json
- Default return mimetypes: For a DESCRIBE and CONTRUCT query types, the default return mimetype (if Accept: */* is sent) is text/turtle
- In case of a bad formed query, Fuseki 1 returns 200 instead of 400.


Eclipse RDF4J
-------------
:Website: `Eclipse RDF4J (formerly known as OpenRDF Sesame) <http://rdf4j.org/>`_
:Documentation: `<https://rdf4j.eclipse.org/documentation/rest-api/#the-query-operation>`_, `<https://rdf4j.eclipse.org/documentation/rest-api/#content-types>`_
:Uses: Only content negotiation (no URL parameters).
:Parameter: If an unexpected parameter is used, the server ignores it.
:JSON-LD (application/ld+json): supported (in CONSTRUCT and DESCRIBE).

- SELECT

  - ``application/sparql-results+xml`` (DEFAULT if ``Accept: */*`` is sent))
  - ``application/sparql-results+json`` (also ``application/json``)
  - ``text/csv``
  - ``text/tab-separated-values``
  - Other values: ``application/x-binary-rdf-results-table``

- ASK

  - ``application/sparql-results+xml`` (DEFAULT if ``Accept: */*`` is sent))
  - ``application/sparql-results+json``
  - Other values: ``text/boolean``
  - **Not supported**: ``text/csv``
  - **Not supported**: ``text/tab-separated-values``

- CONSTRUCT

  - ``application/rdf+xml``
  - ``application/n-triples`` (DEFAULT if ``Accept: */*`` is sent)
  - ``text/turtle``
  - ``text/n3``
  - ``application/ld+json``
  - Other acceptable values: ``application/n-quads``, ``application/rdf+json``, ``application/trig``, ``application/trix``, ``application/x-binary-rdf``
  - ``text/plain`` (returns ``application/n-triples``)
  - ``text/rdf+n3`` (returns ``text/n3``)
  - ``text/x-nquads`` (returns ``application/n-quads``)

- DESCRIBE

  - ``application/rdf+xml``
  - ``application/n-triples`` (DEFAULT if ``Accept: */*`` is sent)
  - ``text/turtle``
  - ``text/n3``
  - ``application/ld+json``
  - Other acceptable values: ``application/n-quads``, ``application/rdf+json``, ``application/trig``, ``application/trix``, ``application/x-binary-rdf``
  - ``text/plain`` (returns ``application/n-triples``)
  - ``text/rdf+n3`` (returns ``text/n3``)
  - ``text/x-nquads`` (returns ``application/n-quads``)


RASQAL
------
:Website: `RASQAL <http://librdf.org/rasqal/>`_
:Documentation: `<http://librdf.org/rasqal/roqet.html>`_
:Parameter key: ``results``.
:JSON-LD (application/ld+json): NOT supported.

Uses roqet as RDF query utility (see `<http://librdf.org/rasqal/roqet.html>`_)
For variable bindings, the values of FORMAT vary upon what Rasqal supports but include simple
for a simple text format (default), xml for the SPARQL Query Results XML format, csv for SPARQL CSV,
tsv for SPARQL TSV, rdfxml and turtle for RDF syntax formats, and json for a JSON version of the results.

For RDF graph results, the values of FORMAT are ntriples (N-Triples, default),
rdfxml-abbrev (RDF/XML Abbreviated), rdfxml (RDF/XML), turtle (Turtle),
json (RDF/JSON resource centric), json-triples (RDF/JSON triples) or
rss-1.0 (RSS 1.0, also an RDF/XML syntax).


Marklogic
---------
:Website: `Marklogic <http://marklogic.com>`_
:Uses: Only content negotiation (no URL parameters).
:JSON-LD (application/ld+json): NOT supported.

`You can use following methods to query triples <https://docs.marklogic.com/guide/semantics/semantic-searches#chapter>`_:

- SPARQL mode in Query Console. For details, see Querying Triples with SPARQL
- XQuery using the semantics functions, and Search API, or a combination of XQuery and SPARQL. For details, see Querying Triples with XQuery or JavaScript.
- HTTP via a SPARQL endpoint. For details, see Using Semantics with the REST Client API.

`Formats are specified as part of the HTTP Accept headers of the REST request. <https://docs.marklogic.com/guide/semantics/REST#id_92428>`_
When you query the SPARQL endpoint with REST Client APIs, you can specify the result output format (See `<https://docs.marklogic.com/guide/semantics/REST#id_54258>`_. The response type format depends on the type of query and the MIME type in the HTTP Accept header.

This table describes the MIME types and Accept Header/Output formats (MIME type) for different types of SPARQL queries. (See `<https://docs.marklogic.com/guide/semantics/REST#id_54258>`_ and `<https://docs.marklogic.com/guide/semantics/loading#id_70682>`_)

- SELECT

  - application/sparql-results+xml
  - application/sparql-results+json
  - text/html
  - text/csv

- ASK queries return a boolean (true or false).

- CONSTRUCT or DESCRIBE

  - application/n-triples
  - application/rdf+json
  - application/rdf+xml
  - text/turtle
  - text/n3
  - application/n-quads
  - application/trig


AllegroGraph
------------
:Website: `AllegroGraph <https://franz.com/agraph/allegrograph/>`_
:Documentation: `<https://franz.com/agraph/support/documentation/current/http-protocol.html>`_
:Uses: Only content negotiation (no URL parameters).
:Parameter: The server always looks at the Accept header of a request, and tries to
  generate a response in the format that the client asks for. If this fails,
  a 406 response is returned. When no Accept, or an Accept of */* is specified,
  the server prefers text/plain, in order to make it easy to explore the interface from a web browser.
:JSON-LD (application/ld+json): NOT supported.


- SELECT

  - application/sparql-results+xml (DEFAULT if Accept: */* is sent)
  - application/sparql-results+json (and application/json)
  - text/csv
  - text/tab-separated-values
  - OTHERS: application/sparql-results+ttl, text/integer, application/x-lisp-structured-expression, text/table, application/processed-csv, text/simple-csv, application/x-direct-upis

- ASK

  - application/sparql-results+xml (DEFAULT if Accept: */* is sent)
  - application/sparql-results+json (and application/json)
  - Not supported: text/csv
  - Not supported: text/tab-separated-values

- CONSTRUCT

  - application/rdf+xml (DEFAULT if Accept: */* is sent)
  - text/rdf+n3
  - OTHERS: text/integer, application/json, text/plain, text/x-nquads, application/trix, text/table, application/x-direct-upis

- DESCRIBE

  - application/rdf+xml (DEFAULT if Accept: */* is sent)
  - text/rdf+n3


4store
------
:Website: `4store <https://github.com/4store/4store>`_
:Documentation: `<https://4store.danielknoell.de/trac/wiki/SparqlServer/>`_
:Uses: Parameters **and** Content Negotiation.
:Parameter key: ``output``.
:Parameter value: alias. If an unexpected alias is used, the server is not working properly.
:JSON-LD (application/ld+json): NOT supported.


- SELECT

  - application/sparql-results+xml (alias xml) (DEFAULT if Accept: */* is sent))
  - application/sparql-results+json or application/json (alias json)
  - text/csv (alias csv)
  - text/tab-separated-values (alias tsv). Returns "text/plain" in GET.
  - Other values: text/plain, application/n-triples

- ASK

  - application/sparql-results+xml (alias xml) (DEFAULT if Accept: */* is sent))
  - application/sparql-results+json or application/json (alias json)
  - text/csv (alias csv)
  - text/tab-separated-values (alias tsv). Returns "text/plain" in GET.
  - Other values: text/plain, application/n-triples

- CONSTRUCT

  - application/rdf+xml (alias xml) (DEFAULT if Accept: */* is sent)
  - text/turtle (alias "text")

- DESCRIBE

  - application/rdf+xml (alias xml) (DEFAULT if Accept: */* is sent)
  - text/turtle (alias "text")

:Valid alias for SELECT and ASK: "json", "xml", csv", "tsv" (also "text" and "ascii")
:Valid alias for DESCRIBE and CONSTRUCT: "xml", "text" (for turtle)


Blazegraph
----------
:Website: `Blazegraph (Formerly known as Bigdata) <https://www.blazegraph.com/>`_ & `NanoSparqlServer <https://wiki.blazegraph.com/wiki/index.php/NanoSparqlServer>`_
:Documentation: `<https://wiki.blazegraph.com/wiki/index.php/REST_API#SPARQL_End_Point>`_
:Uses: Parameters **and** Content Negotiation.
:Parameter key: ``format`` (available since version 1.4.0). `Setting this parameter will override any Accept Header that is present <https://wiki.blazegraph.com/wiki/index.php/REST_API#GET_or_POST>`_
:Parameter value: alias. If an unexpected alias is used, the server is not working properly.
:JSON-LD (application/ld+json): NOT supported.

- SELECT

  - application/sparql-results+xml (alias xml) (DEFAULT if Accept: */* is sent))
  - application/sparql-results+json or application/json (alias json)
  - text/csv
  - text/tab-separated-values
  - Other values: application/x-binary-rdf-results-table

- ASK

  - application/sparql-results+xml (alias xml) (DEFAULT if Accept: */* is sent))
  - application/sparql-results+json or application/json (alias json)

- CONSTRUCT

  - application/rdf+xml (alias xml) (DEFAULT if Accept: */* is sent)
  - text/turtle (returns text/n3)
  - text/n3

- DESCRIBE

  - application/rdf+xml (alias xml) (DEFAULT if Accept: */* is sent)
  - text/turtle (returns text/n3)
  - text/n3

:Valid alias for SELECT and ASK: "xml", "json"
:Valid alias for DESCRIBE and CONSTRUCT: "xml", "json" (but it returns unexpected "application/sparql-results+json")


GraphDB
-------
:Website: `GraphDB, formerly known as OWLIM (OWLIM-Lite, OWLIM-SE) <http://graphdb.ontotext.com/>`_
:Documentation: `<http://graphdb.ontotext.com/documentation/free/>`_
:Uses: Only content negotiation (no URL parameters).
:Note: If the Accept value is not within the expected ones, the server returns a 406 "No acceptable file format found."
:JSON-LD (application/ld+json): supported (in CONSTRUCT and DESCRIBE).

- SELECT

  - application/sparql-results+xml, application/xml (.srx file)
  - application/sparql-results+json, application/json (.srj file)
  - text/csv (DEFAULT if Accept: */* is sent)
  - text/tab-separated-values

- ASK

  - application/sparql-results+xml, application/xml (.srx file)
  - application/sparql-results+json (DEFAULT if Accept: */* is sent), application/json (.srj file)
  - NOT supported: text/csv, text/tab-separated-values

- CONSTRUCT

  - application/rdf+xml, application/xml (.rdf file)
  - text/turtle (.ttl file)
  - application/n-triples (.nt file) (DEFAULT if Accept: */* is sent)
  - text/n3, text/rdf+n3 (.n3 file)
  - application/ld+json (.jsonld file)

- DESCRIBE

  - application/rdf+xml, application/xml (.rdf file)
  - text/turtle (.ttl file)
  - application/n-triples (.nt file) (DEFAULT if Accept: */* is sent)
  - text/n3, text/rdf+n3 (.n3 file)
  - application/ld+json (.jsonld file)


Stardog
-------
:Website: `Stardog <https://www.stardog.com>`_
:Documentation: `<https://www.stardog.com/docs/#_http_headers_content_type_accept>`_ (looks outdated)
:Uses: Only content negotiation (no URL parameters).
:Parameter key: If an unexpected parameter is used, the server ignores it.
:JSON-LD (application/ld+json): supported (in CONSTRUCT and DESCRIBE).


- SELECT

  - application/sparql-results+xml (DEFAULT if Accept: */* is sent)
  - application/sparql-results+json
  - text/csv
  - text/tab-separated-values
  - Other values: application/x-binary-rdf-results-table

- ASK

  - application/sparql-results+xml (DEFAULT if Accept: */* is sent)
  - application/sparql-results+json
  - Other values: text/boolean
  - Not supported: text/csv
  - Not supported: text/tab-separated-values

- CONSTRUCT

  - application/rdf+xml
  - text/turtle (DEFAULT if Accept: */* is sent)
  - text/n3
  - application/ld+json
  - Other acceptable values: application/n-triples, application/x-turtle, application/trig, application/trix, application/n-quads

- DESCRIBE

  - application/rdf+xml
  - text/turtle (DEFAULT if Accept: */* is sent)
  - text/n3
  - application/ld+json
  - Other acceptable values: application/n-triples, application/x-turtle, application/trig, application/trix, application/n-quads


Development
===========

Requirements
------------

The `RDFLib <https://rdflib.readthedocs.io>`_ package is used for RDF parsing.

This package is imported in a lazy fashion, ie, only when needed. Ie, if the user never intends to use the
RDF format, the RDFLib package is not imported and the user does not have to install it.

Source code
-----------

The source distribution contains:

-  ``SPARQLWrapper``: the Python package. You should copy the directory
   somewhere into your PYTHONPATH. Alternatively, you can also run
   the distutils scripts: ``python setup.py install``

-  ``test``: some unit and integrations tests. In order to run the tests 
   some packages have to be installed before. So please install the packages 
   listed in requirements.development.txt:
   ``pip install -r requirements.development.txt``

-  ``scripts``: some scripts to run the package against some SPARQL endpoints.

-  ``docs``: the documentation.

Community
=========

Community support is available through the developer's discussion group `rdflib-dev <http://groups.google.com/d/forum/rdflib-dev>`_.
The `archives <http://sourceforge.net/mailarchive/forum.php?forum_name=sparql-wrapper-devel>`_. from the old mailing list are still available.

Issues
======

Please, `report any issue to github <https://github.com/RDFLib/sparqlwrapper/issues>`_.

Documentation
=============

The `SPARQLWrapper documentation is available online <https://sparqlwrapper.readthedocs.io>`_.

Other interesting documents are the latest `SPARQL 1.1 Specification (W3C Recommendation 21 March 2013) <https://www.w3.org/TR/sparql11-overview/>`_
and the initial `SPARQL Specification (W3C Recommendation 15 January 2008) <http://www.w3.org/TR/rdf-sparql-query/>`_.


License
=======

The SPARQLWrapper package is licensed under `W3C license`_.

.. _W3C license: https://www.w3.org/Consortium/Legal/2015/copyright-software-and-document


Acknowledgement
===============

The package was greatly inspired by `Lee Feigenbaum's similar package for Javascript <http://thefigtrees.net/lee/blog/2006/04/sparql_calendar_demo_a_sparql.html>`_.

Developers involved:

* Ivan Herman <http://www.ivan-herman.net>
* Sergio Fernández <http://www.wikier.org>
* Carlos Tejo Alonso <http://www.dayures.net>
* Alexey Zakhlestin <https://indeyets.ru/>

Organizations involved:

* `World Wide Web Consortium <http://www.w3.org>`_
* `Salzburg Research <http://www.salzburgresearch.at>`_
* `Foundation CTIC <http://www.fundacionctic.org/>`_


.. |Build Status| image:: https://secure.travis-ci.org/RDFLib/sparqlwrapper.svg?branch=master
   :target: https://travis-ci.org/RDFLib/sparqlwrapper
.. |PyPi version| image:: https://badge.fury.io/py/SPARQLWrapper.svg
   :target: https://pypi.python.org/pypi/SPARQLWrapper
