import pytest
import pdb
import logging

# The configuration below will get executed for all testcases within the
#  'testcases/' folder
class dp_setup_obj(object):
    setup_status = 0 

@pytest.fixture(scope="session", autouse="True")
def dp_setup(common):
    dss = dp_setup_obj()

    try:
        print("Setting up for testcaes")
        # Do work
        dss.setup_status = 1

    except:
        logging.error("conftest:dp_setup: Test bring-up failed for \
                       dataplane testcase execution")
        dss.setup_status = 0

    return dss



