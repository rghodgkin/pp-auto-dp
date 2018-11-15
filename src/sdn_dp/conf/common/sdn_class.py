#!/usr/bin/env python
# encoding: utf-8

import logging
import yaml
import pdb
#import sdn_dp.conf.aws.aws_utils as aws_utils

class SdnNetObj(object):
    def __init__(self, topo_dict, common):
        self.topo = topo_dict
        self.common = common
        self.tenant_cidr = self.topo['tenant_cidr']
        self.tenant_net_name = self.topo['tenant_net_name']
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
        self.os = {'tenant_net':'', 'tenant_port_id':'', \
                'server_id':''}

class SdnNetrouterCloudObj(SdnEdgeParent):
    def __init__(self, topo_dict, common):
        SdnEdgeParent.__init__(self, topo_dict, common)

    def sdn_deploy(self):
        pass

    def sdn_destroy(self):
        pass

class SdnEdgeCloudObj(SdnEdgeParent):
    def __init__(self, topo_dict, common):
        SdnEdgeParent.__init__(self, topo_dict, common)
        # Initialize cloud specific Openstack dict keys
        self.os['provider_net_id'] = ''
        self.os['provider_port_id'] = ''

    def sdn_deploy(self):
        # Needs to do following: 1) get port from tenant net (self.os.tenant_net_id)
        #                        2) get port from provider net (self.os.provider_net_id)
        #                        3) Create server instance with ports
        pass

    def sdn_destroy(self):
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

    def sdn_deploy(self):
        pass

    def sdn_destroy(self):
        pass

class SdnEdgeMobileCloudObj(SdnEdgeParent):
    def __init__(self, topo_dict, common):
        SdnEdgeParent.__init__(self, topo_dict, common)

    def sdn_deploy(self):
        pass

    def sdn_destroy(self):
        pass

        

