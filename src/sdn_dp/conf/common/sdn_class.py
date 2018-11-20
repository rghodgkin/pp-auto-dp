#!/usr/bin/env python
# encoding: utf-8

import logging
import yaml
import time
import pdb
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

class SdnNetrouterCloudObj(SdnEdgeParent):
    def __init__(self, topo_dict, common):
        SdnEdgeParent.__init__(self, topo_dict, common)

    def deploy(self):
        if self.deploy_state == 0:
            if self.os['networks']['tenant']['port_obj'] == '':
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


        else:
            logging.info("SdnNetrouterCloudObj: deploy of %s failed b/c \
                          already in deployed state" % selfname)
            return 0

    def destroy(self):
        pass

class SdnEdgeCloudObj(SdnEdgeParent):
    def __init__(self, topo_dict, common):
        SdnEdgeParent.__init__(self, topo_dict, common)
        # Initialize cloud specific Openstack dict keys
        self.os['networks']['provider'] = {'net_obj':'', 'port_obj':''}

    def deploy(self):
        # Needs to do following: 1) get port from tenant net (self.os.tenant_net_id)
        #                        2) get port from provider net (self.os.provider_net_id)
        #                        3) Create server instance with ports
        if self.deploy_state == 0:
            
            nova = self.common.os['clients']['nova']['client']

            image = nova.glance.find_image('%s' % OSCLOUDIMAGE.cloud)
            flavor_name = OSCLOUDFLAVOR.netrouter
            flavor = nova.flavors.find(name=flavor_name)
            net_tenant = self.os['networks']['tenant']['net_obj']['network']['id']
            net_provider = self.os['networks']['provider']['net_obj']['network']['id']
            nics = [{'net-id': net_tenant, 'name': '%s-tenant-port' % self.name},
                    {'net-id': net_provider, 'name': '%s-provider-port' % self.name}]
            pdb.set_trace()
            instance = nova.servers.create(name=self.name, image=image, \
                                           flavor=flavor, nics=nics, \
                                           availability_zone=self.topo['engine'])

            self.os['server']['server_obj'] = instance
            # Pull the 'tenant' and 'provider' IP address and MAC's and store into
            #   self.topo.tenant_ip, tenant_mac, provider_ip and provider_mac
            # The below should be easiest way, but for some reason comes back empty
            #  no longer how long wait period is set for. 
            #instance_net_info = instance.addresses
            #if instance_net_info == {}:
            #    print("*********FAIL*********")
            #for loop in range(10):
            #    time.sleep(2)
            #    print("Loop cntr =: %s" % loop)
            #    instance_net_info = instance.addresses
            #    if len(instance_net_info) == 2:
            #        break
            #self.topo['tenant_ip'] = instance_net_info[self.topo\
            #                         ['tenant_net_name']][0]['addr']
            #self.topo['tenant_mac'] = instance_net_info[self.topo\
            #                         ['tenant_net_name']][0]['OS-EXT-IPS-MAC:mac_addr']
            #self.topo['provider_ip'] = instance_net_info[self.topo\
            #                         ['provider_net_name']][0]['addr']
            #self.topo['provider_mac'] = instance_net_info\
            #                         [self.topo['provider_net_name']][0]['OS-EXT-IPS-MAC:mac_addr']
            # The below is a backup method for getting addr and mac
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

    def destroy(self):
        pass

    def aws_deploy(self):
        status = aws_utils.deploy_aws_cloud(self.topo)
        if status[0] == 1:
            #self.aws_data = aws_utils.deploy_aws_cloud(self.topo)
            return 1
        else:
            logging.error("Error: Edge Cloud.aws_deploy: Failed to deploy edge \
                           cloud %s" % self.topo.name)
            return 0

    def aws_destroy(self):
        pass 

class SdnEdgeSiteCloudObj(SdnEdgeParent):
    def __init__(self, topo_dict, common):
        SdnEdgeParent.__init__(self, topo_dict, common) 

    def deploy(self):
        pass

    def destroy(self):
        pass

class SdnEdgeMobileCloudObj(SdnEdgeParent):
    def __init__(self, topo_dict, common):
        SdnEdgeParent.__init__(self, topo_dict, common)

    def deploy(self):
        pass

    def destroy(self):
        pass

        

