# -*- coding: utf8 -*-

u"""

This is a wrapper around a SPARQL service. It helps in creating the query URI and,
possibly, convert the result into a more managable format.

The following packages are used:

  - for JSON, the U{simplejson<http://cheeseshop.python.org/pypi/simplejson>} package: C{http://cheeseshop.python.org/pypi/simplejson}
  - for RDF/XML, the U{RDFLib<http://rdflib.net>}: C{http://rdflib.net}

These packages are imported in a lazy fashion, ie, only when needed. Ie, if the user never intends to use the
JSON format, the C{simplejson} package is not imported and the user does not have to install it.

The package can be downloaded in C{zip} and C{.tar.gz} formats from
U{http://www.ivan-herman.net/Misc/PythonStuff/SPARQL/<http://www.ivan-herman.net/Misc/PythonStuff/SPARQL/>}. It is also
available from U{Sourceforge<https://sourceforge.net/projects/sparql-wrapper/>} under the project named "C{sparql-wrapper}".
Documentation is included in the distribution.


Basic QUERY Usage
=================

Simple query
------------

The simplest usage of this module looks as follows (using the default, ie, U{XML return format<http://www.w3.org/TR/rdf-sparql-XMLres/>}, and special URI for the
SPARQL Service)::

 from SPARQLWrapper import SPARQLWrapper
 queryString = "SELECT * WHERE { ?s ?p ?o. }"
 sparql = SPARQLWrapper("http://localhost:2020/sparql")
 # add a default graph, though that can also be part of the query string
 sparql.addDefaultGraph("http://www.example.com/data.rdf")
 sparql.setQuery(queryString)
 try :
    ret = sparql.query()
    # ret is a stream with the results in XML, see <http://www.w3.org/TR/rdf-sparql-XMLres/>
 except :
    deal_with_the_exception()

If C{SPARQLWrapper("http://localhost:2020/sparql",returnFormat=SPARQLWrapper.JSON)} was used, the result would be in
U{JSON format<http://www.w3.org/TR/rdf-sparql-json-res/>} instead of XML (provided the sparql
processor can return JSON).

Automatic conversion of the results
-----------------------------------

To make processing somewhat easier, the package can do some conversions automatically from the return result. These are:

  - for XML, the U{xml.dom.minidom<http://docs.python.org/library/xml.dom.minidom.html>} (C{http://docs.python.org/library/xml.dom.minidom.html}) is
  used to convert the result stream into a Python representation of a DOM tree
  - for JSON, the U{simplejson<http://cheeseshop.python.org/pypi/simplejson>} package (C{http://cheeseshop.python.org/pypi/simplejson}) to generate a Python dictionary

There are two ways to generate this conversion:

 - use C{ret.convert()} in the return result from C{sparql.query()} in the code above
 - use C{sparql.queryAndConvert()} to get the converted result right away if the intermediate stream is not used

For example, in the code below::
 try :
     sparql.setReturnFormat(SPARQLWrapper.JSON)
     ret = sparql.query()
     dict = ret.convert()
 except:
     deal_with_the_exception()
the value of C{dict} is a Python dictionary of the query result, based on the U{JSON format<http://www.w3.org/TR/rdf-sparql-json-res/>}.

The L{SPARQLWrapper} class can be subclassed by overriding the conversion routines if the user wants to use something else.

Partial interpretation of the results
-------------------------------------

A further help is to offer an extra, partial interpretation of the results, again to cover
most of the practical use cases.
Based on the  U{JSON format<http://www.w3.org/TR/rdf-sparql-json-res/>}, the L{SmartWrapper.Bindings} class
can perform some simple steps in decoding the JSON return results. If L{SPARQLWrapper2}
is used instead of L{SPARQLWrapper}, this result format is generated. Note that this relies on a JSON format only,
ie, it has to be checked whether the SPARQL service can return JSON or not.

Here is a simple code that makes use of this feature::

 from SPARQLWrapper import SPARQLWrapper2
 queryString = "SELECT ?subj ?prop WHERE { ?subj ?prop ?o. }"
 sparql = SPARQLWrapper2("http://localhost:2020/sparql")
 # add a default graph, though that can also be in the query string
 sparql.addDefaultGraph("http://www.example.com/data.rdf")
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

To make this type of code even easier to realize, the C{[]} and C{in} operators are also implemented
on the result of L{SmartWrapper.Bindings}. This can be used to check and find a particular binding (ie, particular row
in the return value). This features becomes particularly useful when the C{OPTIONAL} feature of SPARQL is used. For example::

 from SPARQLWrapper import SPARQLWrapper2
 queryString = "SELECT ?subj ?o ?opt WHERE { ?subj <http://a.b.c> ?o. OPTIONAL { ?subj <http://d.e.f> ?opt }}"
 sparql = SPARQLWrapper2("http://localhost:2020/sparql")
 # add a default graph, though that can also be in the query string
 sparql.addDefaultGraph("http://www.example.com/data.rdf")
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


CONSTRUCT, ASK, DESCRIBE
========================

All the examples so far were based on the SELECT queries. If the query includes, eg, the C{CONSTRUCT} keyword then the accepted
return formats should be different: eg, C{SPARQLWrapper.XML} means C{RDF/XML} and most of the SPARQL engines can also return the 
results in C{Turtle}. The package, though it does not contain a full SPARQL parser, makes an attempt to determine the query type 
when the query is set. This should work in most of the cases (but there is a possibility to set this manually, in case something 
goes wrong).

For RDF/XML, the U{RDFLib<http://rdflib.net>} (C{http://rdflib.net}) package is used to convert the result into a C{Graph} instance.

GET or POST
===========

By default, all SPARQL services are invoked using HTTP GET. However, POST might be useful if the size of the query
extends a reasonable size; this can be set in the query instance.

Note that some combination may not work yet with all SPARQL processors
(eg, there are implementations where POST+JSON return does not work). Hopefully, this problem will eventually disappear.

Note that SPARQLWrapper only supports nowadays query using POST via URL-encoded.

Acknowledgement
===============

The package was greatly inspired by U{Lee Feigenbaum's similar package for Javascript<http://thefigtrees.net/lee/blog/2006/04/sparql_calendar_demo_a_sparql.html>}.

@summary: Python interface to SPARQL services
@see: U{SPARQL Specification<http://www.w3.org/TR/rdf-sparql-query/>}
@authors: U{Ivan Herman<http://www.ivan-herman.net>}, U{Sergio Fernández<http://www.wikier.org>}, U{Carlos Tejo Alonso<http://www.dayures.net>}
@organization: U{World Wide Web Consortium<http://www.w3.org>}, U{Salzburg Research<http://www.salzburgresearch.at>} and U{Foundation CTIC<http://www.fundacionctic.org/>}.
@license: U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/copyright-software">}
@requires: U{simplejson<http://cheeseshop.python.org/pypi/simplejson>} package.
@requires: U{RDFLib<http://rdflib.net>} package.
"""

__version__ = "1.8.0"
"""The version of SPARQLWrapper"""

__authors__  = "Ivan Herman, Sergio Fernández, Carlos Tejo Alonso, Alexey Zakhlestin"
"""The primary authors of SPARQLWrapper"""

__license__ = "W3C® SOFTWARE NOTICE AND LICENSE, http://www.w3.org/Consortium/Legal/copyright-software"
"""The license governing the use and distribution of SPARQLWrapper"""

__url__ = "http://rdflib.github.io/sparqlwrapper"
"""The URL for SPARQLWrapper's homepage"""

__contact__ = "rdflib-dev@googlegroups.com"
"""Mail list to contact to other people RDFLib and SPARQLWrappers folks and developers"""

__date__    = "2015-12-18"
"""Last update"""

__agent__   = "sparqlwrapper %s (rdflib.github.io/sparqlwrapper)" % __version__


from Wrapper import SPARQLWrapper
from Wrapper import XML, JSON, TURTLE, N3, JSONLD, RDF, RDFXML
from Wrapper import GET, POST
from Wrapper import SELECT, CONSTRUCT, ASK, DESCRIBE, INSERT, DELETE
from Wrapper import URLENCODED, POSTDIRECTLY
from Wrapper import BASIC, DIGEST

from SmartWrapper import SPARQLWrapper2
