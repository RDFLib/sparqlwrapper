# -*- coding: utf-8 -*-

"""

SPARQL Wrapper exceptions

@authors: U{Ivan Herman<http://www.ivan-herman.net>}, U{Sergio Fernández<http://www.wikier.org>}, U{Carlos Tejo Alonso<http://www.dayures.net>}
@organization: U{World Wide Web Consortium<http://www.w3.org>} and U{Foundation CTIC<http://www.fundacionctic.org/>}.
@license: U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/copyright-software">}

"""


class SPARQLWrapperException(Exception):
    """
    Base class for SPARQL Wrapper exceptions
    """

    msg = "an exception has occured"
    
    def __init__(self, response=None):
        if response:
            formatted_msg = "%s: %s. \n\nResponse:\n%s" % (self.__class__.__name__, self.msg, response)
        else:
            formatted_msg = "%s: %s." % (self.__class__.__name__, self.msg)

        super(SPARQLWrapperException, self).__init__(formatted_msg)

class EndPointInternalError(SPARQLWrapperException):
    """
    Exception type for 500 Internal Server Error responses.
    """

    msg = "endpoint returned code 500 and response"


class QueryBadFormed(SPARQLWrapperException):
    """
    Query Bad Formed exception
    """

    msg = "a bad request has been sent to the endpoint, probably the sparql query is bad formed"


class EndPointNotFound(SPARQLWrapperException):
    """
    End Point Not Found exception
    """

    msg = "it was impossible to connect with the endpoint in that address, check if it is correct"
