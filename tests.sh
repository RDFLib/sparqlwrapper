#!/bin/bash

PYTHON_VERSION=`python -c "import sys;t='{v[0]}.{v[1]}'.format(v=list(sys.version_info[:2]));sys.stdout.write(t)";`

echo "running tests on python $PYTHON_VERSION.x..."

if  [[ $PYTHON_VERSION == 3.* ]] ;
then
    . run_tests_py3.sh
else
    nosetests-$PYTHON_VERSION
fi

