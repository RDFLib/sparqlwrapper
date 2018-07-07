# SPARQL Endpoint interface to Python

[![Build Status](https://secure.travis-ci.org/RDFLib/sparqlwrapper.svg?branch=master)](https://travis-ci.org/RDFLib/sparqlwrapper)
[![PyPi version](https://badge.fury.io/py/SPARQLWrapper.svg)](https://pypi.python.org/pypi/SPARQLWrapper)

`SPARQLWrapper` is a simple Python wrapper around a SPARQL service to remotelly execute your queries.
It helps in creating the query invokation and, possibly, convert the result into a more manageable format. 


## Installation

From PyPi:

    $ pip install sparqlwrapper


From GitHub::

    $ pip install git+https://github.com/rdflib/sparqlwrapper#egg=sparqlwrapper

From Debian

    $ sudo apt-get install python-sparqlwrapper

## Usage

Create an instance to execute your query (SELECT, ASK, CONSTRUCT, DESCRIBE):

```python
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
    print('%s: %s' % (result["label"]["xml:lang"], result["label"]["value"]))
```

```python
from SPARQLWrapper import SPARQLWrapper, XML

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
sparql.setQuery("""
    ASK WHERE { 
        <http://dbpedia.org/resource/Asturias> rdfs:label "Asturias"@es
    }    
""")
sparql.setReturnFormat(XML)
results = sparql.query().convert()
print results.toxml()
```

```python
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
```

```python
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
```

There is also a `SPARQLWrapper2` class that works with JSON SELECT results only and wraps the results to make processing of average queries a bit simpler.

```python
from SPARQLWrapper import SPARQLWrapper2

sparql = SPARQLWrapper2("http://dbpedia.org/sparql")
sparql.setQuery("""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?label
    WHERE { <http://dbpedia.org/resource/Asturias> rdfs:label ?label }
""")

for result in sparql.query().bindings:
    print('%s: %s' % (result["label"].lang, result["label"].value))
```

## Source code

The source distribution contains:

* `SPARQLWrapper`: the Python library. You should copy the directory somewhere into your `PYTHONPATH`. Alternatively, you can also run the distutils scripts:

    python setup.py install

* `test`: some unit and integrations tests
  
* `script`: some scripts to run the library against some SPARQL endpoints.

## Documentation

The SPARQLWrapper documentation is available online at https://rdflib.github.io/sparqlwrapper/doc/latest/.

## License

The package is licensed under [W3C license](https://www.w3.org/Consortium/Legal/2015/copyright-software-and-document).

