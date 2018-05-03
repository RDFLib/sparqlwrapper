# -*- coding: utf-8 -*-
# epydoc
#
"""
@var JSON: to be used to set the return format to JSON
@var XML: to be used to set the return format to XML (SPARQL XML format or RDF/XML, depending on the query type). This is the default.
@var RDFXML: to be used to set the return format to RDF/XML explicitly.
@var TURTLE: to be used to set the return format to Turtle
@var N3: to be used to set the return format to N3 (for most of the SPARQL services this is equivalent to Turtle)
@var RDF: to be used to set the return RDF Graph
@var CSV: to be used to set the return format to CSV
@var TSV: to be used to set the return format to TSV
@var JSONLD: to be used to set the return format to JSON-LD

@var POST: to be used to set HTTP POST
@var GET: to be used to set HTTP GET. This is the default.

@var SELECT: to be used to set the query type to SELECT. This is, usually, determined automatically.
@var CONSTRUCT: to be used to set the query type to CONSTRUCT. This is, usually, determined automatically.
@var ASK: to be used to set the query type to ASK. This is, usually, determined automatically.
@var DESCRIBE: to be used to set the query type to DESCRIBE. This is, usually, determined automatically.

@var INSERT: to be used to set the query type to INSERT.
@var DELETE: to be used to set the query type to DELETE.
@var CREATE: to be used to set the query type to CREATE.
@var CLEAR: to be used to set the query type to CLEAR.
@var DROP: to be used to set the query type to DROP.
@var LOAD: to be used to set the query type to LOAD.
@var COPY: to be used to set the query type to COPY.
@var MOVE: to be used to set the query type to MOVE.
@var ADD: to be used to set the query type to ADD.


@var BASIC: BASIC HTTP Authentication method
@var DIGEST: DIGEST HTTP Authentication method

@see: U{SPARQL Specification<http://www.w3.org/TR/rdf-sparql-query/>}
@authors: U{Ivan Herman<http://www.ivan-herman.net>}, U{Sergio Fernández<http://www.wikier.org>}, U{Carlos Tejo Alonso<http://www.dayures.net>}
@organization: U{World Wide Web Consortium<http://www.w3.org>}, U{Salzburg Research<http://www.salzburgresearch.at>} and U{Foundation CTIC<http://www.fundacionctic.org/>}.
@license: U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/copyright-software">}
@requires: U{RDFLib<http://rdflib.net>} package.
"""

import urllib
import urllib2
from urllib2 import urlopen as urlopener  # don't change the name: tests override it
import base64
import re
import sys
import warnings

import json
from KeyCaseInsensitiveDict import KeyCaseInsensitiveDict
from SPARQLExceptions import QueryBadFormed, EndPointNotFound, EndPointInternalError, Unauthorized
from SPARQLWrapper import __agent__

#  From <https://www.w3.org/TR/sparql11-protocol/#query-success>
#  The response body of a successful query operation with a 2XX response is either:
#  * SELECT and ASK: a SPARQL Results Document in XML, JSON, or CSV/TSV format.
#  * DESCRIBE and CONSTRUCT: an RDF graph serialized, for example, in the RDF/XML syntax, or an equivalent RDF graph serialization.
#
#  Possible parameter keys and values...
#  Examples:
#  - ClioPatria: the SWI-Prolog Semantic Web Server <http://cliopatria.swi-prolog.org/home>
#    * Parameter key: "format" <http://cliopatria.swi-prolog.org/help/http>
#    * Parameter value must have one of these values: "rdf+xml", "json", "csv", "application/sparql-results+xml" or "application/sparql-results+json".
#
#  - OpenLink Virtuoso  <http://virtuoso.openlinksw.com>
#    * Parameter key: "format" or "output"
#    * Parameter value, like directly:
#      "text/html" (HTML), "text/x-html+tr" (HTML (Faceted Browsing Links)), "application/vnd.ms-excel"
#      "application/sparql-results+xml" (XML), "application/sparql-results+json", (JSON)
#      "application/javascript" (Javascript), "text/turtle" (Turtle), "application/rdf+xml" (RDF/XML)
#      "text/plain" (N-Triples), "text/csv" (CSV), "text/tab-separated-values" (TSV)
#    * Parameter value, like indirectly:
#      "HTML" (alias text/html), "JSON" (alias application/sparql-results+json), "XML" (alias application/sparql-results+xml), "TURTLE" (alias text/rdf+n3), JavaScript (alias application/javascript)
#       See  <http://virtuoso.openlinksw.com/dataspace/doc/dav/wiki/Main/VOSSparqlProtocol#Additional HTTP Response Formats -- SELECT>
#
#  - Fuseki (formerly there was Joseki) <https://jena.apache.org/documentation/serving_data/>
#    * Parameter key: "format" or "output"
#      See Fuseki 1: https://github.com/apache/jena/blob/master/jena-fuseki1/src/main/java/org/apache/jena/fuseki/HttpNames.java
#      See Fuseki 2: https://github.com/apache/jena/blob/master/jena-arq/src/main/java/org/apache/jena/riot/web/HttpNames.java
#    * Fuseki 1 - Short names for "output=" : "json", "xml", "sparql", "text", "csv", "tsv", "thrift"
#      See <https://github.com/apache/jena/blob/master/jena-fuseki1/src/main/java/org/apache/jena/fuseki/servlets/ResponseResultSet.java>
#    * Fuseki 2 - Short names for "output=" : "json", "xml", "sparql", "text", "csv", "tsv", "thrift"
#      See <https://github.com/apache/jena/blob/master/jena-fuseki2/jena-fuseki-core/src/main/java/org/apache/jena/fuseki/servlets/ResponseResultSet.java>
#
#  - Eclipse RDF4J (formerly known as Sesame) <http://rdf4j.org/>
#    * Uses only content negotiation (no URL parameters).
#    * See <http://rdf4j.org/doc/the-rdf4j-server-rest-api/#The_QUERY_operation>
#
#  - RASQAL <http://librdf.org/rasqal/>
#    * Parameter key: "results"
#    * Uses roqet as RDF query utility
#      For variable bindings, the values of FORMAT vary upon what Rasqal supports but include simple
#      for a simple text format (default), xml for the SPARQL Query Results XML format, csv for SPARQL CSV,
#      tsv for SPARQL TSV, rdfxml and turtle for RDF syntax formats, and json for a JSON version of the results.
#
#      For RDF graph results, the values of FORMAT are ntriples (N-Triples, default),
#      rdfxml-abbrev (RDF/XML Abbreviated), rdfxml (RDF/XML), turtle (Turtle),
#      json (RDF/JSON resource centric), json-triples (RDF/JSON triples) or
#      rss-1.0 (RSS 1.0, also an RDF/XML syntax).
#
#      See <http://librdf.org/rasqal/roqet.html>
#
#  - Marklogic <http://marklogic.com>
#    * Uses content negotiation (no URL parameters).
#    * You can use following methods to query triples <https://docs.marklogic.com/guide/semantics/semantic-searches#chapter>:
#      - SPARQL mode in Query Console. For details, see Querying Triples with SPARQL
#      - XQuery using the semantics functions, and Search API, or a combination of XQuery and SPARQL. For details, see Querying Triples with XQuery or JavaScript.
#      - HTTP via a SPARQL endpoint. For details, see Using Semantics with the REST Client API.
#    * Formats are specified as part of the HTTP Accept headers of the REST request. <https://docs.marklogic.com/guide/semantics/REST#id_92428>
#      - When you query the SPARQL endpoint with REST Client APIs, you can specify the result output format.  <https://docs.marklogic.com/guide/semantics/REST#id_54258>
#        The response type format depends on the type of query and the MIME type in the HTTP Accept header.
#      - This table describes the MIME types and Accept Header/Output formats (MIME type) for different types of SPARQL queries. See <https://docs.marklogic.com/guide/semantics/REST#id_54258> and <https://docs.marklogic.com/guide/semantics/loading#id_70682>
#        SELECT "application/sparql-results+xml", "application/sparql-results+json", "text/html", "text/csv"
#        CONSTRUCT or DESCRIBE "application/n-triples", "application/rdf+json", "application/rdf+xml", "text/turtle", "text/n3", "application/n-quads", "application/trig"
#        ASK queries return a boolean (true or false).
#
#  - AllegroGraph <https://franz.com/agraph/allegrograph/>
#    * Uses only content negotiation (no URL parameters).
#    * The server always looks at the Accept header of a request, and tries to
#      generate a response in the format that the client asks for. If this fails,
#      a 406 response is returned. When no Accept, or an Accept of */* is specified,
#      the server prefers text/plain, in order to make it easy to explore the interface from a web browser.
#    * Accept header expected (values returned by server when a wrong header is sent):
#    ** SELECT
#    *** application/sparql-results+xml
#    *** application/sparql-results+json (and application/json)
#    *** text/csv
#    *** text/tab-separated-values
#    *** OTHERS: application/sparql-results+ttl, text/integer, application/x-lisp-structured-expression, text/table, application/processed-csv, text/simple-csv, application/x-direct-upis
#
#    ** CONSTRUCT
#    *** application/rdf+xml
#    *** text/rdf+n3
#    *** OTHERS: text/integer, application/json, text/plain, text/x-nquads, application/trix, text/table, application/x-direct-upis
#
#      See <https://franz.com/agraph/support/documentation/current/http-protocol.html>


JSON   = "json"
JSONLD = "json-ld"
XML    = "xml"
TURTLE = "turtle"
N3     = "n3"
RDF    = "rdf"
RDFXML = "rdf+xml"
CSV    = "csv"
TSV    = "tsv"
_allowedFormats = [JSON, XML, TURTLE, N3, RDF, RDFXML, CSV, TSV]

# Possible HTTP methods
POST = "POST"
GET = "GET"
_allowedRequests = [POST, GET]

# Possible HTTP Authentication methods
BASIC = "BASIC"
DIGEST = "DIGEST"
_allowedAuth = [BASIC, DIGEST]

# Possible SPARQL/SPARUL query type (aka SPARQL Query forms)
SELECT     = "SELECT"
CONSTRUCT  = "CONSTRUCT"
ASK        = "ASK"
DESCRIBE   = "DESCRIBE"
INSERT     = "INSERT"
DELETE     = "DELETE"
CREATE     = "CREATE"
CLEAR      = "CLEAR"
DROP       = "DROP"
LOAD       = "LOAD"
COPY       = "COPY"
MOVE       = "MOVE"
ADD        = "ADD"
_allowedQueryTypes = [SELECT, CONSTRUCT, ASK, DESCRIBE, INSERT, DELETE, CREATE, CLEAR, DROP,
                      LOAD, COPY, MOVE, ADD]

# Possible methods to perform requests
URLENCODED = "urlencoded"
POSTDIRECTLY = "postdirectly"
_REQUEST_METHODS = [URLENCODED, POSTDIRECTLY]

# Possible output format (mime types) that can be converted by the local script. Unfortunately,
# it does not work by simply setting the return format, because there is still a certain level of confusion
# among implementations.
# For example, Joseki returns application/javascript and not the sparql-results+json thing that is required...
# Ie, alternatives should be given...
# Andy Seaborne told me (June 2007) that the right return format is now added to his CVS, ie, future releases of
# joseki will be o.k., too. The situation with turtle and n3 is even more confusing because the text/n3 and text/turtle
# mime types have just been proposed and not yet widely used...
_SPARQL_DEFAULT  = ["application/sparql-results+xml", "application/rdf+xml", "*/*"]
_SPARQL_XML      = ["application/sparql-results+xml"]
_SPARQL_JSON     = ["application/sparql-results+json", "application/json", "text/javascript", "application/javascript"] # VIVO server returns "application/javascript"
_RDF_XML         = ["application/rdf+xml"]
_RDF_N3          = ["text/rdf+n3", "application/n-triples", "application/turtle", "application/n3", "text/n3", "text/turtle"]
_RDF_JSONLD      = ["application/x-json+ld", "application/ld+json"]
_CSV             = ["text/csv"]
_TSV             = ["text/tab-separated-values"]
_XML             = ["application/xml"]
_ALL             = ["*/*"]
_RDF_POSSIBLE    = _RDF_XML + _RDF_N3 + _XML

_SPARQL_PARAMS = ["query"]

try:
    import rdflib_jsonld
    _allowedFormats.append(JSONLD)
    _RDF_POSSIBLE = _RDF_POSSIBLE + _RDF_JSONLD
except ImportError:
    #warnings.warn("JSON-LD disabled because no suitable support has been found", RuntimeWarning)
    pass

# This is very ugly. The fact is that the key for the choice of the output format is not defined.
# Virtuoso uses 'format', joseki uses 'output', rasqual seems to use "results", etc. Lee Feigenbaum
# told me that virtuoso also understand 'output' these days, so I removed 'format'. I do not have
# info about the others yet, ie, for the time being I keep the general mechanism. Hopefully, in a
# future release, I can get rid of that. However, these processors are (hopefully) oblivious to the
# parameters they do not understand. So: just repeat all possibilities in the final URI. UGLY!!!!!!!
_returnFormatSetting = ["format", "output", "results"]

#######################################################################################################


class SPARQLWrapper(object):
    """
    Wrapper around an online access to a SPARQL Web entry point.

    The same class instance can be reused for subsequent queries. The values of the base Graph URI, return formats, etc,
    are retained from one query to the next (in other words, only the query string changes). The instance can also be
    reset to its initial values using the L{resetQuery} method.

    @cvar pattern: regular expression used to determine whether a query is of type L{CONSTRUCT}, L{SELECT}, L{ASK}, or L{DESCRIBE}.
    @type pattern: compiled regular expression (see the C{re} module of Python)
    @ivar endpoint: SPARQL endpoint's URI
    @type endpoint: string
    @ivar updateEndpoint: SPARQL endpoint's URI for update operations (if it's a different one). Default is C{None}
    @type updateEndpoint: string
    @ivar agent: The User-Agent for the HTTP request header.
    @type agent: string
    @ivar _defaultGraph: URI for the default graph. Default is C{None}, the value can be set either via an L{explicit call<addParameter>}("default-graph-uri", uri) or as part of the query string.
    @type _defaultGraph: string
    @ivar user: The username of the credentials for querying the current endpoint. Default is C{None}, the value can be set an L{explicit call<setCredentials>}.
    @type user: string
    @ivar passwd: The password of the credentials for querying the current endpoint. Default is C{None}, the value can be set an L{explicit call<setCredentials>}.
    @type passwd: string
    @ivar http_auth: HTTP Authentication type. The default value is L{BASIC}. Possible values are L{BASIC} or L{DIGEST}
    @type http_auth: string
    @ivar onlyConneg: Option for allowing (or not) only HTTP Content Negotiation (so dismiss the use of HTTP parameters).The default value is L{False}.
    @type onlyConneg: boolean
    @ivar customHttpHeaders: Custom HTTP Headers to be included in the request. Important: These headers override previous values (including C{Content-Type}, C{User-Agent}, C{Accept} and C{Authorization} if they are present). It is a dictionary where keys are the header field nada and values are the header values.
    @type customHttpHeaders: dict
    """
    pattern = re.compile(r"""
        ((?P<base>(\s*BASE\s*<.*?>)\s*)|(?P<prefixes>(\s*PREFIX\s+.+:\s*<.*?>)\s*))*
        (?P<queryType>(CONSTRUCT|SELECT|ASK|DESCRIBE|INSERT|DELETE|CREATE|CLEAR|DROP|LOAD|COPY|MOVE|ADD))
    """, re.VERBOSE | re.IGNORECASE)
    comments_pattern = re.compile(r"(^|\n)\s*#.*?\n")

    def __init__(self, endpoint, updateEndpoint=None, returnFormat=XML, defaultGraph=None, agent=__agent__):
        """
        Class encapsulating a full SPARQL call.
        @param endpoint: string of the SPARQL endpoint's URI
        @type endpoint: string
        @param updateEndpoint: string of the SPARQL endpoint's URI for update operations (if it's a different one)
        @type updateEndpoint: string
        @param returnFormat: Default: L{XML}.
        Can be set to JSON or Turtle/N3

        No local check is done, the parameter is simply
        sent to the endpoint. Eg, if the value is set to JSON and a construct query is issued, it
        is up to the endpoint to react or not, this wrapper does not check.

        Possible values:
        L{JSON}, L{XML}, L{TURTLE}, L{N3}, L{RDFXML}, L{CSV}, L{TSV} (constants in this module). The value can also be set via explicit
        call, see below.
        @type returnFormat: string
        @param defaultGraph: URI for the default graph. Default is None, the value can be set either via an L{explicit call<addDefaultGraph>} or as part of the query string.
        @type defaultGraph: string
        @param agent: The User-Agent for the HTTP request header.
        @type agent: string
        """
        self.endpoint = endpoint
        self.updateEndpoint = updateEndpoint if updateEndpoint else endpoint
        self.agent = agent
        self.user = None
        self.passwd = None
        self.http_auth = BASIC
        self._defaultGraph = defaultGraph
        self.onlyConneg = False # Only Content Negotiation
        self.customHttpHeaders = {}

        if returnFormat in _allowedFormats:
            self._defaultReturnFormat = returnFormat
        else:
            self._defaultReturnFormat = XML

        self.resetQuery()

    def resetQuery(self):
        """Reset the query, ie, return format, method, query, default or named graph settings, etc,
        are reset to their default values.
        """
        self.parameters = {}
        if self._defaultGraph:
            self.addParameter("default-graph-uri", self._defaultGraph)
        self.returnFormat = self._defaultReturnFormat
        self.method = GET
        self.setQuery("""SELECT * WHERE{ ?s ?p ?o }""")
        self.timeout = None
        self.requestMethod = URLENCODED


    def setReturnFormat(self, format):
        """Set the return format. If not an allowed value, the setting is ignored.

        @param format: Possible values are L{JSON}, L{XML}, L{TURTLE}, L{N3}, L{RDF}, L{RDFXML}, L{CSV}, L{TSV}, L{JSONLD} (constants in this module). All other cases are ignored.
        @type format: string
        @raise ValueError: If L{JSONLD} is tried to set and the current instance does not support JSON-LD.
        """
        if format in _allowedFormats:
            self.returnFormat = format
        elif format == JSONLD:
            raise ValueError("Current instance does not support JSON-LD; you might want to install the rdflib-json package.")
        else:
            warnings.warn("Ignore format '%s'; current instance supports: %s." %(format, ", ".join(_allowedFormats)), SyntaxWarning)

    def supportsReturnFormat(self, format):
        """Check if a return format is supported.

        @param format: Possible values are L{JSON}, L{XML}, L{TURTLE}, L{N3}, L{RDF}, L{RDFXML}, L{CSV}, L{TSV} (constants in this module). All other cases are ignored.
        @type format: string
        @return: Returns a boolean after checking if a return format is supported.
        @rtype: bool
        """
        return (format in _allowedFormats)

    def setTimeout(self, timeout):
        """Set the timeout (in seconds) to use for querying the endpoint.

        @param timeout: Timeout in seconds.
        @type timeout: int
        """
        self.timeout = int(timeout)

    def setOnlyConneg(self, onlyConneg):
        """Set this option for allowing (or not) only HTTP Content Negotiation (so dismiss the use of HTTP parameters).
        @since: 1.8.1

        @param onlyConneg: True if only HTTP Content Negotiation is allowed; False is HTTP parameters are allowed also.
        @type onlyConneg: bool
        """
        self.onlyConneg = onlyConneg

    def setRequestMethod(self, method):
        """Set the internal method to use to perform the request for query or
        update operations, either URL-encoded (C{SPARQLWrapper.URLENCODED}) or
        POST directly (C{SPARQLWrapper.POSTDIRECTLY}).
        Further details at U{http://www.w3.org/TR/sparql11-protocol/#query-operation}
        and U{http://www.w3.org/TR/sparql11-protocol/#update-operation}.

        @param method: Possible values are C{SPARQLWrapper.URLENCODED} (URL-encoded) or C{SPARQLWrapper.POSTDIRECTLY} (POST directly). All other cases are ignored.
        @type method: string
        """
        if method in _REQUEST_METHODS:
            self.requestMethod = method
        else:
            warnings.warn("invalid update method '%s'" % method, RuntimeWarning)

    def addDefaultGraph(self, uri):
        """
            Add a default graph URI.
            @param uri: URI of the graph
            @type uri: string
            @deprecated: use addParameter("default-graph-uri", uri) instead of this method
        """
        self.addParameter("default-graph-uri", uri)

    def addNamedGraph(self, uri):
        """
            Add a named graph URI.
            @param uri: URI of the graph
            @type uri: string
            @deprecated: use addParameter("named-graph-uri", uri) instead of this method
        """
        self.addParameter("named-graph-uri", uri)

    def addExtraURITag(self, key, value):
        """
            Some SPARQL endpoints require extra key value pairs.
            E.g., in virtuoso, one would add C{should-sponge=soft} to the query forcing
            virtuoso to retrieve graphs that are not stored in its local database.
            Alias of L{SPARQLWrapper.addParameter} method.
            @param key: key of the query part
            @type key: string
            @param value: value of the query part
            @type value: string
            @deprecated: use addParameter(key, value) instead of this method
        """
        self.addParameter(key, value)

    def addCustomParameter(self, name, value):
        """
            Method is kept for backwards compatibility. Historically, it "replaces" parameters instead of adding.
            @param name: name
            @type name: string
            @param value: value
            @type value: string
            @return: Returns a boolean indicating if the adding has been accomplished.
            @rtype: bool
            @deprecated: use addParameter(name, value) instead of this method
        """
        self.clearParameter(name)
        return self.addParameter(name, value)

    def addParameter(self, name, value):
        """
            Some SPARQL endpoints allow extra key value pairs.
            E.g., in virtuoso, one would add C{should-sponge=soft} to the query forcing
            virtuoso to retrieve graphs that are not stored in its local database.
            If the param C{query} is tried to be set, this intent is dismissed.
            Returns a boolean indicating if the set has been accomplished.
            @param name: name
            @type name: string
            @param value: value
            @type value: string
            @return: Returns a boolean indicating if the adding has been accomplished.
            @rtype: bool
        """
        if name in _SPARQL_PARAMS:
            return False
        else:
            if name not in self.parameters:
                self.parameters[name] = []
            self.parameters[name].append(value)
            return True

    def addCustomHttpHeader(self, httpHeaderName, httpHeaderValue):
        """
            Add a custom HTTP header (this method can override all HTTP headers).
            IMPORTANT: Take into acount that each previous value for the header field names
            C{Content-Type}, C{User-Agent}, C{Accept} and C{Authorization} would be overriden
            if the header field name is present as value of the parameter C{httpHeaderName}.
            @since: 1.8.2

            @param httpHeaderName: The header field name.
            @type httpHeaderName: string
            @param httpHeaderValue: The header field value.
            @type httpHeaderValue: string
        """
        self.customHttpHeaders[httpHeaderName] = httpHeaderValue

    def clearCustomHttpHeader(self, httpHeaderName):
        """
            Clear the values of a custom Http Header previously setted.
            Returns a boolean indicating if the clearing has been accomplished.
            @since: 1.8.2

            @param httpHeaderName: name
            @type httpHeaderName: string
            @return: Returns a boolean indicating if the clearing has been accomplished.
            @rtype: bool
        """
        try:
            del self.customHttpHeaders[httpHeaderName]
            return True
        except KeyError:
            return False

    def clearParameter(self, name):
        """
            Clear the values of a concrete parameter.
            Returns a boolean indicating if the clearing has been accomplished.
            @param name: name
            @type name: string
            @return: Returns a boolean indicating if the clearing has been accomplished.
            @rtype: bool
        """
        if name in _SPARQL_PARAMS:
            return False
        else:
            try:
                del self.parameters[name]
                return True
            except KeyError:
                return False

    def setCredentials(self, user, passwd):
        """
            Set the credentials for querying the current endpoint.
            @param user: username
            @type user: string
            @param passwd: password
            @type passwd: string
        """
        self.user = user
        self.passwd = passwd

    def setHTTPAuth(self, auth):
        """
            Set the HTTP Authentication type. Possible values are L{BASIC} or L{DIGEST}.
            @param auth: auth type
            @type auth: string
            @raise TypeError: If the C{auth} parameter is not an string.
            @raise ValueError: If the C{auth} parameter has not one of the valid values: L{BASIC} or L{DIGEST}.
        """
        if not isinstance(auth, str):
            raise TypeError('setHTTPAuth takes a string')
        elif auth.upper() in _allowedAuth:
            self.http_auth = auth.upper()
        else:
            valid_types = ", ".join(_allowedAuth)
            raise ValueError("Value should be one of {0}".format(valid_types))

    def setQuery(self, query):
        """
            Set the SPARQL query text. Note: no check is done on the validity of the query
            (syntax or otherwise) by this module, except for testing the query type (SELECT,
            ASK, etc). Syntax and validity checking is done by the SPARQL service itself.
            @param query: query text
            @type query: string
            @raise TypeError: If the C{query} parameter is not an unicode-string or utf-8 encoded byte-string.
        """
        if sys.version < '3':  # have to write it like this, for 2to3 compatibility
            if isinstance(query, unicode):
                pass
            elif isinstance(query, str):
                query = query.decode('utf-8')
            else:
                raise TypeError('setQuery takes either unicode-strings or utf-8 encoded byte-strings')
        else:
            if isinstance(query, str):
                pass
            elif isinstance(query, bytes):
                query = query.decode('utf-8')
            else:
                raise TypeError('setQuery takes either unicode-strings or utf-8 encoded byte-strings')

        self.queryString = query
        self.queryType = self._parseQueryType(query)

    def _parseQueryType(self, query):
        """
            Internal method for parsing the SPARQL query and return its type (ie, L{SELECT}, L{ASK}, etc).

            Note that the method returns L{SELECT} if nothing is specified. This is just to get all other
            methods running; in fact, this means that the query is erroneous, because the query must be,
            according to the SPARQL specification, one of Select, Ask, Describe, or Construct. The
            SPARQL endpoint should raise an exception (via urllib) for such syntax error.

            @param query: query text
            @type query: string
            @return: the type of SPARQL query (aka SPARQL query form)
            @rtype: string
        """
        try:
            query = query if (isinstance(query, str)) else query.encode('ascii', 'ignore')
            query = self._cleanComments(query)
            r_queryType = self.pattern.search(query).group("queryType").upper()
        except AttributeError:
            warnings.warn("not detected query type for query '%s'" % query.replace("\n", " "), RuntimeWarning)
            r_queryType = None

        if r_queryType in _allowedQueryTypes:
            return r_queryType
        else:
            #raise Exception("Illegal SPARQL Query; must be one of SELECT, ASK, DESCRIBE, or CONSTRUCT")
            warnings.warn("unknown query type '%s'" % r_queryType, RuntimeWarning)
            return SELECT

    def setMethod(self, method):
        """Set the invocation method. By default, this is L{GET}, but can be set to L{POST}.
        @param method: should be either L{GET} or L{POST}. Other cases are ignored.
        @type method: string
        """
        if method in _allowedRequests:
            self.method = method

    def setUseKeepAlive(self):
        """Make urllib2 use keep-alive.
        @raise ImportError: when could not be imported keepalive.HTTPHandler
        """
        try:
            from keepalive import HTTPHandler

            if urllib2._opener and any(isinstance(h, HTTPHandler) for h in urllib2._opener.handlers):
                # already installed
                return

            keepalive_handler = HTTPHandler()
            opener = urllib2.build_opener(keepalive_handler)
            urllib2.install_opener(opener)
        except ImportError:
            warnings.warn("keepalive support not available, so the execution of this method has no effect")

    def isSparqlUpdateRequest(self):
        """ Returns C{TRUE} if SPARQLWrapper is configured for executing SPARQL Update request.
        @return: Returns C{TRUE} if SPARQLWrapper is configured for executing SPARQL Update request
        @rtype: bool
        """
        return self.queryType in [INSERT, DELETE, CREATE, CLEAR, DROP, LOAD, COPY, MOVE, ADD]

    def isSparqlQueryRequest(self):
        """ Returns C{TRUE} if SPARQLWrapper is configured for executing SPARQL Query request.
        @return: Returns C{TRUE} if SPARQLWrapper is configured for executing SPARQL Query request.
        @rtype: bool
        """
        return not self.isSparqlUpdateRequest()

    def _cleanComments(self, query):
        """ Internal method for returning the query after all occurrence of singleline comments are removed (issues #32 and #77).
        @param query: The query
        @type query: string
        @return: the query after all occurrence of singleline comments are removed.
        @rtype: string
        """
        return re.sub(self.comments_pattern, "\n\n", query)

    def _getRequestEncodedParameters(self, query=None):
        """ Internal method for getting the request encoded parameters.
        @param query: The query
        @type query: string
        """
        query_parameters = self.parameters.copy()

        if query and (isinstance(query, tuple)) and len(query) == 2:
            #tuple ("query"/"update", queryString)
            query_parameters[query[0]] = [query[1]]

        # This is very ugly. The fact is that the key for the choice of the output format is not defined.
        # Virtuoso uses 'format',sparqler uses 'output'
        # However, these processors are (hopefully) oblivious to the parameters they do not understand.
        # So: just repeat all possibilities in the final URI. UGLY!!!!!!!
        if not self.onlyConneg:
            for f in _returnFormatSetting:
                query_parameters[f] = [self.returnFormat]
                # Virtuoso is not supporting a correct Accept header and an unexpected "output"/"format" parameter value. It returns a 406.
                # "tsv" and "json-ld" are not supported as a correct "output"/"format" parameter value but "text/tab-separated-values" is a valid value,
                # and there is no problem to send both.
                if self.returnFormat in [TSV, JSONLD]:
                    acceptHeader = self._getAcceptHeader() # to obtain the mime-type "text/tab-separated-values"
                    if "*/*" in acceptHeader:
                        acceptHeader = "" # clear the value in case of "*/*"
                    query_parameters[f] += [acceptHeader]

        pairs = (
            "%s=%s" % (
                urllib.quote_plus(param.encode('UTF-8'), safe='/'),
                urllib.quote_plus(value.encode('UTF-8'), safe='/')
            )
            for param, values in query_parameters.items() for value in values
        )

        return '&'.join(pairs)

    def _getAcceptHeader(self):
        """ Internal method for getting the HTTP Accept Header.
        @see: U{Hypertext Transfer Protocol -- HTTP/1.1 - Header Field Definitions<https://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.1>}
        """
        if self.queryType in [SELECT, ASK]:
            if self.returnFormat == XML:
                acceptHeader = ",".join(_SPARQL_XML)
            elif self.returnFormat == JSON:
                acceptHeader = ",".join(_SPARQL_JSON)
            elif self.returnFormat == CSV: # Allowed for SELECT and ASK (https://www.w3.org/TR/2013/REC-sparql11-protocol-20130321/#query-success) but only described for SELECT (https://www.w3.org/TR/sparql11-results-csv-tsv/)
                acceptHeader = ",".join(_CSV)
            elif self.returnFormat == TSV: # Allowed for SELECT and ASK (https://www.w3.org/TR/2013/REC-sparql11-protocol-20130321/#query-success) but only described for SELECT (https://www.w3.org/TR/sparql11-results-csv-tsv/)
                acceptHeader = ",".join(_TSV)
            else:
                acceptHeader = ",".join(_ALL)
                warnings.warn("Sending Accept header '*/*' because unexpected returned format '%s' in a '%s' SPARQL query form" % (self.returnFormat, self.queryType), RuntimeWarning)
        elif self.queryType in [INSERT, DELETE]:
            acceptHeader = "*/*"
        else: #CONSTRUCT, DESCRIBE
            if self.returnFormat == N3 or self.returnFormat == TURTLE:
                acceptHeader = ",".join(_RDF_N3)
            elif self.returnFormat == XML:
                acceptHeader = ",".join(_RDF_XML)
            elif self.returnFormat == JSONLD and JSONLD in _allowedFormats:
                acceptHeader = ",".join(_RDF_JSONLD)
            else:
                acceptHeader = ",".join(_ALL)
                warnings.warn("Sending Accept header '*/*' because unexpected returned format '%s' in a '%s' SPARQL query form" % (self.returnFormat, self.queryType), RuntimeWarning)
        return acceptHeader

    def _createRequest(self):
        """Internal method to create request according a HTTP method. Returns a
        C{urllib2.Request} object of the urllib2 Python library
        @raise NotImplementedError: If the C{HTTP authentification} method is not one of the valid values: L{BASIC} or L{DIGEST}.
        @return: request a C{urllib2.Request} object of the urllib2 Python library
        """
        request = None

        if self.isSparqlUpdateRequest():
            #protocol details at http://www.w3.org/TR/sparql11-protocol/#update-operation
            uri = self.updateEndpoint

            if self.method != POST:
                warnings.warn("update operations MUST be done by POST")

            if self.requestMethod == POSTDIRECTLY:
                request = urllib2.Request(uri + "?" + self._getRequestEncodedParameters())
                request.add_header("Content-Type", "application/sparql-update")
                request.data = self.queryString.encode('UTF-8')
            else:  # URL-encoded
                request = urllib2.Request(uri)
                request.add_header("Content-Type", "application/x-www-form-urlencoded")
                request.data = self._getRequestEncodedParameters(("update", self.queryString)).encode('ascii')
        else:
            #protocol details at http://www.w3.org/TR/sparql11-protocol/#query-operation
            uri = self.endpoint

            if self.method == POST:
                if self.requestMethod == POSTDIRECTLY:
                    request = urllib2.Request(uri + "?" + self._getRequestEncodedParameters())
                    request.add_header("Content-Type", "application/sparql-query")
                    request.data = self.queryString.encode('UTF-8')
                else:  # URL-encoded
                    request = urllib2.Request(uri)
                    request.add_header("Content-Type", "application/x-www-form-urlencoded")
                    request.data = self._getRequestEncodedParameters(("query", self.queryString)).encode('ascii')
            else:  # GET
                request = urllib2.Request(uri + "?" + self._getRequestEncodedParameters(("query", self.queryString)))

        request.add_header("User-Agent", self.agent)
        request.add_header("Accept", self._getAcceptHeader())
        if self.user and self.passwd:
            if self.http_auth == BASIC:
                credentials = "%s:%s" % (self.user, self.passwd)
                request.add_header("Authorization", "Basic %s" % base64.b64encode(credentials.encode('utf-8')).decode('utf-8'))
            elif self.http_auth == DIGEST:
                realm = "SPARQL"
                pwd_mgr = urllib2.HTTPPasswordMgr()
                pwd_mgr.add_password(realm, uri, self.user, self.passwd)
                opener = urllib2.build_opener()
                opener.add_handler(urllib2.HTTPDigestAuthHandler(pwd_mgr))
                urllib2.install_opener(opener)
            else:
                valid_types = ", ".join(_allowedAuth)
                raise NotImplementedError("Expecting one of: {0}, but received: {1}".format(valid_types,
                                                                                            self.http_auth))

        # The header field name is capitalized in the request.add_header method.
        for customHttpHeader in self.customHttpHeaders:
            request.add_header(customHttpHeader, self.customHttpHeaders[customHttpHeader])

        return request

    def _query(self):
        """Internal method to execute the query. Returns the output of the
        C{urllib2.urlopen} method of the standard Python library

        @return: tuples with the raw request plus the expected format.
        @raise QueryBadFormed: If the C{HTTP return code} is C{400}.
        @raise Unauthorized: If the C{HTTP return code} is C{401}.
        @raise EndPointNotFound: If the C{HTTP return code} is C{404}.
        @raise EndPointInternalError: If the C{HTTP return code} is C{500}.
        """
        request = self._createRequest()

        try:
            if self.timeout:
                response = urlopener(request, timeout=self.timeout)
            else:
                response = urlopener(request)
            return response, self.returnFormat
        except urllib2.HTTPError, e:
            if e.code == 400:
                raise QueryBadFormed(e.read())
            elif e.code == 404:
                raise EndPointNotFound(e.read())
            elif e.code == 401:
                raise Unauthorized(e.read())
            elif e.code == 500:
                raise EndPointInternalError(e.read())
            else:
                raise e

    def query(self):
        """
            Execute the query.
            Exceptions can be raised if either the URI is wrong or the HTTP sends back an error (this is also the
            case when the query is syntactically incorrect, leading to an HTTP error sent back by the SPARQL endpoint).
            The usual urllib2 exceptions are raised, which therefore cover possible SPARQL errors, too.

            Note that some combinations of return formats and query types may not make sense. For example,
            a SELECT query with Turtle response is meaningless (the output of a SELECT is not a Graph), or a CONSTRUCT
            query with JSON output may be a problem because, at the moment, there is no accepted JSON serialization
            of RDF (let alone one implemented by SPARQL endpoints). In such cases the returned media type of the result is
            unpredictable and may differ from one SPARQL endpoint implementation to the other. (Endpoints usually fall
            back to one of the "meaningful" formats, but it is up to the specific implementation to choose which
            one that is.)

            @return: query result
            @rtype: L{QueryResult} instance
        """
        return QueryResult(self._query())

    def queryAndConvert(self):
        """Macro like method: issue a query and return the converted results.
        @return: the converted query result. See the conversion methods for more details.
        """
        res = self.query()
        return res.convert()

#######################################################################################################


class QueryResult(object):
    """
    Wrapper around an a query result. Users should not create instances of this class, it is
    generated by a L{SPARQLWrapper.query} call. The results can be
    converted to various formats, or used directly.

    If used directly: the class gives access to the direct http request results
    L{self.response}: it is a file-like object with two additional methods: C{geturl()} to
    return the URL of the resource retrieved and
    C{info()} that returns the meta-information of the HTTP result as a dictionary-like object
    (see the urllib2 standard library module of Python).

    For convenience, these methods are also available on the instance. The C{__iter__} and
    C{next} methods are also implemented (by mapping them to L{self.response}). This means that the
    common idiom::
     for l in obj : do_something_with_line(l)
    would work, too.

    @ivar response: the direct HTTP response; a file-like object, as return by the C{urllib2.urlopen} library call.
    @ivar requestedFormat: The requested format. The possible values are: L{JSON}, L{XML}, L{RDFXML}, L{TURTLE}, L{N3}, L{RDF}, L{CSV}, L{TSV}, L{JSONLD}.
    @type requestedFormat: string

    """
    def __init__(self, result):
        """
        @param result: HTTP response stemming from a L{SPARQLWrapper.query} call, or a tuple with the expected format: (response,format)
        """
        if isinstance(result, tuple):
            self.response = result[0]
            self.requestedFormat = result[1]
        else:
            self.response = result
        """Direct response, see class comments for details"""

    def geturl(self):
        """Return the URL of the original call.
        @return: URL of the original call
        @rtype: string
        """
        return self.response.geturl()

    def info(self):
        """Return the meta-information of the HTTP result.
        @return: meta information of the HTTP result
        @rtype: dict
        """
        return KeyCaseInsensitiveDict(self.response.info())

    def __iter__(self):
        """Return an iterator object. This method is expected for the inclusion
        of the object in a standard C{for} loop.
        """
        return self.response.__iter__()

    def next(self):
        """Method for the standard iterator."""
        return self.response.next()

    def _convertJSON(self):
        """
        Convert a JSON result into a Python dict. This method can be overwritten in a subclass
        for a different conversion method.
        @return: converted result
        @rtype: dict
        """
        return json.loads(self.response.read().decode("utf-8"))

    def _convertXML(self):
        """
        Convert an XML result into a Python dom tree. This method can be overwritten in a
        subclass for a different conversion method.
        @return: converted result
        @rtype: PyXlib DOM node
        """
        from xml.dom.minidom import parse
        return parse(self.response)

    def _convertRDF(self):
        """
        Convert a RDF/XML result into an RDFLib triple store. This method can be overwritten
        in a subclass for a different conversion method.
        @return: converted result
        @rtype: RDFLib C{Graph}
        """
        try:
            from rdflib.graph import ConjunctiveGraph
        except ImportError:
            from rdflib import ConjunctiveGraph
        retval = ConjunctiveGraph()
        # (DEPRECATED) this is a strange hack. If the publicID is not set, rdflib (or the underlying xml parser) makes a funny
        # (DEPRECATED) (and, as far as I could see, meaningless) error message...
        retval.load(self.response) # (DEPRECATED) publicID=' ')
        return retval

    def _convertN3(self):
        """
        Convert a RDF Turtle/N3 result into a string. This method can be overwritten in a subclass
        for a different conversion method.
        @return: converted result
        @rtype: string
        """
        return self.response.read()

    def _convertCSV(self):
        """
        Convert a CSV result into a string. This method can be overwritten in a subclass
        for a different conversion method.
        @return: converted result
        @rtype: string
        """
        return self.response.read()

    def _convertTSV(self):
        """
        Convert a TSV result into a string. This method can be overwritten in a subclass
        for a different conversion method.
        @return: converted result
        @rtype: string
        """
        return self.response.read()

    def _convertJSONLD(self):
        """
        Convert a RDF JSON-LD result into an RDFLib triple store. This method can be overwritten
        in a subclass for a different conversion method.
        @return: converted result
        @rtype: RDFLib Graph
        """
        from rdflib import ConjunctiveGraph
        retval = ConjunctiveGraph()
        retval.load(self.response, format='json-ld')# (DEPRECATED), publicID=' ')
        return retval

    def convert(self):
        """
        Encode the return value depending on the return format:
            - in the case of XML, a DOM top element is returned;
            - in the case of JSON, a simplejson conversion will return a dictionary;
            - in the case of RDF/XML, the value is converted via RDFLib into a C{Graph} instance;
            - in the case of RDF Turtle/N3, a string is returned;
            - in the case of CSV/TSV, a string is returned.
        In all other cases the input simply returned.

        @return: the converted query result. See the conversion methods for more details.
        """
        def _content_type_in_list(real, expected):
            return True in [real.find(mime) != -1 for mime in expected]

        def _validate_format(format_name, allowed, mime, requested):
            if requested not in allowed:
                message = "Format requested was %s, but %s (%s) has been returned by the endpoint"
                warnings.warn(message % (requested.upper(), format_name, mime), RuntimeWarning)

        # TODO. In order to compare properly, the requested QueryType (SPARQL Query Form) is needed. For instance, the unexpected N3 requested for a SELECT would return XML
        if "content-type" in self.info():
            ct = self.info()["content-type"] # returned Content-Type value

            if _content_type_in_list(ct, _SPARQL_XML):
                _validate_format("XML", [XML], ct, self.requestedFormat)
                return self._convertXML()
            elif _content_type_in_list(ct, _XML):
                _validate_format("XML", [XML], ct, self.requestedFormat)
                return self._convertXML()
            elif _content_type_in_list(ct, _SPARQL_JSON):
                _validate_format("JSON", [JSON], ct, self.requestedFormat)
                return self._convertJSON()
            elif _content_type_in_list(ct, _RDF_XML):
                _validate_format("RDF/XML", [RDF, XML, RDFXML], ct, self.requestedFormat)
                return self._convertRDF()
            elif _content_type_in_list(ct, _RDF_N3):
                _validate_format("N3", [N3, TURTLE], ct, self.requestedFormat)
                return self._convertN3()
            elif _content_type_in_list(ct, _CSV):
                _validate_format("CSV", [CSV], ct, self.requestedFormat)
                return self._convertCSV()
            elif _content_type_in_list(ct, _TSV):
                _validate_format("TSV", [TSV], ct, self.requestedFormat)
                return self._convertTSV()
            elif _content_type_in_list(ct, _RDF_JSONLD):
                _validate_format("JSON(-LD)", [JSONLD, JSON], ct, self.requestedFormat)
                return self._convertJSONLD()
            else:
                warnings.warn("unknown response content type '%s' returning raw response..." %(ct), RuntimeWarning)
        return self.response.read()

    def print_results(self, minWidth=None):
        results = self._convertJSON()
        if minWidth:
            width = self.__get_results_width(results, minWidth)
        else:
            width = self.__get_results_width(results)
        index = 0
        for var in results["head"]["vars"]:
            print ("?" + var).ljust(width[index]), "|",
            index += 1
        print
        print "=" * (sum(width) + 3 * len(width))
        for result in results["results"]["bindings"]:
            index = 0
            for var in results["head"]["vars"]:
                result = self.__get_prettyprint_string_sparql_var_result(result[var])
                print result.ljust(width[index]), "|",
                index += 1
            print

    def __get_results_width(self, results, minWidth=2):
        width = []
        for var in results["head"]["vars"]:
            width.append(max(minWidth, len(var)+1))
        for result in results["results"]["bindings"]:
            index = 0
            for var in results["head"]["vars"]:
                result = self.__get_prettyprint_string_sparql_var_result(result[var])
                width[index] = max(width[index], len(result))
                index += 1
        return width

    def __get_prettyprint_string_sparql_var_result(self, result):
        value = result["value"]
        lang = result.get("xml:lang", None)
        datatype = result.get("datatype", None)
        if lang is not None:
            value += "@"+lang
        if datatype is not None:
            value += " ["+datatype+"]"
        return value
