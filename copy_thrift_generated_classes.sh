#!/bin/bash

# You probably don't need to run this script.
#
# This script copies over the Thrift-generated Python classes from the
# Concrete repository to this repository.
#
# The Concrete repository contains the .thrift definition files, but not
# the Python classes generated by the Thrift compiler.  This repository
# contains the Thrift-generated Python classes, but not the .thrift
# definition files.
#
# This script should be run whenever the .thrift definition files in the
# Concrete repository are changed.


# Path to Concrete repo that contains the Python classes generated by
# the Thrift compiler
CONCRETE_PATH="${HOME}/concrete"

cp -a ${CONCRETE_PATH}/python/concrete/* concrete/
