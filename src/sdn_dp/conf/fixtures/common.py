#!/usr/bin/env python
# encoding: utf-8

import pytest
import pdb
from sdn_dp.conf.common.fixture_class import COMMON

@pytest.fixture(scope="session", autouse=True)
def common(request):
    '''
    Returns global master object that holds all config and run-time
     dict data 
    '''
    config_file = request.config.getoption("--configfile")
    topo_file = request.config.getoption("--topo")
    return COMMON(config_file, topo_file)
