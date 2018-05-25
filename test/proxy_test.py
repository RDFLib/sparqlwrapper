#!/usr/bin/python
# -*- coding: utf-8 -*-

import inspect
import os
import sys
import urllib

# prefer local copy to the one which is installed
# hack from http://stackoverflow.com/a/6098238/280539
_top_level_path = os.path.realpath(os.path.abspath(os.path.join(
    os.path.split(inspect.getfile(inspect.currentframe()))[0],
    ".."
)))
if _top_level_path not in sys.path:
    sys.path.insert(0, _top_level_path)
# end of hack

from SPARQLWrapper import SPARQLWrapper, XML, GET, SELECT
import unittest
from urllib2 import URLError
import socket
import errno  

endpoint = "http://dbpedia.org/sparql"
endpoint_ssl = "https://dbpedia.org/sparql"

prefixes = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
"""

selectQuery = """
    SELECT ?label
    WHERE {
    <http://dbpedia.org/resource/Asturias> rdfs:label ?label .
    }
"""

proxiesWorking = {
            "http":"177.22.107.236:8080", 
            "https":"177.22.107.236:8080"} # Checked using http://www.proxy-checker.org/

proxiesNotWorking = {"http":"127.0.0.1:80", 
                     "https":"127.0.0.1:80"}

class SPARQLWrapperProxyTests(unittest.TestCase):

    def __generic(self, endpoint):
        sparql = SPARQLWrapper(endpoint)
        sparql.setQuery(prefixes + selectQuery)
        sparql.setReturnFormat(XML)
        sparql.setMethod(GET)
        return sparql

    def testProxyWorking(self):
        sparql = self.__generic(endpoint)
        sparql.setProxies(proxiesWorking)
        self.assertTrue(sparql.proxies) # assert no empty

        try:
            result = sparql.query() 
        except URLError as error:
            print "The Proxy server is not responding"
            print error # Because we are not sure that the proxy is working
        else:
            result.convert().toprettyxml()
            self.assertTrue(True)

    def testProxyWorkingSSL(self):
        sparql = self.__generic(endpoint_ssl)
        self.assertEqual(sparql.endpoint, endpoint_ssl) 
        sparql.setProxies(proxiesWorking)
        self.assertTrue(sparql.proxies) # assert no empty

        try:
            result = sparql.query() 
        except URLError as error:
            print "The Proxy server is not responding"
            print error # Because we are not sure that the proxy is working
        else:
            result.convert().toprettyxml()
            self.assertTrue(True)

    def testProxyNotWorking(self):
        sparql = self.__generic(endpoint)
        sparql.setProxies(proxiesNotWorking)
        self.assertTrue(sparql.proxies) # assert no empty

        try:
            result = sparql.query() 
        except URLError as error:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

if __name__ == "__main__":
    unittest.main()
    
    
