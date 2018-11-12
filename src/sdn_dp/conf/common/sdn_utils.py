#!/usr/bin/env python
# encoding: utf-8

import logging
import pdb
import sdn_dp.conf.common.utils as utils
import sdn_dp.conf.common.sdn_class as sdn_class
from sdn_dp.conf.common.constants import TopoTemps
from sdn_dp.conf.common.constants import SDNVLAN
from sdn_dp.conf.common.constants import SDNCIDR


def gen_sdn_topo(tv, common):
  
    try: 
      aws_vlan_start = SDNVLAN.AWS_VLAN_START
      goog_vlan_start = SDNVLAN.GOOGLE_VLAN_START
      tenant_cidr_start = SDNVLAN.OS_TENANT_CIDR_START
      aws_cidr_start = SDNVLAN.AWS_PROVIDER_CIDR_START
      goog_cidr_start = SDNVLAN.GOOGLE_PROVIDER_CIDR_START

      # Configure SDN related data
      sdn_name = tv['sdn']['name']
  
      # Configure Network related data
      net_count = tv['sdn']['network']['count']
      net_cntr = 1
      for net_item in range(0,net_count):
          # Generate subnet list from inside supernet
          vpc_ipv4_sub_list = utils.return_ip_subnets(vpc_ip_str, vpc_sub_prefix, \
                              skip_zero=True)
          net_kl = TopoTemps.network
          net_kl['name'] = "%s-Network%s" % (sdn_name, net_cntr)
          net_kl['sdn_description'] = "Network Controller %s" % net_kl['name']
          net_kl['sdn_account'] = tv['sdn']['network']['sdn_account'] 
          net_kl['sdn_network_type'] = tv['sdn']['network']['sdn_network_type']
          net_aws_zone = tv['sdn']['network']['sdn_zone']
          net_kl['sdn_zone'] = SDNNetTrans.aws[net_aws_zone]
  
          edge_list = tv['sdn']['network']['edge_list']
          edge_cntr = 1
          for edge_item in edge_list:
            if edge_item['type'] == "cloud":
              edge_count = edge_item['count']
              edge_inst_cntr = 1
              for c_item in range(0,edge_count):
                edge_kl = TopoTemps.cloud.copy()
                edge_kl['name'] = "%s-Cloud-%s-%s" % (net_kl['name'], edge_cntr, edge_inst_cntr)
                edge_kl['sdn_description'] = "Cloud Gateway %s" % \
                                          edge_kl['name'] 
                edge_kl['sdn_network'] = net_kl['name']
                edge_kl['sdn_cloud_provider'] = edge_item['cloud_provider'] 
                edge_kl['aws_cloud_region'] = edge_item['region']
                edge_kl['sdn_cloud_location'] = SDNCloudTrans.aws[edge_item['region']]
                edge_kl['aws_cloud_account'] = common.config['aws']['account_number']
                edge_kl['IPv4_CIDR_block'] = vpc_ipv4_sub_list.pop()
  
                # Add edge_kl to net_kl['edge_list']
                net_kl['edge_list'].append(edge_kl)
                edge_inst_cntr += 1
                    
            elif edge_item['type'] == "site":
              pass
  
            elif edge_item['type'] == "mobile":
              pass
  
            edge_cntr += 1 
         
          # Add net_kl to sdn['network']
          sdn['network'].append(net_kl)
          net_cntr += 1

      return 1, sdn 

    except:
      logging.error("Error: gen_sdn_topo method did not execute cleanly")
          
      return 0, {} 
  
def gen_sdn_data(topo, common):
    """
    This function returns a list of 'network' objects that ultimately populates 
    'common.sdn[]' list with network objects
    """
    try:
        ret_net_list = []
        topo_net_list = topo['network']
        for net_item in topo_net_list:
            x = sdn_class.SdnNetObj(net_item, common)
            x.gen_edge_data()
            ret_net_list.append(x) 
    
        return 1, ret_net_list

    except: 
        logging.error("Error: gen_sdn_data method did not complete properly")

        return 0, {}

    
