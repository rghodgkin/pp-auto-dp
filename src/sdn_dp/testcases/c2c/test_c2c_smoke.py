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
        pdb.set_trace()
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

    def test_c2c_dp_ping(self, common):
        logging.info("inside testcase: test_c2c_dp_ping")
        assert 1




