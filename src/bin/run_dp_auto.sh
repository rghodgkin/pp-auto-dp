#!/bin/sh

CWD=$(cd $(dirname $0); pwd)

RUN_CONFIG=$(echo $1 | tr [:upper:] [:lower:])
RUN_TOPO=$(echo $2 | tr [:upper:] [:lower:])

if [ -z "$RUN_CONFIG" ]; then
    echo "Test configuration file must be specified"
    exit 1
fi

if [ -z "$RUN_TOPO" ]; then
    echo "Test topology file must be specified"
    RUN_MODE='test'
fi

SDN_LOG_FILE=sdn-pytest-log.log
SDN_LOG_DIR=$HOME/sdn-auto

py.test -s -v \
        --configfile=$RUN_CONFIG \
        --topo=$RUN_TOPO \
        --logfile=$SDN_LOG_DIR/$SDN_LOG_FILE \
        ./sdn_dp/testcases

