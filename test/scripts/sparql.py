#!/usr/bin/python
# -*- coding: utf-8 -*-


from SPARQLWrapper import SPARQLWrapper2, SPARQLWrapper, TURTLE
import sys, getopt

localSparqler = "http://localhost:2020/sparql"
localVirtuoso = "http://localhost:8890/sparql"

def main(server,query,sponge=False) :
    sparql = SPARQLWrapper2(server)
    if sponge : sparql.addExtraURITag("should-sponge","grab-everything")
        
    sparql.setQuery(query)
    res = sparql.query()
    variables = res.variables
    
    print "Variables:"
    print variables
    print
    print "Bindings:"
    for b in res.bindings :
        for v in res.variables :
            try :
                val = b[v]
                if val.lang :
                    str = "%s: %s@%s" % (v,val.value,val.lang)
                elif val.datatype :
                    str = "%s: %s^^%s" % (v,val.value,val.datatype)
                else :
                    str = "%s: %s" % (v,val.value)
            except KeyError :
                # no binding to that one...
                str = "%s: <<None>>" % v
            print str.encode('utf-8')
        print
            
    
    
# -------------------------------------------------------------------------------------------------------------
server   = localSparqler
query    = ""
sponge  = False
usagetxt="""%s [-s] [-u url] [file]
-s:      use local sparqler (default)
-v:      use local virtuoso
-u url:  server url
-p:      issue an extra sponge for virtuoso
file: sparql query file
"""
def usage() :
    print usagetxt % sys.argv[0]
    sys.exit(1)

if __name__ == '__main__' :
    if len(sys.argv) == 1: 
        usage()
    try :
        opts,args = getopt.getopt(sys.argv[1:],"shu:pv")
        for o,a in opts :
            if o == "-s" :
                server = localSparqler
            elif o == "-v" :
                server = localVirtuoso
                sponge = True
            elif o == "-h" :
                print usage
                sys.exit(0)
            elif o == "-u" :
                server = a
            elif o == "-p" :
                sponge = True
        if query == "" and len(args) > 0 :
            inp = file(args[0])
            query = ""
            for l in inp :
                query += l
    except :
        usage()
    if query == "" : usage()
    main(server,query,sponge)

