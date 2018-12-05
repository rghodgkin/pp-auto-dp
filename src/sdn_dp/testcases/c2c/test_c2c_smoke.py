#!/usr/bin/env python
# encoding: utf-8

import pytest
import logging
from time import sleep
import pdb

class TestC2CSmoke:

    @classmethod
    def before_class(cls, common):
        logging.info("inside before_class")
        pass

    @classmethod
    def after_class(cls, common):
        logging.info("inside after_class")
        pass

    def before_each_func(self, common):
        logging.info("inside before_each_func")
        pass

    def after_each_func(self, common):
        logging.info("inside after_each_func")
        pass

    def test_c2c_dp_ping(self, common, dp_setup):
        logging.info("inside testcase: test_c2c_dp_ping")
        print("dp_setup setup_status is: %s" % dp_setup.setup_status)

        # Run basic traffic test from first cloud gateway
        #  in each tenant network
        result_all = 1
        for net in common.sdn:
            cgw1 = net.edge_cloud_list[0]
            cgw2 = net.edge_cloud_list[1]
            # traffic_time=x, 
            result = cgw1.traffic_run(cgw2.name, traffic_time=2)

            if result == '1':
                logging.info("Traffic passed for net %s" % net.topo['name'])
            else:
                logging.info("Traffic failed for net %s" % net.topo['name'])
                result_all = 0 

        pdb.set_trace()
        if result_all == 1:
            info.logging("Basic TCP bi-directional traffic testcase passed")
            assert 1
        else:
            info.logging("Basic TCP bi-directional traffic testcase failed")
            assert 0



