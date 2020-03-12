#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

try:
    from ez_setup import use_setuptools
    use_setuptools()
except:
    pass

from setuptools import setup

try:
    import six
    py3 = six.PY3
except:
    py3 = sys.version_info[0] >= 3

# metadata
import re
_version_re = re.compile(r'__version__\s*=\s*"(.*)"')
_authors_re = re.compile(r'__authors__\s*=\s*"(.*)"')
_url_re = re.compile(r'__url__\s*=\s*"(.*)"')

for line in open('SPARQLWrapper/__init__.py'):

    version_match = _version_re.match(line)
    if version_match:
        version = version_match.group(1)

    authors_match = _authors_re.match(line)
    if authors_match:
        authors = authors_match.group(1)

    url_match = _url_re.match(line)
    if url_match:
        url = url_match.group(1)

# requirements
with open('requirements.txt', 'r') as f:
    _install_requires = [line.rstrip('\n') for line in f]


setup(
      name = 'SPARQLWrapper',
      version = version,
      description = 'SPARQL Endpoint interface to Python',
      long_description = 'This is a wrapper around a SPARQL service. It helps in creating the query URI and, possibly, convert the result into a more manageable format.',
      license = 'W3C SOFTWARE NOTICE AND LICENSE',
      author = authors,
      url = url,
      download_url = 'https://github.com/RDFLib/sparqlwrapper/releases',
      platforms = ['any'],
      packages = ['SPARQLWrapper'],
      install_requires = _install_requires,
      extras_require = {
        'keepalive': ['keepalive>=0.5'],
      },
      classifiers =  [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: W3C License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords = ['python', 'sparql', 'rdf', 'rdflib'],
      use_2to3 = True,
      use_2to3_fixers = ['custom_fixers'],
      project_urls={
        'Home': 'https://rdflib.github.io/sparqlwrapper/',
        'Documentation': 'https://sparqlwrapper.readthedocs.io',
        'Source': 'https://github.com/RDFLib/sparqlwrapper',
        'Tracker': 'https://github.com/RDFLib/sparqlwrapper/issues',
	  }
)
