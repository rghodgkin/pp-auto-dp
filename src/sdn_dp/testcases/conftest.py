import pytest
import pdb
import logging
import sdn_dp.conf.common.sdn_utils as sdn_utils

# The configuration below will get executed for all testcases within the
#  'testcases/' folder
class dp_setup_obj(object):
    setup_status = 0 

# The following function will cleanup all OS resources that begin with
#  
#def dp_cleanup_proc(common):
#    # Match against all resources in OS with prefix of 'common.topo['name']'
#    #  example matching 'AUTO'
#    nova = common.os['clients']['nova']['client']
#    neutron = common.os['clients']['neutron']['client']
#   
#    pdb.set_trace()
#    server_list = nova.servers.list()
#    for server in server_list:
#        if server.name.rfind(common.topo['name']) != "-1":
#            logging.info("dp_cleanup: deleting server %s" % server.name)
#            #server.delete()
#
#    net_list = neutron.list_networks()['networks']
#    for net in net_list:
#        if net['name'].rfind(common.topo['name']) != "-1":
#            logging.info("dp_cleanup: deleting network %s" % net['name'])
#            #neutron.delete_network(net['id'])


@pytest.fixture(scope="session", autouse="True")
def dp_setup(common):
    dss = dp_setup_obj()

    try:
        logging.info("testcases/conftest: Executing setup for sdn_dp \
                      testcases")
        
        for net in common.sdn:
            for nrtr in net.edge_netrouter_list:
                nrtr.deploy()
            for cgw in net.edge_cloud_list:
                cgw.deploy()
            for sgw in net.edge_site_list:
                sgw.deploy()
            for mgw in net.edge_mobile_list:
                mgw.deploy()

        # TEMPORARY
        # The below is used to configure OSPF within coud network
        #  until we get true BGP support in place
        for net in common.sdn:
            for nrtr in net.edge_netrouter_list:
                sdn_utils.ansible_deploy_lxd_ospf(common, nrtr) 
            for cgw in net.edge_cloud_list:
                sdn_utils.ansible_deploy_lxd_ospf(common, cgw) 
            for sgw in net.edge_site_list:
                sdn_utils.ansible_deploy_lxd_ospf(common, sgw) 
            for mgw in net.edge_mobile_list:
                sdn_utils.ansible_deploy_lxd_ospf(common, mgw) 

        dss.setup_status = 1

    except:
        logging.error("conftest:dp_setup: Test bring-up failed for \
                       dataplane testcase execution")
        dss.setup_status = 0

    return dss

#@pytest.fixture(scope="session", autouse="True")
#def dp_cleanup(request, common):
#    print("IM INSIDE CLEANUP") 
#
#    def dp_cleanup_proc(common):
#        # Match against all resources in OS with prefix of 'common.topo['name']'
#        #  example matching 'AUTO'
#        nova = common.os['clients']['nova']['client']
#        neutron = common.os['clients']['neutron']['client']
#    
#        pdb.set_trace()
#        server_list = nova.servers.list()
#        for server in server_list:
#            if server.name.rfind(common.topo['name']) != "-1":
#                logging.info("dp_cleanup: deleting server %s" % server.name)
#                #server.delete()
#    
#        net_list = neutron.list_networks()['networks']
#        for net in net_list:
#            if net['name'].rfind(common.topo['name']) != "-1":
#                logging.info("dp_cleanup: deleting network %s" % net['name'])
#                #neutron.delete_network(net['id'])
#
#    request.addfinalizer(dp_cleanup_proc(common))






