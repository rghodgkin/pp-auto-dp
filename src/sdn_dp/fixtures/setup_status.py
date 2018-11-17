#!/usr/bin/env python
# encoding: utf-8

import logging
import pytest
import pdb


@pytest.fixture(scope='function', autouse=True)
def setup_status_check(dp_setup):
    """
    Automatically call prior to each testcase to check the value
    of dp_setup.setup_status and skip testcase if zero
    """

    if dp_setup.setup_status == 0:
        pytest.skip("Skipping testcase because setup \
                     did not complete properly")


