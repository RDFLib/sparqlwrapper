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

Create an instance to execute your query:

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

