#!/usr/bin/env python
# encoding: utf-8

import logging
import pdb
import sdn_dp.conf.common.utils as utils
import sdn_dp.conf.common.sdn_class as sdn_class
from sdn_dp.conf.common.constants import TopoTemps
from sdn_dp.conf.common.constants import SDNVLAN
from sdn_dp.conf.common.constants import SDNCIDR
from sdn_dp.conf.common.constants import OSBRIDGEMAPPING


def gen_sdn_topo(tv, common):
  
    try:
      aws_vlan = SDNVLAN.AWS_VLAN_START
      google_vlan = SDNVLAN.GOOGLE_VLAN_START
      tenant_ip_start = SDNCIDR.OS_TENANT_IP_START
      tenant_prefix = SDNCIDR.OS_TENANT_PREFIX
      aws_ip_start = SDNCIDR.AWS_PROVIDER_IP_START
      aws_prefix = SDNCIDR.AWS_PROVIDER_PREFIX
      goog_ip_start = SDNCIDR.GOOGLE_PROVIDER_IP_START
      goog_prefix = SDNCIDR.GOOGLE_PROVIDER_PREFIX

      tenant_sub_list = utils.return_ip_subnets(tenant_ip_start, tenant_prefix, \
                        skip_zero=True)
      aws_sub_list = utils.return_ip_subnets(aws_ip_start, aws_prefix, \
                     skip_zero=True)
      goog_sub_list = utils.return_ip_subnets(goog_ip_start, goog_prefix, \
                      skip_zero=True)

      # Configure SDN related data
      sdn_name = tv['sdn']['name']
      sdn = {'name':sdn_name, 'network':[] } 
  
      # Configure Network related data
      net_count = tv['sdn']['network']['count']
      net_cntr = 1
      for net_item in range(0,net_count):

          net_kl = TopoTemps.network.copy()
          net_kl['name'] = "%s-%s" % (sdn_name, net_cntr)
          net_kl['tenant_net_name'] = "%s-network-%s" % (sdn_name, net_cntr) 
          net_kl['tenant_cidr'] = str(tenant_sub_list.pop())
          net_kl['edge_list'] = [] 
  
          edge_list = tv['sdn']['network']['edge_list']
          edge_cntr = 1
          for edge_item in edge_list:

            if edge_item['type'] == "netrouter":
              edge_count = edge_item['count']
              edge_engine = edge_item['engine']
              edge_inst_cntr = 1
              for e_item in edge_item['engine']:
                for n_item in range(0,edge_count):
                  edge_kl = TopoTemps.netrouter.copy()
                  edge_kl['name'] = "%s-netrtr-%s-%s" % (sdn_name, net_cntr, edge_inst_cntr)
                  edge_kl['engine'] = e_item 
                  edge_kl['tenant_ip'] = ""
  
                  # Add edge_kl to net_kl['edge_list']
                  net_kl['edge_list'].append(edge_kl)
                  edge_inst_cntr += 1

            elif edge_item['type'] == "cloud":
              edge_count = edge_item['count']
              edge_engine = edge_item['engine'] 
              edge_inst_cntr = 1
              for e_item in edge_item['engine']: 
                for c_item in range(0,edge_count):
                  edge_kl = TopoTemps.cloud.copy()
                  edge_kl['name'] = "%s-Cloud-%s-%s" % (sdn_name, net_cntr, edge_inst_cntr)
                  edge_kl['engine'] = e_item
                  edge_kl['cloud_provider'] = edge_item['cloud_provider']
                  edge_kl['physical_net'] =  OSBRIDGEMAPPING.OS_PHYSICAL_NET
                  if edge_item['cloud_provider'].lower() == 'aws':
                      edge_kl['segment_id'] = aws_vlan
                      edge_kl['provider_net'] = str(aws_sub_list.pop())
                      aws_vlan += 1
                  elif edge_item['cloud_provider'].lower() == 'google':
                      edge_kl['segment_id'] = google_vlan
                      edge_kl['provider_net'] = str(goog_sub_list.pop())
                      google_vlan += 1 
                  edge_kl['tenant_ip'] = ""
                  edge_kl['provider_ip'] =  utils.return_ip_subnets(edge_kl['provider_net'], \
                          32, skip_zero=True).pop() 
    
                  # Add edge_kl to net_kl['edge_list']
                  net_kl['edge_list'].append(edge_kl)
                  edge_inst_cntr += 1
                    
            elif edge_item['type'] == "site":
              edge_count = edge_item['count']
              edge_engine = edge_item['engine']
              edge_inst_cntr = 1
              for e_item in edge_item['engine']:
                for n_item in range(0,edge_count):
                  edge_kl = TopoTemps.site.copy()
                  edge_kl['name'] = "%s-site-%s-%s" % (sdn_name, net_cntr, edge_inst_cntr)
                  edge_kl['engine'] = e_item
                  edge_kl['vpn_net'] = ""

                  # Add edge_kl to net_kl['edge_list']
                  net_kl['edge_list'].append(edge_kl)
                  edge_inst_cntr += 1 

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

    
