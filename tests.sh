#!/bin/bash

PYTHON_VERSION=`python -c "import platform; print(int(platform.python_version()[:1]))"`
VERSION_THRESHOLD=3

echo "running tests on python $PYTHON_VERSION.x..."

if [[ ${PYTHON_VERSION} -ge ${VERSION_THRESHOLD} ]]; then
	bash ./run_tests_py3.sh
else
	nosetests
fi