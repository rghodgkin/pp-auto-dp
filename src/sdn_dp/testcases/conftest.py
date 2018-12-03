import pytest
import pdb
import logging
import time
import re
import sdn_dp.conf.common.ansible_utils as ansible_utils
import sdn_dp.conf.common.utils as utils
from sdn_dp.conf.common.constants import TRAFFICINFO
from sdn_dp.conf.common.constants import OSCLOUDIMAGE
from sdn_dp.conf.common.constants import OSCLOUDFLAVOR

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

        logging.info("Sleeping 10 seconds after deploy to let all containers \
                      get to active state")
        time.sleep(10)


        # TEMPORARY
        # The below is used to configure OSPF within coud network
        #  until we get true BGP support in place
        for net in common.sdn:
            for nrtr in net.edge_netrouter_list:
                ansbile_utils.ansible_deploy_lxd_ospf(common, nrtr) 
            for cgw in net.edge_cloud_list:
                ansible_utils.ansible_deploy_lxd_ospf(common, cgw) 
            for sgw in net.edge_site_list:
                ansible_utils.ansible_deploy_lxd_ospf(common, sgw) 
            for mgw in net.edge_mobile_list:
                ansible_utils.ansible_deploy_lxd_ospf(common, mgw) 


        # The below configures traffic info within common.sdn cloud
        #  objects.  Configures IP addresses and routes as per confi
        traffic_mode = common.topo['other']['traffic'].lower()
        logging.info("Setting up edge traffic, mode is: %s" %
                      common.topo['other']['traffic'])
        if traffic_mode == 'os':
          # Here we will spawn an OS 'provider' instance for each
          #  cloud and site gateway
          traffic_kl = common.config['devices']['traffic']
          nova = common.os['clients']['nova']['client']
          image = nova.glance.find_image('%s' % OSCLOUDIMAGE.traffic)
          flavor_name = OSCLOUDFLAVOR.traffic
          flavor = nova.flavors.find(name=flavor_name)
          for net in common.sdn:
              for edge_item in net.edge_cloud_list:
                pdb.set_trace()
                c_type = edge_item.topo['type']
                c_name = '%s-traffic' % edge_item.topo['name']

                if c_type == 'cloud':
                  c_prov = edge_item.topo['cloud_provider']
                  net_provider = edge_item.os['networks']['provider']['net_obj']['network']['id']
                  nics = [{'net-id': net_provider, 'name': '%s-traffic-port' % edge_item.name}] 
                  edge_item.topo['traffic_mode'] = \
                            traffic_mode
                  edge_item.topo['traffic_engine'] = \
                            traffic_kl[c_prov]['engine']
                  edge_item.topo['traffic_engine_ip'] = \
                            traffic_kl[c_prov]['engine_ip']
                  edge_item.topo['traffic_name'] = c_name
  
                elif c_type == 'site':
                  pass
               
                for respawn in range(5):
                    instance = nova.servers.create(name=c_name, image=image, \
                                           flavor=flavor, nics=nics, \
                                           availability_zone=edge_item.topo['engine'])
                    time.sleep(3)
                    dir(instance)
                    if instance._info['OS-EXT-SRV-ATTR:instance_name'] != '':
                        break
                    else:
                        instance.delete()
                        time.sleep(5)

                edge_item.os['server']['traffic_obj'] = instance
                edge_item.topo['traffic_instance_name'] = instance._info['OS-EXT-SRV-ATTR:instance_name']
                instance_net_info = instance.interface_list()
                edge_item.topo['traffic_engine_int_ip'] =  instance_net_info[0].fixed_ips[0]['ip_address']
                edge_item.topo['traffic_engine_int_mac'] = instance_net_info[0].mac_addr

                # Configure OSPF on LXD traffic instance
                ansible_utils.ansible_deploy_lxd_traffic_ospf(common, edge_item)
                
  
        else:
          # Default traffic mode will be 'external' if not
          #   specified otherwise.  The below populates the necessary
          #   'traffic_*' items in topo to configure traffic as
          #   needed by 'edge_item.traffic_start()' method
          traffic_kl = common.config['devices']['traffic']
          for net in common.sdn:
              for edge_item in net.edge_cloud_list:
                c_type = edge_item.topo['type']
                host_ip_list = utils.return_ip_subnets(edge_item.topo['provider_net'], 32, skip_zero=True)
                regex_match = re.search("([0-9.]+)/[0-9]+", host_ip_list[255 - int(TRAFFICINFO.EXTERNAL_IP)])
                traf_gen_ip = '%s/%s' % (regex_match.group(1), str(TRAFFICINFO.EXTERNAL_IP_MASK))
                if c_type == 'cloud':
                  c_prov = edge_item.topo['cloud_provider']
                  edge_item.topo['traffic_mode'] = \
                            traffic_mode
                  edge_item.topo['traffic_engine'] = \
                            traffic_kl[c_prov]['engine']
                  edge_item.topo['traffic_engine_ip'] = \
                            traffic_kl[c_prov]['engine_ip']
                  edge_item.topo['traffic_engine_int'] = \
                            traffic_kl[c_prov]['engine_int']
                  edge_item.topo['traffic_engine_int_ip'] = \
                            traf_gen_ip 
  
                elif c_type == 'site':
                  edge_item.topo.traffic_mode = \
                            traffic_mode
  
                elif c_type == 'mobile':
                  edge_item.topo.traffic_mode = \
                            traffic_mode

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






