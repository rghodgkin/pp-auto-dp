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
        for net in common.sdn:
            cgw1 = net.edge_cloud_list[0]
            cgw2 = net.edge_cloud_list[1]
            cgw1.traffic_start(cgw2.name)
        assert 1




