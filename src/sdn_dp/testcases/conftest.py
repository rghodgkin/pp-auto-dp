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
        logging.info("testcases/conftest: Executing setup for sdn_dp \
                      testcases")
        pdb.set_trace() 
        for net in common.sdn:
            for nrtr in net.edge_netrouter_list:
                nrtr.deploy()
            for cgw in net.edge_cloud_list:
                cgw.deploy()
            for sgw in net.edge_site_list:
                sgw.deploy()
            for mgw in net.edge_mobile_list:
                mgw.deploy()
        dss.setup_status = 1

    except:
        logging.error("conftest:dp_setup: Test bring-up failed for \
                       dataplane testcase execution")
        dss.setup_status = 0

    return dss



