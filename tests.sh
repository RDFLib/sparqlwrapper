#!/bin/bash

# Please, install the required tools previously:
# $ sudo apt-get install python3-nose

if hash nosetests3 2>/dev/null; then
    nosetests3 -v
else
    nosetests -v
fi

