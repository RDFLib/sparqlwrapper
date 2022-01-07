"""
Query a SPARQL endpoint and return results as a Pandas dataframe.
"""
from SPARQLWrapper import SPARQLWrapper2, SPARQLWrapper, CSV, SELECT

class QueryException(Exception):
    pass

def get_sparql_dataframe_orig(endpoint, query):
    """ copy paste from: https://github.com/lawlesst/sparql-dataframe """
    # pandas inside to avoid requiring it
    import pandas as pd
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    if sparql.queryType != SELECT:
        raise QueryException("Only SPARQL SELECT queries are supported.")
    sparql.setReturnFormat(CSV)
    results = sparql.query().convert()
    _csv = pd.compat.StringIO(results.decode('utf-8'))
    return pd.read_csv(_csv, sep=",")

def get_sparql_typed_dict(endpoint, query):
    """ modified from: https://github.com/lawlesst/sparql-dataframe """
    # pandas inside to avoid requiring it
    import pandas as pd
    # rdflib in here because there is some meta stuff in the setup.py and Travis fails because rdflib is installed later
    import rdflib.term
    sparql = SPARQLWrapper2(endpoint)
    sparql.setQuery(query)
    if sparql.queryType != SELECT:
        raise QueryException("Only SPARQL SELECT queries are supported.")
    # sparql.setReturnFormat(JSON)
    results = sparql.query()
    # consider perf hacking later, probably slow
    # convert list of dicts to python types
    d = list()
    for x in results.bindings:
        row = dict()
        for k in x:
            v = x[k]
            vv = rdflib.term.Literal(v.value, datatype=v.datatype).toPython()
            row[k] = vv
        d.append(row)
    return d

def get_sparql_dataframe(endpoint, query):
    import pandas as pd
    d = get_sparql_typed_dict(endpoint, query)
    # TODO: will nan fill somehow, make more strict if there is way of getting the nan types from rdflib
    df = pd.DataFrame(d)
    return df
