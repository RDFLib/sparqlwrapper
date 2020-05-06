#!/bin/bash

# FOR MANUAL RUNNING, IT REQUIRES modules: 2to3, python3-setuptools, python3-nose
# REMEMBER to remove PYTHON_VERSION SUFFIX
# Please, install the required tools previously:
# $ sudo apt-get install 2to3
# $ sudo apt-get install python3-setuptools
# $ sudo apt-get install python3-nose

function cmdcheck() {
    command -v $1 >/dev/null 2>&1 || { echo >&2 "ERROR: command $1 required but it's not installed; aborting..."; exit -1; }
}

cmdcheck python3

PYTHON_VERSION=`python3 -c "import sys;t='{v[0]}.{v[1]}'.format(v=list(sys.version_info[:2]));sys.stdout.write(t)";`

#cmdcheck 2to3-$PYTHON_VERSION
#cmdcheck nosetests-$PYTHON_VERSION
#cmdcheck nosetests3

python3 setup.py build

if [ -d build/py3_testing ]; then
    rm -r build/py3_testing
    echo "removed build/py3_testing directory from previous run"
fi

mkdir build/py3_testing
cp -r test build/py3_testing/
cp -r build/lib/SPARQLWrapper build/py3_testing/

cd build/py3_testing

if command -v 2to3-$PYTHON_VERSION; then
    2to3-$PYTHON_VERSION -wn --no-diffs test
else
    2to3 -wn --no-diffs test
fi

sed -i.bak s/urllib2._opener/urllib.request._opener/g test/wrapper_test.py

if hash nosetests3 2>/dev/null; then
    nosetests3 -v
else
    nosetests -v
fi

cd ../..

