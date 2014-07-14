#!/bin/sh

python3 setup.py build

if [ -d build/py3_testing ]; then
    rm -r build/py3_testing
    echo "removed build/py3_testing directory from previous run"
fi

mkdir build/py3_testing
cp -r test build/py3_testing/
cp -r build/lib/SPARQLWrapper build/py3_testing/

cd build/py3_testing

2to3 -wn --no-diffs test

nosetests3

cd ../..

