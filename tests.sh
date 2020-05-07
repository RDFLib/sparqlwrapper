#!/bin/bash

# FOR MANUAL RUNNING, IT REQUIRES modules: 2to3, python3-setuptools, python3-nose
# REMEMBER to remove PYTHON_VERSION SUFFIX
# Please, install the required tools previously:
# $ sudo apt-get install 2to3
# $ sudo apt-get install python3-setuptools
# $ sudo apt-get install python3-nose

python3 setup.py build

if [ -d build/py3_testing ]; then
    rm -r build/py3_testing
    echo "removed build/py3_testing directory from previous run"
fi

mkdir build/py3_testing
cp -r test build/py3_testing/
cp -r build/lib/SPARQLWrapper build/py3_testing/

cd build/py3_testing

if hash nosetests3 2>/dev/null; then
    nosetests3 -v
else
    nosetests -v
fi

cd ../..

