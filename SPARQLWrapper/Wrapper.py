# -*- coding: utf-8 -*-

"""
..
  .. seealso:: `SPARQL Specification <http://www.w3.org/TR/rdf-sparql-query/>`_

  Developers involved:

  * Ivan Herman <http://www.ivan-herman.net>
  * Sergio Fernández <http://www.wikier.org>
  * Carlos Tejo Alonso <http://www.dayures.net>
  * Alexey Zakhlestin <https://indeyets.ru/>

  Organizations involved:

  * `World Wide Web Consortium <http://www.w3.org>`_
  * `Salzburg Research <http://www.salzburgresearch.at>`_
  * `Foundation CTIC <http://www.fundacionctic.org/>`_

  :license: `W3C® Software notice and license <http://www.w3.org/Consortium/Legal/copyright-software>`_

  :requires: `RDFLib <https://rdflib.readthedocs.io>`_ package.
"""

import base64
import json
import re
import urllib.error
import urllib.parse
import urllib.request
import warnings
from http.client import HTTPResponse
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Optional, Tuple, Union, cast
from urllib.request import (
    urlopen as urlopener,
)  # don't change the name: tests override it
from xml.dom.minidom import Document, parse

from SPARQLWrapper import __agent__

if TYPE_CHECKING:
    from rdflib import Graph



from .KeyCaseInsensitiveDict import KeyCaseInsensitiveDict
from .SPARQLExceptions import (
    EndPointInternalError,
    EndPointNotFound,
    QueryBadFormed,
    Unauthorized,
    URITooLong,
)

# alias

XML = "xml"
"""to be used to set the return format to ``XML`` (``SPARQL Query Results XML`` format or ``RDF/XML``, depending on the
query type). **This is the default**."""
JSON = "json"
"""to be used to set the return format to ``JSON``."""
JSONLD = "json-ld"
"""to be used to set the return format to ``JSON-LD``."""
TURTLE = "turtle"
"""to be used to set the return format to ``Turtle``."""
N3 = "n3"
"""to be used to set the return format to ``N3`` (for most of the SPARQL services this is equivalent to Turtle)."""
RDF = "rdf"
"""to be used to set the return ``RDF Graph``."""
RDFXML = "rdf+xml"
"""to be used to set the return format to ``RDF/XML`` explicitly."""
CSV = "csv"
"""to be used to set the return format to ``CSV``"""
TSV = "tsv"
"""to be used to set the return format to ``TSV``"""
_allowedFormats = [JSON, XML, TURTLE, N3, RDF, RDFXML, CSV, TSV, JSONLD]

# Possible HTTP methods
GET = "GET"
"""to be used to set HTTP method ``GET``. **This is the default**."""
POST = "POST"
"""to be used to set HTTP method ``POST``."""
_allowedRequests = [POST, GET]

# Possible HTTP Authentication methods
BASIC = "BASIC"
"""to be used to set ``BASIC`` HTTP Authentication method."""
DIGEST = "DIGEST"
"""to be used to set ``DIGEST`` HTTP Authentication method."""
_allowedAuth = [BASIC, DIGEST]

# Possible SPARQL/SPARUL query type (aka SPARQL Query forms)
SELECT = "SELECT"
"""to be used to set the query type to ``SELECT``. This is, usually, determined automatically."""
CONSTRUCT = "CONSTRUCT"
"""to be used to set the query type to ``CONSTRUCT``. This is, usually, determined automatically."""
ASK = "ASK"
"""to be used to set the query type to ``ASK``. This is, usually, determined automatically."""
DESCRIBE = "DESCRIBE"
"""to be used to set the query type to ``DESCRIBE``. This is, usually, determined automatically."""
INSERT = "INSERT"
"""to be used to set the query type to ``INSERT``. This is, usually, determined automatically."""
DELETE = "DELETE"
"""to be used to set the query type to ``DELETE``. This is, usually, determined automatically."""
CREATE = "CREATE"
"""to be used to set the query type to ``CREATE``. This is, usually, determined automatically."""
CLEAR = "CLEAR"
"""to be used to set the query type to ``CLEAR``. This is, usually, determined automatically."""
DROP = "DROP"
"""to be used to set the query type to ``DROP``. This is, usually, determined automatically."""
LOAD = "LOAD"
"""to be used to set the query type to ``LOAD``. This is, usually, determined automatically."""
COPY = "COPY"
"""to be used to set the query type to ``COPY``. This is, usually, determined automatically."""
MOVE = "MOVE"
"""to be used to set the query type to ``MOVE``. This is, usually, determined automatically."""
ADD = "ADD"
"""to be used to set the query type to ``ADD``. This is, usually, determined automatically."""
_allowedQueryTypes = [
    SELECT,
    CONSTRUCT,
    ASK,
    DESCRIBE,
    INSERT,
    DELETE,
    CREATE,
    CLEAR,
    DROP,
    LOAD,
    COPY,
    MOVE,
    ADD,
]

# Possible methods to perform requests
URLENCODED = "urlencoded"
"""to be used to set **URL encode** as the encoding method for the request.
This is, usually, determined automatically."""
POSTDIRECTLY = "postdirectly"
"""to be used to set **POST directly** as the encoding method for the request.
This is, usually, determined automatically."""
_REQUEST_METHODS = [URLENCODED, POSTDIRECTLY]

# Possible output format (mime types) that can be converted by the local script. Unfortunately,
# it does not work by simply setting the return format, because there is still a certain level of confusion
# among implementations.
# For example, Joseki returns application/javascript and not the sparql-results+json thing that is required...
# Ie, alternatives should be given...
# Andy Seaborne told me (June 2007) that the right return format is now added to his CVS, ie, future releases of
# joseki will be o.k., too. The situation with turtle and n3 is even more confusing because the text/n3 and text/turtle
# mime types have just been proposed and not yet widely used...

_SPARQL_DEFAULT = ["application/sparql-results+xml", "application/rdf+xml", "*/*"]
_SPARQL_XML = ["application/sparql-results+xml"]
_SPARQL_JSON = [
    "application/sparql-results+json",
    "application/json",
    "text/javascript",
    "application/javascript",
]  # VIVO server returns "application/javascript"
_RDF_XML = ["application/rdf+xml"]
_RDF_TURTLE = ["application/turtle", "text/turtle"]
_RDF_N3 = _RDF_TURTLE + [
    "text/rdf+n3",
    "application/n-triples",
    "application/n3",
    "text/n3",
]
_RDF_JSONLD = ["application/ld+json", "application/x-json+ld"]
_CSV = ["text/csv"]
_TSV = ["text/tab-separated-values"]
_XML = ["application/xml"]
_ALL = ["*/*"]
_RDF_POSSIBLE = _RDF_XML + _RDF_N3 + _XML + _RDF_JSONLD

_SPARQL_PARAMS = ["query"]

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
    reset to its initial values using the :meth:`resetQuery` method.

    :ivar endpoint: SPARQL endpoint's URI.
    :vartype endpoint: string
    :ivar updateEndpoint: SPARQL endpoint's URI for SPARQL Update operations (if it's a different one).
    The **default** value is ``None``.
    :vartype updateEndpoint: string
    :ivar agent: The User-Agent for the HTTP request header. The **default** value is an autogenerated string using t
    he SPARQLWrapper version code.
    :vartype agent: string
    :ivar _defaultGraph: URI for the default graph. The value can be set either via an explicit call
    :func:`addParameter("default-graph-uri", uri)<addParameter>` or as part of the query string. The **default**
    value is ``None``.
    :vartype _defaultGraph: string
    :ivar user: The username of the credentials for querying the current endpoint. The value can be set an explicit
    call :func:`setCredentials`. The **default** value is ``None``.
    :vartype user: string
    :ivar passwd: The password of the credentials for querying the current endpoint. The value can be set an explicit
    call :func:`setCredentials`. The **default** value is ``None``.
    :vartype passwd: string
    :ivar http_auth: HTTP Authentication type. The **default** value is :data:`BASIC`. Possible values are
    :data:`BASIC` or :data:`DIGEST`. It is used only in case the credentials are set.
    :vartype http_auth: string
    :ivar onlyConneg: Option for allowing (or not) **only** HTTP Content Negotiation (so dismiss the use of HTTP
    parameters). The default value is ``False``.
    :vartype onlyConneg: boolean
    :ivar customHttpHeaders: Custom HTTP Headers to be included in the request. It is a dictionary where keys are the
    header field and values are the header values. **Important**: These headers override previous values (including
    ``Content-Type``, ``User-Agent``, ``Accept`` and ``Authorization`` if they are present).
    :vartype customHttpHeaders: dict
    :ivar timeout: The timeout (in seconds) to use for querying the endpoint.
    :vartype timeout: int
    :ivar queryString: The SPARQL query text.
    :vartype queryString: string
    :ivar queryType: The type of SPARQL query (aka SPARQL query form), like :data:`CONSTRUCT`, :data:`SELECT`,
    :data:`ASK`, :data:`DESCRIBE`, :data:`INSERT`, :data:`DELETE`, :data:`CREATE`, :data:`CLEAR`, :data:`DROP`,
    :data:`LOAD`, :data:`COPY`, :data:`MOVE` or :data:`ADD` (constants in this module).
    :vartype queryType: string
    :ivar returnFormat: The return format.\
    No local check is done, so the parameter is simply sent to the endpoint. Eg, if the value is set to :data:`JSON`
    and a construct query is issued, it is up to the endpoint to react or not, this wrapper does not check.\
    The possible values are :data:`JSON`, :data:`XML`, :data:`TURTLE`, :data:`N3`, :data:`RDF`, :data:`RDFXML`,
    :data:`CSV`, :data:`TSV`, :data:`JSONLD` (constants in this module).\
    The **default** value is :data:`XML`.
    :vartype returnFormat: string
    :ivar requestMethod: The request method for query or update operations. The possibles values are URL-encoded
    (:data:`URLENCODED`) or POST directly (:data:`POSTDIRECTLY`).
    :vartype requestMethod: string
    :ivar method: The invocation method (HTTP verb).  The **default** value is :data:`GET`, but it can be set to
    :data:`POST`.
    :vartype method: string
    :ivar parameters: The parameters of the request (key/value pairs in a dictionary).
    :vartype parameters: dict
    :ivar _defaultReturnFormat: The default return format. It is used in case the same class instance is reused for
    subsequent queries.
    :vartype _defaultReturnFormat: string

    :cvar prefix_pattern: regular expression used to remove base/prefixes in the process of determining the query type.
    :vartype prefix_pattern: :class:`re.RegexObject`, a compiled regular expression. See the :mod:`re` module of Python
    :cvar pattern: regular expression used to determine whether a query (without base/prefixes) is of type
    :data:`CONSTRUCT`, :data:`SELECT`, :data:`ASK`, :data:`DESCRIBE`, :data:`INSERT`, :data:`DELETE`, :data:`CREATE`,
    :data:`CLEAR`, :data:`DROP`, :data:`LOAD`, :data:`COPY`, :data:`MOVE` or :data:`ADD`.
    :vartype pattern: :class:`re.RegexObject`, a compiled regular expression. See the :mod:`re` module of Python
    :cvar comments_pattern: regular expression used to remove comments from a query.
    :vartype comments_pattern: :class:`re.RegexObject`, a compiled regular expression. See the :mod:`re` module of
    Python
    """

    prefix_pattern = re.compile(
        r"((?P<base>(\s*BASE\s*<.*?>)\s*)|(?P<prefixes>(\s*PREFIX\s+.+:\s*<.*?>)\s*))*"
    )
    # Maybe the future name could be queryType_pattern
    pattern = re.compile(
        r"(?P<queryType>(CONSTRUCT|SELECT|ASK|DESCRIBE|INSERT|DELETE|CREATE|CLEAR|DROP|LOAD|COPY|MOVE|ADD))",
        re.VERBOSE | re.IGNORECASE,
    )
    comments_pattern = re.compile(r"(^|\n)\s*#.*?\n")

    def __init__(
        self,
        endpoint: str,
        updateEndpoint: Optional[str] = None,
        returnFormat: str = XML,
        defaultGraph: Optional[str] = None,
        agent: str = __agent__,
    ) -> None:
        """
        Class encapsulating a full SPARQL call.

        :param endpoint: SPARQL endpoint's URI.
        :type endpoint: string
        :param updateEndpoint: SPARQL endpoint's URI for update operations (if it's a different one). The **default**
        value is ``None``.
        :type updateEndpoint: string
        :param returnFormat: The return format.\
        No local check is done, so the parameter is simply sent to the endpoint. Eg, if the value is set to
        :data:`JSON` and a construct query is issued, it is up to the endpoint to react or not, this wrapper does not
        check.\
        The possible values are :data:`JSON`, :data:`XML`, :data:`TURTLE`, :data:`N3`, :data:`RDF`, :data:`RDFXML`,
        :data:`CSV`, :data:`TSV`, :data:`JSONLD` (constants in this module).\
        The **default** value is :data:`XML`.
        :param defaultGraph: URI for the default graph. The value can be set either via an explicit call
        :func:`addParameter("default-graph-uri", uri)<addParameter>` or as part of the query string. The
        **default** value is ``None``.
        :type defaultGraph: string
        :param agent: The User-Agent for the HTTP request header. The **default** value is an autogenerated string
        using the SPARQLWrapper version number.
        :type agent: string
        """
        self.endpoint = endpoint
        self.updateEndpoint = updateEndpoint if updateEndpoint else endpoint
        self.agent = agent
        self.user: Optional[str] = None
        self.passwd: Optional[str] = None
        self.http_auth = BASIC
        self._defaultGraph = defaultGraph
        self.onlyConneg = False  # Only Content Negotiation
        self.customHttpHeaders: Dict[str, str] = {}
        self.timeout: Optional[int]

        if returnFormat in _allowedFormats:
            self._defaultReturnFormat = returnFormat
        else:
            self._defaultReturnFormat = XML

        self.resetQuery()

    def resetQuery(self) -> None:
        """Reset the query, ie, return format, method, query, default or named graph settings, etc,
        are reset to their default values. This includes the default values for parameters, method, timeout or
        requestMethod.
        """
        self.parameters: Dict[str, List[str]] = {}
        if self._defaultGraph:
            self.addParameter("default-graph-uri", self._defaultGraph)
        self.returnFormat = self._defaultReturnFormat
        self.method = GET
        self.setQuery("""SELECT * WHERE{ ?s ?p ?o }""")
        self.timeout = None
        self.requestMethod = URLENCODED

    def setReturnFormat(self, format: str) -> None:
        """Set the return format. If the one set is not an allowed value, the setting is ignored.

        :param format: Possible values are :data:`JSON`, :data:`XML`, :data:`TURTLE`, :data:`N3`, :data:`RDF`,
        :data:`RDFXML`, :data:`CSV`, :data:`TSV`, :data:`JSONLD` (constants in this module). All other cases
        are ignored.
        :type format: string
        :raises ValueError: If :data:`JSONLD` is tried to set and the current instance does not support ``JSON-LD``.
        """
        if format in _allowedFormats:
            self.returnFormat = format
        else:
            warnings.warn(
                "Ignore format '%s'; current instance supports: %s."
                % (format, ", ".join(_allowedFormats)),
                SyntaxWarning,
            )

    def supportsReturnFormat(self, format: str) -> bool:
        """Check if a return format is supported.

        :param format: Possible values are :data:`JSON`, :data:`XML`, :data:`TURTLE`, :data:`N3`, :data:`RDF`,
        :data:`RDFXML`, :data:`CSV`, :data:`TSV`, :data:`JSONLD` (constants in this module). All other cases
        are ignored.
        :type format: string
        :return: Returns ``True`` if the return format is supported, otherwise ``False``.
        :rtype: bool
        """
        return format in _allowedFormats

    def setTimeout(self, timeout: int) -> None:
        """Set the timeout (in seconds) to use for querying the endpoint.

        :param timeout: Timeout in seconds.
        :type timeout: int
        """
        self.timeout = int(timeout)

    def setOnlyConneg(self, onlyConneg: bool) -> None:
        """Set this option for allowing (or not) only HTTP Content Negotiation (so dismiss the use of HTTP parameters).

        .. versionadded:: 1.8.1

        :param onlyConneg: ``True`` if **only** HTTP Content Negotiation is allowed; ``False`` if HTTP parameters
        are used.
        :type onlyConneg: bool
        """
        self.onlyConneg = onlyConneg

    def setRequestMethod(self, method: str) -> None:
        """Set the internal method to use to perform the request for query or
        update operations, either URL-encoded (:data:`URLENCODED`) or
        POST directly (:data:`POSTDIRECTLY`).
        Further details at `query operation in SPARQL <http://www.w3.org/TR/sparql11-protocol/#query-operation>`_
        and `update operation in SPARQL Update <http://www.w3.org/TR/sparql11-protocol/#update-operation>`_.

        :param method: Possible values are :data:`URLENCODED` (URL-encoded) or :data:`POSTDIRECTLY` (POST directly).
        All other cases are ignored.
        :type method: string
        """
        if method in _REQUEST_METHODS:
            self.requestMethod = method
        else:
            warnings.warn("invalid update method '%s'" % method, RuntimeWarning)

    def addDefaultGraph(self, uri: str) -> None:
        """
        Add a default graph URI.

        .. deprecated:: 1.6.0 Use :func:`addParameter("default-graph-uri", uri)<addParameter>` instead of this
        method.

        :param uri: URI of the default graph.
        :type uri: string
        """
        self.addParameter("default-graph-uri", uri)

    def addNamedGraph(self, uri: str) -> None:
        """
        Add a named graph URI.

        .. deprecated:: 1.6.0 Use :func:`addParameter("named-graph-uri", uri)<addParameter>` instead of this
        method.

        :param uri: URI of the named graph.
        :type uri: string
        """
        self.addParameter("named-graph-uri", uri)

    def addExtraURITag(self, key: str, value: str) -> None:
        """
        Some SPARQL endpoints require extra key value pairs.
        E.g., in virtuoso, one would add ``should-sponge=soft`` to the query forcing
        virtuoso to retrieve graphs that are not stored in its local database.
        Alias of :func:`addParameter` method.

        .. deprecated:: 1.6.0 Use :func:`addParameter(key, value)<addParameter>` instead of this method

        :param key: key of the query part.
        :type key: string
        :param value: value of the query part.
        :type value: string
        """
        self.addParameter(key, value)

    def addCustomParameter(self, name: str, value: str) -> bool:
        """
        Method is kept for backwards compatibility. Historically, it "replaces" parameters instead of adding.

        .. deprecated:: 1.6.0 Use :func:`addParameter(key, value)<addParameter>` instead of this method

        :param name: name.
        :type name: string
        :param value: value.
        :type value: string
        :return: Returns ``True`` if the adding has been accomplished, otherwise ``False``.
        :rtype: bool
        """
        self.clearParameter(name)
        return self.addParameter(name, value)

    def addParameter(self, name: str, value: str) -> bool:
        """
        Some SPARQL endpoints allow extra key value pairs.
        E.g., in virtuoso, one would add ``should-sponge=soft`` to the query forcing
        virtuoso to retrieve graphs that are not stored in its local database.
        If the parameter :attr:`query` is tried to be set, this intent is dismissed.
        Returns a boolean indicating if the set has been accomplished.

        :param name: name.
        :type name: string
        :param value: value.
        :type value: string
        :return: Returns ``True`` if the adding has been accomplished, otherwise ``False``.
        :rtype: bool
        """
        if name in _SPARQL_PARAMS:
            return False
        else:
            if name not in self.parameters:
                self.parameters[name] = []
            self.parameters[name].append(value)
            return True

    def addCustomHttpHeader(self, httpHeaderName: str, httpHeaderValue: str) -> None:
        """
        Add a custom HTTP header (this method can override all HTTP headers).

        **Important**: Take into account that each previous value for the header field names
        ``Content-Type``, ``User-Agent``, ``Accept`` and ``Authorization`` would be overriden
        if the header field name is present as value of the parameter :attr:`httpHeaderName`.

        .. versionadded:: 1.8.2

        :param httpHeaderName: The header field name.
        :type httpHeaderName: string
        :param httpHeaderValue: The header field value.
        :type httpHeaderValue: string
        """
        self.customHttpHeaders[httpHeaderName] = httpHeaderValue

    def clearCustomHttpHeader(self, httpHeaderName: str) -> bool:
        """
        Clear the values of a custom HTTP Header previously set.
        Returns a boolean indicating if the clearing has been accomplished.

        .. versionadded:: 1.8.2

        :param httpHeaderName: HTTP header name.
        :type httpHeaderName: string
        :return: Returns ``True`` if the clearing has been accomplished, otherwise ``False``.
        :rtype: bool
        """
        try:
            del self.customHttpHeaders[httpHeaderName]
            return True
        except KeyError:
            return False

    def clearParameter(self, name: str) -> bool:
        """
        Clear the values of a concrete parameter.
        Returns a boolean indicating if the clearing has been accomplished.

        :param name: name
        :type name: string
        :return: Returns ``True`` if the clearing has been accomplished, otherwise ``False``.
        :rtype: bool
        """
        if name in _SPARQL_PARAMS:
            return False
        else:
            try:
                del self.parameters[name]
                return True
            except KeyError:
                return False

    def setCredentials(
        self, user: Optional[str], passwd: Optional[str], realm: str = "SPARQL"
    ) -> None:
        """
        Set the credentials for querying the current endpoint.

        :param user: username.
        :type user: string
        :param passwd: password.
        :type passwd: string
        :param realm: realm. Only used for :data:`DIGEST` authentication. The **default** value is ``SPARQL``
        :type realm: string

        .. versionchanged:: 1.8.3
           Added :attr:`realm` parameter.
        """
        self.user = user
        self.passwd = passwd
        self.realm = realm

    def setHTTPAuth(self, auth: str) -> None:
        """
        Set the HTTP Authentication type. Possible values are :class:`BASIC` or :class:`DIGEST`.

        :param auth: auth type.
        :type auth: string
        :raises TypeError: If the :attr:`auth` parameter is not an string.
        :raises ValueError: If the :attr:`auth` parameter has not one of the valid values: :class:`BASIC` or
        :class:`DIGEST`.
        """
        if not isinstance(auth, str):
            raise TypeError("setHTTPAuth takes a string")
        elif auth.upper() in _allowedAuth:
            self.http_auth = auth.upper()
        else:
            valid_types = ", ".join(_allowedAuth)
            raise ValueError("Value should be one of {0}".format(valid_types))

    def setQuery(self, query: Union[str, bytes]) -> None:
        """
        Set the SPARQL query text.

        .. note::
          No check is done on the validity of the query
          (syntax or otherwise) by this module, except for testing the query type (SELECT,
          ASK, etc). Syntax and validity checking is done by the SPARQL service itself.

        :param query: query text.
        :type query: string
        :raises TypeError: If the :attr:`query` parameter is not an unicode-string or utf-8 encoded byte-string.
        """
        if isinstance(query, str):
            pass
        elif isinstance(query, bytes):
            query = query.decode("utf-8")
        else:
            raise TypeError(
                "setQuery takes either unicode-strings or utf-8 encoded byte-strings"
            )

        self.queryString = query
        self.queryType = self._parseQueryType(query)

    def _parseQueryType(self, query: str) -> Optional[str]:
        """
        Internal method for parsing the SPARQL query and return its type (ie, :data:`SELECT`, :data:`ASK`, etc).

        .. note::
          The method returns :data:`SELECT` if nothing is specified. This is just to get all other
          methods running; in fact, this means that the query is erroneous, because the query must be,
          according to the SPARQL specification. The
          SPARQL endpoint should raise an exception (via :mod:`urllib`) for such syntax error.

        :param query: query text.
        :type query: string
        :return: the type of SPARQL query (aka SPARQL query form).
        :rtype: string
        """
        try:
            query = (
                query if (isinstance(query, str)) else query.encode("ascii", "ignore")
            )
            query = self._cleanComments(query)
            query_for_queryType = re.sub(self.prefix_pattern, "", query.strip())
            # type error: Item "None" of "Optional[Match[str]]" has no attribute "group"
            r_queryType = (
                self.pattern.search(query_for_queryType).group("queryType").upper()  # type: ignore[union-attr]
            )
        except AttributeError:
            warnings.warn(
                "not detected query type for query '%r'" % query.replace("\n", " "),
                RuntimeWarning,
            )
            r_queryType = None

        if r_queryType in _allowedQueryTypes:
            return r_queryType
        else:
            # raise Exception("Illegal SPARQL Query; must be one of SELECT, ASK, DESCRIBE, or CONSTRUCT")
            warnings.warn("unknown query type '%s'" % r_queryType, RuntimeWarning)
            return SELECT

    def setMethod(self, method: str) -> None:
        """Set the invocation method. By default, this is :data:`GET`, but can be set to :data:`POST`.

        :param method: should be either :data:`GET` or :data:`POST`. Other cases are ignored.
        :type method: string
        """
        if method in _allowedRequests:
            self.method = method

    def setUseKeepAlive(self) -> None:
        """Make :mod:`urllib2` use keep-alive.

        :raises ImportError: when could not be imported ``keepalive.HTTPHandler``.
        """
        try:
            from keepalive import HTTPHandler  # type: ignore[import]

            if urllib.request._opener and any(  # type: ignore[attr-defined]
                isinstance(h, HTTPHandler) for h in urllib.request._opener.handlers  # type: ignore[attr-defined]
            ):
                # already installed
                return

            keepalive_handler = HTTPHandler()
            opener = urllib.request.build_opener(keepalive_handler)
            urllib.request.install_opener(opener)
        except ImportError:
            warnings.warn(
                "keepalive support not available, so the execution of this method has no effect"
            )

    def isSparqlUpdateRequest(self) -> bool:
        """Returns ``True`` if SPARQLWrapper is configured for executing SPARQL Update request.

        :return: Returns ``True`` if SPARQLWrapper is configured for executing SPARQL Update request.
        :rtype: bool
        """
        return self.queryType in [
            INSERT,
            DELETE,
            CREATE,
            CLEAR,
            DROP,
            LOAD,
            COPY,
            MOVE,
            ADD,
        ]

    def isSparqlQueryRequest(self) -> bool:
        """Returns ``True`` if SPARQLWrapper is configured for executing SPARQL Query request.

        :return: Returns ``True`` if SPARQLWrapper is configured for executing SPARQL Query request.
        :rtype: bool
        """
        return not self.isSparqlUpdateRequest()

    def _cleanComments(self, query: str) -> str:
        """Internal method for returning the query after all occurrence of singleline comments are removed
        (issues #32 and #77).

        :param query: The query.
        :type query: string
        :return: the query after all occurrence of singleline comments are removed.
        :rtype: string
        """
        return re.sub(self.comments_pattern, "\n\n", query)

    def _getRequestEncodedParameters(
        self, query: Optional[Tuple[str, str]] = None
    ) -> str:
        """ Internal method for getting the request encoded parameters.

        :param query: a tuple of two items. The first item can be the string \
        ``query`` (for :data:`SELECT`, :data:`DESCRIBE`, :data:`ASK`, :data:`CONSTRUCT` query) or the string
        ``update`` (for SPARQL Update queries, like :data:`DELETE` or :data:`INSERT`). The second item of the tuple
        is the query string itself.
        :type query: tuple
        :return: the request encoded parameters.
        :rtype: string
        """
        query_parameters = self.parameters.copy()

        # in case of query = tuple("query"/"update", queryString)
        if query and isinstance(query, tuple) and len(query) == 2:
            query_parameters[query[0]] = [query[1]]

        if not self.isSparqlUpdateRequest():
            # This is very ugly. The fact is that the key for the choice of the output format is not defined.
            # Virtuoso uses 'format',sparqler uses 'output'
            # However, these processors are (hopefully) oblivious to the parameters they do not understand.
            # So: just repeat all possibilities in the final URI. UGLY!!!!!!!
            if not self.onlyConneg:
                for f in _returnFormatSetting:
                    query_parameters[f] = [self.returnFormat]
                    # Virtuoso is not supporting a correct Accept header and an unexpected "output"/"format" parameter
                    # value. It returns a 406.
                    # "tsv", "rdf+xml" and "json-ld" are not supported as a correct "output"/"format" parameter value
                    # but "text/tab-separated-values" or "application/rdf+xml" are a valid values,
                    # and there is no problem to send both (4store does not support unexpected values).
                    if self.returnFormat in [TSV, JSONLD, RDFXML]:
                        acceptHeader = (
                            self._getAcceptHeader()
                        )  # to obtain the mime-type "text/tab-separated-values" or "application/rdf+xml"
                        if "*/*" in acceptHeader:
                            acceptHeader = ""  # clear the value in case of "*/*"
                        query_parameters[f] += [acceptHeader]

        pairs = (
            "%s=%s"
            % (
                urllib.parse.quote_plus(param.encode("UTF-8"), safe="/"),
                urllib.parse.quote_plus(value.encode("UTF-8"), safe="/"),
            )
            for param, values in query_parameters.items()
            for value in values
        )
        return "&".join(pairs)

    def _getAcceptHeader(self) -> str:
        """Internal method for getting the HTTP Accept Header.

        .. seealso:: `Hypertext Transfer Protocol -- HTTP/1.1 - Header Field Definitions
        <https://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.1>`_
        """
        if self.queryType in [SELECT, ASK]:
            if self.returnFormat == XML:
                acceptHeader = ",".join(_SPARQL_XML)
            elif self.returnFormat == JSON:
                acceptHeader = ",".join(_SPARQL_JSON)
            elif (
                self.returnFormat == CSV
            ):  # Allowed for SELECT and ASK (https://www.w3.org/TR/2013/REC-sparql11-protocol-20130321/#query-success)
                # but only described for SELECT (https://www.w3.org/TR/sparql11-results-csv-tsv/)
                acceptHeader = ",".join(_CSV)
            elif (
                self.returnFormat == TSV
            ):  # Allowed for SELECT and ASK (https://www.w3.org/TR/2013/REC-sparql11-protocol-20130321/#query-success)
                # but only described for SELECT (https://www.w3.org/TR/sparql11-results-csv-tsv/)
                acceptHeader = ",".join(_TSV)
            else:
                acceptHeader = ",".join(_ALL)
                warnings.warn(
                    "Sending Accept header '*/*' because unexpected returned format '%s' in a '%s' SPARQL query form"
                    % (self.returnFormat, self.queryType),
                    RuntimeWarning,
                )
        elif self.queryType in [CONSTRUCT, DESCRIBE]:
            if self.returnFormat == TURTLE:
                acceptHeader = ",".join(_RDF_TURTLE)
            elif self.returnFormat == N3:
                acceptHeader = ",".join(_RDF_N3)
            elif self.returnFormat == XML or self.returnFormat == RDFXML:
                acceptHeader = ",".join(_RDF_XML)
            elif self.returnFormat == JSONLD and JSONLD in _allowedFormats:
                acceptHeader = ",".join(_RDF_JSONLD)
            else:
                acceptHeader = ",".join(_ALL)
                warnings.warn(
                    "Sending Accept header '*/*' because unexpected returned format '%s' in a '%s' SPARQL query form"
                    % (self.returnFormat, self.queryType),
                    RuntimeWarning,
                )
        elif self.queryType in [
            INSERT,
            DELETE,
            CREATE,
            CLEAR,
            DROP,
            LOAD,
            COPY,
            MOVE,
            ADD,
        ]:
            if self.returnFormat == XML:
                acceptHeader = ",".join(_SPARQL_XML)
            elif self.returnFormat == JSON:
                acceptHeader = ",".join(_SPARQL_JSON)
            else:
                acceptHeader = ",".join(_ALL)
        else:
            acceptHeader = "*/*"
        return acceptHeader

    def _createRequest(self) -> urllib.request.Request:
        """Internal method to create request according a HTTP method. Returns a
        :class:`urllib2.Request` object of the :mod:`urllib2` Python library

        :raises NotImplementedError: If the HTTP authentification method is not one of the valid values: :data:`BASIC`
        or :data:`DIGEST`.
        :return: request a :class:`urllib2.Request` object of the :mod:`urllib2` Python library
        """
        request = None

        if self.isSparqlUpdateRequest():
            # protocol details at http://www.w3.org/TR/sparql11-protocol/#update-operation
            uri = self.updateEndpoint

            if self.method != POST:
                warnings.warn("update operations MUST be done by POST")

            if self.requestMethod == POSTDIRECTLY:
                request = urllib.request.Request(
                    uri + "?" + self._getRequestEncodedParameters()
                )
                request.add_header("Content-Type", "application/sparql-update")
                request.data = self.queryString.encode("UTF-8")
            else:  # URL-encoded
                request = urllib.request.Request(uri)
                request.add_header("Content-Type", "application/x-www-form-urlencoded")
                request.data = self._getRequestEncodedParameters(
                    ("update", self.queryString)
                ).encode("ascii")
        else:
            # protocol details at http://www.w3.org/TR/sparql11-protocol/#query-operation
            uri = self.endpoint

            if self.method == POST:
                if self.requestMethod == POSTDIRECTLY:
                    request = urllib.request.Request(
                        uri + "?" + self._getRequestEncodedParameters()
                    )
                    request.add_header("Content-Type", "application/sparql-query")
                    request.data = self.queryString.encode("UTF-8")
                else:  # URL-encoded
                    request = urllib.request.Request(uri)
                    request.add_header(
                        "Content-Type", "application/x-www-form-urlencoded"
                    )
                    request.data = self._getRequestEncodedParameters(
                        ("query", self.queryString)
                    ).encode("ascii")
            else:  # GET
                request = urllib.request.Request(
                    uri
                    + "?"
                    + self._getRequestEncodedParameters(("query", self.queryString))
                )

        request.add_header("User-Agent", self.agent)
        request.add_header("Accept", self._getAcceptHeader())
        if self.user and self.passwd:
            if self.http_auth == BASIC:
                credentials = "%s:%s" % (self.user, self.passwd)
                request.add_header(
                    "Authorization",
                    "Basic %s"
                    % base64.b64encode(credentials.encode("utf-8")).decode("utf-8"),
                )
            elif self.http_auth == DIGEST:
                realm = self.realm
                pwd_mgr = urllib.request.HTTPPasswordMgr()
                pwd_mgr.add_password(realm, uri, self.user, self.passwd)
                opener = urllib.request.build_opener()
                opener.add_handler(urllib.request.HTTPDigestAuthHandler(pwd_mgr))
                urllib.request.install_opener(opener)
            else:
                valid_types = ", ".join(_allowedAuth)
                raise NotImplementedError(
                    "Expecting one of: {0}, but received: {1}".format(
                        valid_types, self.http_auth
                    )
                )

        # The header field name is capitalized in the request.add_header method.
        for customHttpHeader in self.customHttpHeaders:
            request.add_header(
                customHttpHeader, self.customHttpHeaders[customHttpHeader]
            )

        return request

    def _query(self) -> Tuple[HTTPResponse, str]:
        """Internal method to execute the query. Returns the output of the
        :func:`urllib2.urlopen` method of the :mod:`urllib2` Python library

        :return: tuples with the raw request plus the expected format.
        :raises QueryBadFormed: If the HTTP return code is ``400``.
        :raises Unauthorized: If the HTTP return code is ``401``.
        :raises EndPointNotFound: If the HTTP return code is ``404``.
        :raises URITooLong: If the HTTP return code is ``414``.
        :raises EndPointInternalError: If the HTTP return code is ``500``.
        :raises urllib2.HTTPError: If the HTTP return code is different to ``400``, ``401``, ``404``, ``414``, ``500``.
        """
        request = self._createRequest()

        try:
            if self.timeout:
                response = urlopener(request, timeout=self.timeout)
            else:
                response = urlopener(request)
            return response, self.returnFormat
        except urllib.error.HTTPError as e:
            if e.code == 400:
                raise QueryBadFormed(e.read())
            elif e.code == 404:
                raise EndPointNotFound(e.read())
            elif e.code == 401:
                raise Unauthorized(e.read())
            elif e.code == 414:
                raise URITooLong(e.read())
            elif e.code == 500:
                raise EndPointInternalError(e.read())
            else:
                raise e

    def query(self) -> "QueryResult":
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

        :return: query result
        :rtype: :class:`QueryResult` instance
        """
        return QueryResult(self._query())

    def queryAndConvert(self) -> "QueryResult.ConvertResult":
        """Macro like method: issue a query and return the converted results.

        :return: the converted query result. See the conversion methods for more details.
        """
        res = self.query()
        return res.convert()

    def __str__(self) -> str:
        """This method returns the string representation of a :class:`SPARQLWrapper` object.

        .. versionadded:: 1.8.3

        :return: A human-readable string of the object.
        :rtype: string
        """
        fullname = self.__module__ + "." + self.__class__.__name__
        items = ('"%s" : %r' % (k, v) for k, v in sorted(self.__dict__.items()))
        str_dict_items = "{%s}" % (",\n".join(items))
        return "<%s object at 0x%016X>\n%s" % (fullname, id(self), str_dict_items)


#######################################################################################################


class QueryResult(object):
    """
    Wrapper around an a query result. Users should not create instances of this class, it is
    generated by a :func:`SPARQLWrapper.query` call. The results can be
    converted to various formats, or used directly.

    If used directly: the class gives access to the direct HTTP request results
    ``response`` obtained from the call to :func:`urllib.urlopen`.
    It is a file-like object with two additional methods:

    * ``geturl()`` to return the URL of the resource retrieved
    * ``info()`` that returns the meta-information of the HTTP result as a dictionary-like object.

    For convenience, these methods are also available on the :class:`QueryResult` instance.

    The :func:`__iter__` and :func:`next` methods are also implemented (by mapping them to :attr:`response`). This
    means that the common idiom ``for l in obj : do_something_with_line(l)`` would work, too.

    :ivar response: the direct HTTP response; a file-like object, as return by the :func:`urllib2.urlopen` library call.
    :ivar requestedFormat: The requested format. The possible values are: :data:`JSON`, :data:`XML`, :data:`RDFXML`,
    :data:`TURTLE`, :data:`N3`, :data:`RDF`, :data:`CSV`, :data:`TSV`, :data:`JSONLD`.
    :type requestedFormat: string

    """

    ConvertResult = Union[bytes, str, Dict[Any, Any], "Graph", Document, None]

    def __init__(self, result: Union[HTTPResponse, Tuple[HTTPResponse, str]]) -> None:
        """
        :param result: HTTP response stemming from a :func:`SPARQLWrapper.query` call, or a tuple with the expected
        format: (response, format).
        """
        if isinstance(result, tuple):
            self.response = result[0]
            self.requestedFormat = result[1]
        else:
            self.response = result

    def geturl(self) -> str:
        """Return the URL of the original call.

        :return: URL of the original call.
        :rtype: string
        """
        return self.response.geturl()

    def info(self) -> KeyCaseInsensitiveDict[str]:
        """Return the meta-information of the HTTP result.

        :return: meta-information of the HTTP result.
        :rtype: dict
        """
        return KeyCaseInsensitiveDict(dict(self.response.info()))

    def __iter__(self) -> Iterator[bytes]:
        """Return an iterator object. This method is expected for the inclusion
        of the object in a standard ``for`` loop.
        """
        return self.response.__iter__()

    def __next__(self) -> bytes:
        """Method for the standard iterator."""
        return next(self.response)

    def _convertJSON(self) -> Dict[Any, Any]:
        """
        Convert a JSON result into a Python dict. This method can be overwritten in a subclass
        for a different conversion method.

        :return: converted result.
        :rtype: dict
        """
        json_str = json.loads(self.response.read().decode("utf-8"))
        if isinstance(json_str, dict):
            return json_str
        else:
            raise TypeError(type(json_str))

    def _convertXML(self) -> Document:
        """
        Convert an XML result into a Python dom tree. This method can be overwritten in a
        subclass for a different conversion method.

        :return: converted result.
        :rtype: :class:`xml.dom.minidom.Document`
        """
        doc = parse(self.response)
        rdoc = cast(Document, doc)
        return rdoc

    def _convertRDF(self) -> "Graph":
        """
        Convert a RDF/XML result into an RDFLib Graph. This method can be overwritten
        in a subclass for a different conversion method.

        :return: converted result.
        :rtype: :class:`rdflib.graph.Graph`
        """
        from rdflib import ConjunctiveGraph
        retval = ConjunctiveGraph()
        retval.parse(self.response, format="xml")  # type: ignore[no-untyped-call]
        return retval

    def _convertN3(self) -> bytes:
        """
        Convert a RDF Turtle/N3 result into a string. This method can be overwritten in a subclass
        for a different conversion method.

        :return: converted result.
        :rtype: string
        """
        return self.response.read()

    def _convertCSV(self) -> bytes:
        """
        Convert a CSV result into a string. This method can be overwritten in a subclass
        for a different conversion method.

        :return: converted result.
        :rtype: string
        """
        return self.response.read()

    def _convertTSV(self) -> bytes:
        """
        Convert a TSV result into a string. This method can be overwritten in a subclass
        for a different conversion method.

        :return: converted result.
        :rtype: string
        """
        return self.response.read()

    def _convertJSONLD(self) -> "Graph":
        """
        Convert a RDF JSON-LD result into an RDFLib Graph. This method can be overwritten
        in a subclass for a different conversion method.

        :return: converted result
        :rtype: :class:`rdflib.graph.Graph`
        """
        from rdflib import ConjunctiveGraph

        retval = ConjunctiveGraph()
        retval.parse(self.response, format="json-ld")  # type: ignore[no-untyped-call]
        return retval

    def convert(self) -> ConvertResult:
        """
        Encode the return value depending on the return format:

            * in the case of :data:`XML`, a DOM top element is returned
            * in the case of :data:`JSON`, a json conversion will return a dictionary
            * in the case of :data:`RDF/XML<RDFXML>`, the value is converted via RDFLib into a ``RDFLib Graph`` instance
            * in the case of :data:`JSON-LD<JSONLD>`, the value is converted via RDFLib into a ``RDFLib Graph`` instance
            * in the case of RDF :data:`Turtle<TURTLE>`/:data:`N3`, a string is returned
            * in the case of :data:`CSV`/:data:`TSV`, a string is returned
            * In all other cases the input simply returned.

        :return: the converted query result. See the conversion methods for more details.
        """

        def _content_type_in_list(real: str, expected: List[str]) -> bool:
            """Internal method for checking if the content-type header received matches any of the content types of
            the expected list.

            :param real: The content-type header received.
            :type real: string
            :param expected: A list of expected content types.
            :type expected: list
            :return: Returns a boolean after checking if the content-type header received matches any of the content
            types of the expected list.
            :rtype: boolean
            """
            return True in [real.find(mime) != -1 for mime in expected]

        def _validate_format(
            format_name: str, allowed: List[str], mime: str, requested: str
        ) -> None:
            """Internal method for validating if the requested format is one of the allowed formats.

            :param format_name: The format name (to be used in the warning message).
            :type format_name: string
            :param allowed: A list of allowed content types.
            :type allowed: list
            :param mime: The content-type header received (to be used in the warning message).
            :type mime: string
            :param requested: the requested format.
            :type requested: string
            """
            if requested not in allowed:
                message = "Format requested was %s, but %s (%s) has been returned by the endpoint"
                warnings.warn(
                    message % (requested.upper(), format_name, mime), RuntimeWarning
                )

        # TODO. In order to compare properly, the requested QueryType (SPARQL Query Form) is needed. For instance,
        # the unexpected N3 requested for a SELECT would return XML
        if "content-type" in self.info():
            ct = self.info()["content-type"]  # returned Content-Type value

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
                _validate_format(
                    "RDF/XML", [RDF, XML, RDFXML], ct, self.requestedFormat
                )
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
                warnings.warn(
                    "unknown response content type '%s' returning raw response..."
                    % (ct),
                    RuntimeWarning,
                )
        return self.response.read()

    def _get_responseFormat(self) -> Optional[str]:
        """
        Get the response (return) format. The possible values are: :data:`JSON`, :data:`XML`, :data:`RDFXML`,
        :data:`TURTLE`, :data:`N3`, :data:`CSV`, :data:`TSV`, :data:`JSONLD`.
        In case there is no Content-Type, ``None`` is return. In all other cases, the raw Content-Type is return.

        .. versionadded:: 1.8.3

        :return: the response format. The possible values are: :data:`JSON`, :data:`XML`, :data:`RDFXML`,
        :data:`TURTLE`, :data:`N3`, :data:`CSV`, :data:`TSV`, :data:`JSONLD`.
        :rtype: string
        """

        def _content_type_in_list(real: str, expected: List[str]) -> bool:
            """Internal method for checking if the content-type header received matches any of the content types of
            the expected list.

            :param real: The content-type header received.
            :type real: string
            :param expected: A list of expected content types.
            :type expected: list
            :return: Returns a boolean after checking if the content-type header received matches any of the content
            types of the expected list.
            :rtype: boolean
            """
            return True in [real.find(mime) != -1 for mime in expected]

        if "content-type" in self.info():
            ct = self.info()["content-type"]  # returned Content-Type value

            if _content_type_in_list(ct, _SPARQL_XML):
                return XML
            elif _content_type_in_list(ct, _XML):
                return XML
            elif _content_type_in_list(ct, _SPARQL_JSON):
                return JSON
            elif _content_type_in_list(ct, _RDF_XML):
                return RDFXML
            elif _content_type_in_list(ct, _RDF_TURTLE):
                return TURTLE
            elif _content_type_in_list(ct, _RDF_N3):
                return N3
            elif _content_type_in_list(ct, _CSV):
                return CSV
            elif _content_type_in_list(ct, _TSV):
                return TSV
            elif _content_type_in_list(ct, _RDF_JSONLD):
                return JSONLD
            else:
                warnings.warn(
                    "Unknown response content type. Returning raw content-type ('%s')."
                    % (ct),
                    RuntimeWarning,
                )
                return ct
        return None

    def print_results(self, minWidth: Optional[int] = None) -> None:
        """This method prints a representation of a :class:`QueryResult` object that MUST has as response format
        :data:`JSON`.

        :param minWidth: The minimum width, counting as characters. The default value is ``None``.
        :type minWidth: int
        """

        # Check if the requested format was JSON. If not, exit.
        responseFormat = self._get_responseFormat()
        if responseFormat != JSON:
            message = "Format return was %s, but JSON was expected. No printing."
            warnings.warn(message % (responseFormat), RuntimeWarning)
            return None

        results = self._convertJSON()
        if minWidth:
            width = self.__get_results_width(results, minWidth)
        else:
            width = self.__get_results_width(results)
        index = 0
        for var in results["head"]["vars"]:
            print(
                ("?" + var).ljust(width[index]),
                "|",
            )
            index += 1
        print()
        print("=" * (sum(width) + 3 * len(width)))
        for result in results["results"]["bindings"]:
            index = 0
            for var in results["head"]["vars"]:
                result_value = self.__get_prettyprint_string_sparql_var_result(
                    result[var]
                )
                print(
                    result_value.ljust(width[index]),
                    "|",
                )
                index += 1
            print()

    def __get_results_width(
        self, results: Dict[Any, Any], minWidth: int = 2
    ) -> List[int]:
        width: List[int] = []
        for var in results["head"]["vars"]:
            width.append(max(minWidth, len(var) + 1))
        for result in results["results"]["bindings"]:
            index = 0
            for var in results["head"]["vars"]:
                result_value = self.__get_prettyprint_string_sparql_var_result(
                    result[var]
                )
                width[index] = max(width[index], len(result_value))
                index += 1
        return width

    def __get_prettyprint_string_sparql_var_result(self, result: Dict[str, str]) -> str:
        value = result["value"]
        lang = result.get("xml:lang", None)
        datatype = result.get("datatype", None)
        if lang is not None:
            value += "@" + lang
        if datatype is not None:
            value += " [" + datatype + "]"
        return value

    def __str__(self) -> str:
        """This method returns the string representation of a :class:`QueryResult` object.

        :return: A human-readable string of the object.
        :rtype: string
        .. versionadded:: 1.8.3
        """
        fullname = self.__module__ + "." + self.__class__.__name__
        str_requestedFormat = '"requestedFormat" : ' + repr(self.requestedFormat)
        str_url = self.response.geturl()
        str_code = self.response.getcode()
        str_headers = self.response.info()
        str_response = (
            '"response (a file-like object, as return by the urllib2.urlopen library call)" : {\n\t"url" : "'
            '%s",\n\t"code" : "%s",\n\t"headers" : %s}'
            % (str_url, str_code, str_headers)
        )
        return "<%s object at 0x%016X>\n{%s,\n%s}" % (
            fullname,
            id(self),
            str_requestedFormat,
            str_response,
        )
