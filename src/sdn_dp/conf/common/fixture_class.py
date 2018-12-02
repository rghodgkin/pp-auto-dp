#!/usr/bin/env python
# encoding: utf-8

import logging
import yaml
import pdb
import pytest
import sdn_dp.conf.common.sdn_class as sdn_class 
import sdn_dp.conf.common.sdn_utils as sdn_utils 
import sdn_dp.conf.common.utils as utils 
import sdn_dp.conf.os.os_utils as os_utils

class COMMON(object):
    def __init__(self, config_file, topo_file):
        self.config_file = config_file
        self.topo_file = topo_file
        self.topo = {}
        self.topo_virgin = {}
        self.config = {} 
        self.sdn = []
        self.os = {} 
        # Populates the self.config with config info
        self.gen_config_dict()
        # Expands topo for all counts and assigns IP's/vlans for
        #  all tenant and provider nets
        self.gen_topo_dict()
        # Generates the SDN objects for overall 'networks' and 
        #  all edge devices: netrouter, cloud, site, mobile
        #  Note: topo data gets copied directly into sdn.topo dict
        self.gen_sdn_data() 
        # Generates the OpenStack infrastructure needed: images,
        #  flavors, networks
        # Note: as creates nets it backfills ID's into SDN gateway
        #  objects
        self.gen_os_infra() 

    def gen_topo_dict(self):
        '''
        This method will grab info from self.config_file, parse it
         and generate a keyed list format of config data.  Keyed-list
         data will later be passed for 'network' and 'edge' object create
         as input into create_net_object and then create_edge_object class
         objects
        '''
        
        output = utils.import_yaml_to_dict(self.topo_file) 
        if output[0]:
            self.topo_virgin = output[1]
        else:
            pytest.exit(msg="Error: gen_topo_dict YAML parse of topo \
                        did not complete successfully exiting")

        output = sdn_utils.gen_sdn_topo(self.topo_virgin, self)
        if output[0]:
            self.topo = output[1]
        else:
            pytest.exit(msg="Error: gen_topo_dict generation of full \
                             SDN topo failed exiting")

    def gen_config_dict(self):
        '''
        This method will simply grab yaml data from config 
        file and put into self.config dict
        '''
        output = utils.import_yaml_to_dict(self.config_file)
        if output[0]:
            self.config = output[1]
        else:
            pytest.exit(msg="Error: gen_config_dict did not complete successfully \
                           exiting")

    def gen_sdn_data(self):
        '''
        This method will parse config dict and instantiate all network
          objects along with sub edge objects inside (via method calls)
        '''

        try:
          topo_net_list = self.topo['network']
          for net_item in topo_net_list:
              x = sdn_class.SdnNetObj(net_item, self)
              self.sdn.append(x)

        except:
          logging.error("Error: gen_sdn_data method did not complete properly")

        #output = sdn_utils.gen_sdn_net_data(self.topo, self)
        #if output[0]:
        #    self.sdn = output[1]
        #else:
        #    pytest.exit(msg="Error: gen_sdn_data generation failed - exiting")
 
    def gen_os_infra(self):
        '''
        This method will create all OpenStack tokens and references needed
          under self.os
        '''

        output = os_utils.return_keystone_sess(self.config['sdn']['os'])
        if output[0]:
            self.os['sess'] = output[1]
        else:
            pytest.exit(msg="Error: Failed to get OpenStack session key")
 
        output = os_utils.gen_os_clients(self)
        if output[0]:
            self.os['clients'] = output[1]
        else:
            pytest.exit(msg="Error: Failed to provision OpenStack clients")

        output = os_utils.config_os_pre(self)
        if output[0]:
            logging.info("Preconfigure of OpenStack infra successful")
        else:
            pytest.exit(msg="Error: Failed to complete Pre-setup in Openstack")

        output = os_utils.config_os_tenant_networks(self)
        if output[0]:
            logging.info("Configure of OpenStack tenant networks successful")
        else:
            pytest.exit(msg="Error: Failed to configure Openstack tenant networks")

        output = os_utils.config_os_provider_networks(self)
        if output[0]:
            logging.info("Configure of OpenStack provider networks successful")
        else:
            pytest.exit(msg="Error: Failed to configure Openstack provider networks")










         
 
