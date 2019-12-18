=======================================
SPARQL Endpoint interface to Python
=======================================

|Build Status| |PyPi version|

About
=====

**SPARQLWrapper** is a simple Python wrapper around a `SPARQL <https://www.w3.org/TR/sparql11-overview/>`_ service to
remotelly execute your queries. It helps in creating the query
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

-  ``custom_fixers``: 2to3 custom_fixer in order to fix an issue with urllib2._opener.

Community
=========

Community support is available through the developer's discussion group `rdflib-dev <http://groups.google.com/d/forum/rdflib-dev>`_.
The `archives <http://sourceforge.net/mailarchive/forum.php?forum_name=sparql-wrapper-devel>`_. from the old mailing list are still available.

Issues
======

Please, `report any issue to github <https://github.com/RDFLib/sparqlwrapper/issues>`_.

Documentation
=============

The `SPARQLWrapper documentation is available online <https://rdflib.github.io/sparqlwrapper/doc/latest/>`_.

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
