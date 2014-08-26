# -*- coding: utf-8 -*-

import sys

try:
    from ez_setup import use_setuptools
    use_setuptools()
except:
    pass

from setuptools import setup, find_packages

try:
    import six
    py3 = six.PY3
except:
    py3 = sys.version_info[0] >= 3    

# grouping requires
_requires = []
_install_requires = []

# rdflib
_requires.append('rdflib')
_install_requires.append('rdflib >= 2.4.2')

# simplejson
if sys.version_info[0:2] < (2, 6):
    _requires.append('simplejson')
    _install_requires.append('simplejson == 2.0.9')

# metainformation
if py3:
    import re
    _version_re = re.compile(r'__version__\s*=\s*"(.*)"')
    _authors_re = re.compile(r'__authors__\s*=\s*"(.*)"')
    _url_re = re.compile(r'__url__\s*=\s*"(.*)"')
    for line in open('SPARQLWrapper/__init__.py', encoding='utf-8'):
        version_match = _version_re.match(line)
        if version_match:
            version = version_match.group(1)
        authors_match = _authors_re.match(line)
        if authors_match:
            authors = authors_match.group(1)
        url_match = _url_re.match(line)
        if url_match:
            url = url_match.group(1)
else:
    import SPARQLWrapper
    version = SPARQLWrapper.__version__
    authors = SPARQLWrapper.__authors__
    url = SPARQLWrapper.__url__

# actual setup configuration
setup(
      name = 'SPARQLWrapper',
      version = version,
      description = 'SPARQL Endpoint interface to Python',
      long_description = 'This is a wrapper around a SPARQL service. It helps in creating the query URI and, possibly, convert the result into a more manageable format.',
      license = 'W3C SOFTWARE NOTICE AND LICENSE', # should be removed by PEP 314
      author = authors,
      author_email = "ivan at ivan-herman net, sergio at wikier org, carlos.tejo at gmail com, indeyets at gmail com",
      url = url,
      download_url = 'https://github.com/RDFLib/sparqlwrapper/releases',
      platforms = ['any'], # should be removed by PEP 314
      packages = ['SPARQLWrapper'],
      requires = _requires, # used by distutils to create metadata PKG-INFO
      install_requires = _install_requires, # used by setuptools to install the dependencies
      classifiers =  [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: W3C License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
      ],
      keywords = 'python SPARQL',
      use_2to3 = True,
      #requires_python = '>=2.5', # Future in PEP 345
      #scripts = ['ez_setup.py']
)
