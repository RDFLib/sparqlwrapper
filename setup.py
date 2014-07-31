# -*- coding: utf-8 -*-

try:
    from ez_setup import use_setuptools
    use_setuptools()
except:
    pass

from setuptools import setup, find_packages
import sys

_requires = []
_install_requires = []

# rdflib
_requires.append('rdflib')
_install_requires.append('rdflib >= 2.4.2')

# simplejson
if sys.version_info[0:2] < (2, 6):
    _requires.append('simplejson')
    _install_requires.append('simplejson == 2.0.9')

import SPARQLWrapper

setup(
      name = 'SPARQLWrapper',
      version = SPARQLWrapper.__version__,
      description = 'SPARQL Endpoint interface to Python',
      long_description = 'This is a wrapper around a SPARQL service. It helps in creating the query URI and, possibly, convert the result into a more manageable format.',
      license = 'W3C SOFTWARE NOTICE AND LICENSE', # should be removed by PEP 314
      author = SPARQLWrapper__authors__,
      author_email = "ivan at ivan-herman net, sergio at wikier org, carlos.tejo at gmail com, indeyets at gmail com",
      url = SPARQLWrapper.__url__,
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
