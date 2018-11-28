#!/usr/bin/env python
# encoding: utf-8

import logging
import pdb
import subprocess
import time
import sdn_dp.conf.common.sdn_class as sdn_class
import sdn_dp.conf.common.utils as utils
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
      sdn = {'name':sdn_name, 'network':[], 'other':tv['sdn']['other']} 
  
      # Configure Network related data
      net_count = tv['sdn']['network']['count']
      net_cntr = 1
      for net_item in range(0,net_count):
          
          net_kl = TopoTemps.network.copy()
          net_kl['name'] = "%s-%s" % (sdn_name, net_cntr)
          net_kl['tenant_net_name'] = "%s-network-%s" % (sdn_name, net_cntr) 
          tenant_cidr = str(tenant_sub_list.pop())
          net_kl['tenant_cidr'] = tenant_cidr
          net_kl['edge_list'] = [] 
  
          edge_list = tv['sdn']['network']['edge_list']
          edge_net_cntr = 1
          edge_cloud_cntr = 1
          edge_site_cntr = 1
          edge_mobile_cntr = 1

          for edge_item in edge_list:

            if edge_item['type'] == "netrouter":
              edge_count = edge_item['count']
              edge_engine = edge_item['engine']
              for e_item in edge_item['engine']:
                for n_item in range(0,edge_count):
                  edge_kl = TopoTemps.netrouter.copy()
                  edge_kl['name'] = "%s-netrtr-%s-%s" % (sdn_name, net_cntr, edge_net_cntr)
                  edge_kl['engine'] = e_item 
                  edge_kl['tenant_net_name'] = "%s-network-%s-tenant" % (sdn_name, net_cntr)
                  edge_kl['tenant_ip'] = ""
                  edge_kl['tenant_net'] = tenant_cidr
  
                  # Add edge_kl to net_kl['edge_list']
                  net_kl['edge_list'].append(edge_kl)
                  edge_net_cntr += 1

            elif edge_item['type'] == "cloud":
              edge_count = edge_item['count']
              edge_engine = edge_item['engine'] 
              for e_item in edge_item['engine']: 
                for c_item in range(0,edge_count):
                  edge_kl = TopoTemps.cloud.copy()
                  edge_kl['name'] = "%s-cloud-%s-%s" % (sdn_name, net_cntr, edge_cloud_cntr)
                  edge_kl['engine'] = e_item
                  edge_kl['cloud_provider'] = edge_item['cloud_provider']
                  edge_kl['tenant_net_name'] = "%s-network-%s-tenant" % (sdn_name, net_cntr)
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
                  edge_kl['tenant_net'] = tenant_cidr
                  edge_kl['provider_net_name'] = "%s-provider" % edge_kl['name']
                  edge_kl['provider_ip'] = ""
                  #edge_kl['provider_ip'] =  utils.return_ip_subnets(edge_kl['provider_net'], \
                  #        32, skip_zero=True).pop() 

    
                  # Add edge_kl to net_kl['edge_list']
                  net_kl['edge_list'].append(edge_kl)
                  edge_cloud_cntr += 1
                    
            elif edge_item['type'] == "site":
              edge_count = edge_item['count']
              edge_engine = edge_item['engine']
              for e_item in edge_item['engine']:
                for n_item in range(0,edge_count):
                  edge_kl = TopoTemps.site.copy()
                  edge_kl['name'] = "%s-site-%s-%s" % (sdn_name, net_cntr, edge_site_cntr)
                  edge_kl['engine'] = e_item
                  edge_kl['tenant_net_name'] = "%s-network-%s-tenant" % (sdn_name, net_cntr)
                  edge_kl['tenant_ip'] = ""
                  edge_kl['tenant_net'] = tenant_cidr
                  edge_kl['vpn_net'] = ""

                  # Add edge_kl to net_kl['edge_list']
                  net_kl['edge_list'].append(edge_kl)
                  edge_site_cntr += 1 

            elif edge_item['type'] == "mobile":
              pass
  
          # Add net_kl to sdn['network']
          sdn['network'].append(net_kl)
          net_cntr += 1

      return 1, sdn 

    except:
      logging.error("Error: gen_sdn_topo method did not execute cleanly")
          
      return 0, {} 
  
def gen_sdn_net_data(topo, common):
    """
    This function returns a list of 'network' objects that ultimately populates 
    'common.sdn[]' list with network objects
    """
    try:
        ret_net_list = []
        topo_net_list = topo['network']
        for net_item in topo_net_list:
            x = sdn_class.SdnNetObj(net_item, common)
            ret_net_list.append(x)
        return 1, ret_net_list

    except: 
        logging.error("Error: gen_sdn_data method did not complete properly")

        return 0, {}


#def ansible_deploy_lxd_ospf(common, cloud_obj):
#    """
#    This function executes Ansible playbook for configure of basic OSPF
#    into the LXD FRR instance.
#    """
#
#    try: 
#        server_obj = cloud_obj.os['server']['server_obj']
#        # The line below is a workaround to refresh the 'server' object b/c
#        #  it continually comes back with ._info data only half defined
#        dir(server_obj)
#        for loop in range(10):
#            if server_obj._info.has_key('OS-EXT-SRV-ATTR:instance_name') == False:
#                time.sleep(2)
#                print("Loop cntr =: %s" % loop)
#            else:
#                lxd_inst_name = str(server_obj._info['OS-EXT-SRV-ATTR:instance_name'])
#                break
#        engine_ip = common.config['devices']['engines'][cloud_obj.topo['engine']]
#        edge_type = cloud_obj.topo['type'] 
#        if edge_type == "cloud":
#            script = 'lxd-ospf-dual.yml'
#        else:
#            script = 'lxd-ospf-single.yml'
#
#        ansible_cmd = 'ansible-playbook -i %s, "sdn_dp/conf/ansible/playbooks/%s" \
#                       --extra-vars "container_name=%s"' % \
#                       (engine_ip, script, lxd_inst_name)
#        out = subprocess.check_output(ansible_cmd, shell=True)
#
#        return 1, out
#    except:
#        logging.error("Error: ansible_deploy_ospf_lxd: failed to provision properly")
#        return 0, {}

#def ansible_traffic_subint(cloud_obj):
#    '''
#    This function executes Ansible playbook that configures basic subinterface with
#      IP address for external traffic generation.  A cloud object is provided and 
#      all config parameters are derived from 'self.traffic_*'
#    '''
#
#    try:
#        script = traffic_subint
#        ansible_cmd = 'ansible-playbook -i %s, "sdn_dp/conf/ansible/playbooks/%s" \
#                       --extra-vars "traffic_engine_int=%s segment_id=%s \
#                       traffic_engine_int_ip=%s"' % \
#                       (cloud_obj.topo['traffic_engine_ip'], \
#                        script, \
#                        cloud_obj.topo['traffic_engine_int'], \
#                        cloud_obj.topo['segment_id'], \
#                        cloud_obj.topo['traffic_engine_int_ip'])
#        out = subprocess.check_output(ansible_cmd, shell=True)
#
#        return 1, out
#
#    except:
#        logging.error("Error: ansible_traffic_subint: failed to provision properly")
#        return 0, {}


#def ansible_traffic_routes(cloud_obj, common):
#    '''
#    This function will configure necessary routes for external traffic device
#      to pass bi-directional traffic to all other cloud devices in network
#    '''
#
#    try:
#      my_name = cloud_obj.name
#      net_match = re.search('cloud-([0-9]+)-', my_name)
#      my_net_index = net_match.group(1)
#      remote_net_list = []
#      local_net = cloud_obj.topo['provider_net']
#      script = traffic_routes
#
#      for gw in common.sdn[my_net_index].edge_list:
#        if gw.name != my_name:
#          if gw.topo['type'] == 'cloud':
#            remote_net_list.append(gw.topo['provider_net'])
#            remote_traffic_ip = gw.topo['traffic_engine_ip']
#            remote_traffic_gw = gw.topo['provider_ip']
#            # Add route to remote traffic gen for return traffic
#            ansbile_cmd = 'ansible-playbook -i %s, "sdn_dp/conf/ansible/playbooks/%s" \
#                           --extra-vars "remote_net_list=%s \
#                           gateway_ip=%s"' % (remote_traffic_ip, script, \
#                           local_net, remote_traffic_gw)
#
#            out = subprocess.check_output(ansible_cmd, shell=True)
#            #ssh_cmd = "route add %s gw %s" % \
#            #           (self.topo['provider_net'], remote_traffic_gw)
#            #utils.ssh_exec(remote_traffic_ip, ssh_cmd)
#          elif gw.topo['type'] == 'site':
#            pass
#          elif gw.topo['type'] == 'mobile':
#            pass
#      # Add local routes to all remote provider networks
#      ansbile_cmd = 'ansible-playbook -i %s, "sdn_dp/conf/ansible/playbooks/%s" \
#                     --extra-vars "remote_net_list=%s \
#                     gateway_ip=%s"' % (cloud_obj.topo['traffic_engine_ip'], \
#                     script, remote_net_list, cloud_obj.topo['provider_ip'])
#          #ssh_cmd = "route add %s gw %s" % \
#          #           (net, self.topo['provider_ip'])
#          #utils.ssh_exec(self.topo['traffic_engine_ip'], ssh_cmd)
#    
#    except:
#        logging.error("Error: ansible_traffic_routes: failed to provision properly")
#        return 0, {}

    
