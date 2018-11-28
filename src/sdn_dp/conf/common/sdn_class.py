#!/usr/bin/env python
# encoding: utf-8

import logging
import subprocess
import yaml
import time
import pdb
import sdn_dp.conf.common.utils as utils
import sdn_dp.conf.common.ansible_utils as ansible_utils
from sdn_dp.conf.common.constants import OSCLOUDIMAGE
from sdn_dp.conf.common.constants import OSCLOUDFLAVOR

class SdnNetObj(object):
    def __init__(self, topo_dict, common):
        self.topo = topo_dict
        self.common = common
        self.tenant_cidr = self.topo['tenant_cidr']
        self.tenant_net_name = self.topo['tenant_net_name']
        self.tenant_net_obj = ""
        self.tenant_net_subnet_obj = ""
        self.edge_list = []
        self.edge_netrouter_list = []
        self.edge_cloud_list = []
        self.edge_site_list = []
        self.edge_mobile_list = []
        self.gen_edge_data()

    def gen_edge_data(self):
        '''
        This method is going to parse the self.topo['edge_list'] and create
         all edge objects, passing in edge specific dict info
        '''
        logging.info("Inside gen_edge_data") 
        logging.info("Topo data is: %s" % self.topo)

        for edge_item in self.topo['edge_list']:
            self.create_edge_inst(edge_item['type'], edge_item)

    def create_edge_inst(self, type, topo_dict):
        print("I'm inside create_edge_inst: %s, %s" % (type, topo_dict['name']))

        if type == "netrouter":
            tmp_obj = SdnNetrouterCloudObj(topo_dict, self.common)
            self.edge_netrouter_list.append(tmp_obj)
            self.edge_list.append(tmp_obj)

        elif type == "cloud":
            tmp_obj = SdnEdgeCloudObj(topo_dict, self.common)
            self.edge_cloud_list.append(tmp_obj) 
            self.edge_list.append(tmp_obj)

        elif type == "site":
            tmp_obj = SdnEdgeSiteCloudObj(topo_dict, self.common)
            self.edge_site_list.append(tmp_obj) 
            self.edge_list.append(tmp_obj)

        elif type == "mobile":
            tmp_obj = SdnEdgeMobileCloudObj(topo_dict, self.common)
            self.edge_mobile_list.append(tmp_obj)
            self.edge_list.append(tmp_obj)

    def list_edge_inst(self):
        '''
        This function will list all the 'edge' instances from
        the various *_cloud_list arrays 
        ''' 
        return self.edge_list 
        

class SdnEdgeParent(object):
    def __init__(self, topo_dict, common):
        self.topo = topo_dict.copy()
        self.name = self.topo['name']
        self.common = common
        self.os = {'networks':{'tenant':{'net_obj':'', 'subnet_obj':'', \
                   'port_name':'', 'port_obj':''}}, 
                   'server':{'server_obj':''}}
        self.deploy_state = 0
        self.traffic_state = 0

    def destroy(self):
        server = self.os['server']['server_obj'] 
        logging.info("destroy: deleting server %s" % self.name)
        server.delete()

        self.deploy_state = 0


class SdnNetrouterCloudObj(SdnEdgeParent):
    def __init__(self, topo_dict, common):
        SdnEdgeParent.__init__(self, topo_dict, common)

    def deploy(self):
        if self.deploy_state == 0:
            nova = self.common.os['clients']['nova']['client']

            image = nova.glance.find_image('%s' % OSCLOUDIMAGE.netrouter)
            flavor_name = OSCLOUDFLAVOR.netrouter
            flavor = nova.flavors.find(name=flavor_name)
            net_tenant = self.os['networks']['tenant']['net_obj']['network']['id']
            nics = [{'net-id': net_tenant, 'name': 'tenant-port'}]
            instance = nova.servers.create(name=self.name, image=image, \
                                               flavor=flavor, nics=nics, \
                                               availability_zone=self.topo['engine'])
            self.os['server']['server_obj'] = instance

            for loop in range(10):
                time.sleep(2)
                print("Loop cntr =: %s" % loop)
                instance_net_info = instance.interface_list()
                if len(instance_net_info) == 2:
                    break
            self.topo['tenant_ip'] = instance_net_info[0].fixed_ips[0]['ip_address']
            self.topo['tenant_mac'] = instance_net_info[0].mac_addr

            self.deploy_state = 1

            return 1


        else:
            logging.info("SdnNetrouterCloudObj: deploy of %s failed b/c \
                          already in deployed state" % selfname)
            return 0


class SdnEdgeCloudObj(SdnEdgeParent):
    def __init__(self, topo_dict, common):
        SdnEdgeParent.__init__(self, topo_dict, common)
        # Initialize cloud specific Openstack dict keys
        self.os['networks']['provider'] = {'net_obj':'', 'port_obj':''}

    def deploy(self):
        if self.deploy_state == 0:
            
            nova = self.common.os['clients']['nova']['client']

            image = nova.glance.find_image('%s' % OSCLOUDIMAGE.cloud)
            flavor_name = OSCLOUDFLAVOR.netrouter
            flavor = nova.flavors.find(name=flavor_name)
            net_tenant = self.os['networks']['tenant']['net_obj']['network']['id']
            net_provider = self.os['networks']['provider']['net_obj']['network']['id']
            nics = [{'net-id': net_tenant, 'name': '%s-tenant-port' % self.name},
                    {'net-id': net_provider, 'name': '%s-provider-port' % self.name}]
            
            instance = nova.servers.create(name=self.name, image=image, \
                                           flavor=flavor, nics=nics, \
                                           availability_zone=self.topo['engine'])

            self.os['server']['server_obj'] = instance
            for loop in range(10):
                time.sleep(2)
                print("Loop cntr =: %s" % loop)
                instance_net_info = instance.interface_list()
                if len(instance_net_info) == 2:
                    break
            self.topo['tenant_ip'] = instance_net_info[0].fixed_ips[0]['ip_address']
            self.topo['tenant_mac'] = instance_net_info[0].mac_addr
            self.topo['provider_ip'] = instance_net_info[1].fixed_ips[0]['ip_address']
            self.topo['provider_mac'] = instance_net_info[1].mac_addr

            self.deploy_state = 1
   
            return 1

        else:
            logging.info("SdnNetrouterCloudObj: deploy of %s failed b/c \
                          already in deployed state" % selfname)
            return 0 

    def traffic_start(self, dest_name, **kwargs):
        if self.traffic_state == 0:
        # If traffic_state = 0 then we need to configure the subinterface
        #   and routes on each gateway device for reachability
          if self.topo['traffic_mode'] == "external":
            # The below will configure traffic requirements for all
            #  gateways in same network as this device - thus traffic
            #  can be sent anywhere
            ansible_utils.ansible_traffic_subint(self)

            # Configure routes on local customer traffic device to reach
            #   gateway; on all remote devices insert return route
            #my_name = self.name
            #net_match = re.search('cloud-([0-9]+)-', my_name)
            #my_net_index = net_match.group(1)
            #remote_net_list = []
            #local_net = self.topo['provider_net']
            #for gw in common.sdn[my_net_index].edge_list:
            #  if gw.name != my_name: 
            #    if gw.topo['type'] == 'cloud':
            #      remote_net_list.append(gw.topo['provider_net']) 
            #      remote_traffic_ip = gw.topo['traffic_engine_ip']
            #      remote_traffic_gw = gw.topo['provider_ip']
            #      # Add route to remote traffic gen for return traffic
            #      ssh_cmd = "route add %s gw %s" % \
            #                 (self.topo['provider_net'], remote_traffic_gw) 
            #      utils.ssh_exec(remote_traffic_ip, ssh_cmd)
            #    elif gw.topo['type'] == 'site':
            #      pass
            #    elif gw.topo['type'] == 'mobile':
            #      pass
            # Add local routes to all remote provider networks
            #for net in remote_net_list:
            #    ssh_cmd = "route add %s gw %s" % \
            #               (net, self.topo['provider_ip'])
            #    utils.ssh_exec(self.topo['traffic_engine_ip'], ssh_cmd)
            ansible_utils.ansible_traffic_routes(self)

        # Start background iperf3 instance 


class SdnEdgeSiteCloudObj(SdnEdgeParent):
    def __init__(self, topo_dict, common):
        SdnEdgeParent.__init__(self, topo_dict, common) 

    def deploy(self):
        pass


class SdnEdgeMobileCloudObj(SdnEdgeParent):
    def __init__(self, topo_dict, common):
        SdnEdgeParent.__init__(self, topo_dict, common)

    def deploy(self):
        pass


        

