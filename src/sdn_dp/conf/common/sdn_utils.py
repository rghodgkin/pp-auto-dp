#!/usr/bin/env python
# encoding: utf-8

import logging
import pdb
import subprocess
import time
import re
#import sdn_dp.conf.common.sdn_class as sdn_class
import sdn_dp.conf.common.utils as utils
from sdn_dp.conf.common.constants import TopoTemps
from sdn_dp.conf.common.constants import SDNVLAN
from sdn_dp.conf.common.constants import SDNCIDR
from sdn_dp.conf.common.constants import OSBRIDGEMAPPING
from sdn_dp.conf.common.constants import TRAFFICINFO


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
  

def traffic_run_handler(src_obj, dst_obj, **kwargs):
    # src vars below represent source traffic generator
    src_engine_ip = src_obj.topo['traffic_engine_ip']
    src_dest_ip = str(re.search('([0-9.]+)/*[0-9]*', \
         dst_obj.topo['traffic_engine_int_ip']).group(1))
    dst_engine_ip = dst_obj.topo['traffic_engine_ip']

    extra_vars = ''
    traffic_time = 10
    traffic_prot = 'tcp'
    traffic_bw = '1G'
    traffic_port = 5201
    if kwargs.has_key('traffic_time'):
        traffic_time = kwargs['traffic_time']
    if kwargs.has_key('traffic_bw'):
        traffic_bw = kwargs['traffic_bw']
    if kwargs.has_key('traffic_prot'):
        traffic_prot = kwargs['traffic_prot']
    if kwargs.has_key('traffic_port'):
        traffic_port = kwargs['traffic_port']

    if src_obj.topo['traffic_mode'] == 'external' and \
           dst_obj.topo['traffic_mode'] == 'external':
      
        try:
          # Execute ansible playbook to start iperf server
          script = 'iperf3-server.yml'
          extra_vars = 'address=%s traffic_port=%s' % (src_dest_ip, traffic_port)
          ansible_cmd = 'ansible-playbook -i %s, "sdn_dp/conf/ansible/playbooks/%s" \
                         --extra-vars "%s"' % (dst_engine_ip, script, extra_vars)
          out = subprocess.check_output(ansible_cmd, shell=True)
          time.sleep(2)
 
          # Execute ansible playbook to start client traffic
          script = 'iperf3-client-tcp.yml'
          extra_vars = 'address=%s traffic_time=%s traffic_port=%s \
                        traffic_bw=%s' % (src_dest_ip, \
                        traffic_time, traffic_port, traffic_bw)
          ansible_cmd = 'ansible-playbook -i %s, "sdn_dp/conf/ansible/playbooks/%s" \
                         --extra-vars "%s"' % (src_engine_ip, script, extra_vars)
          out_result = subprocess.check_output(ansible_cmd, shell=True)
          out_result = subprocess.check_output(ansible_cmd, shell=True)
          time.sleep(2)
 
          # Execute ansible playbook to kill iperf server process
          script = 'iperf3-server-kill.yml' 
          extra_vars = 'traffic_port=%s' % (traffic_port)
          ansible_cmd = 'ansible-playbook -i %s, "sdn_dp/conf/ansible/playbooks/%s" \
                         --extra-vars "%s"' % (dst_engine_ip, script, extra_vars)
          out = subprocess.check_output(ansible_cmd, shell=True)
 
          send_result = ''
          rev_result = ''
          sum_sent = 0.0
          sum_rcv = 0.0
          sum_rev_sent = 0.0
          sum_rev_rcvd = 0.0
          sum_sent = float(re.search('SUM_SENT=([0-9.]*)\\\\n', out_result).group(1))
          sum_rcvd = float(re.search('SUM_RCVD=([0-9.]*)\\\\n', out_result).group(1))
          sum_rev_sent = float(re.search('SUM_REV_SENT=([0-9.]*)\\\\n', out_result).group(1))
          sum_rev_rcvd = float(re.search('SUM_REV_RCVD=([0-9.]*)\\\\n', out_result).group(1))
 
          traffic_pass_perc = TRAFFICINFO.TRAFFIC_PASS_PERCENT / 100
          if sum_rcvd > sum_sent * traffic_pass_perc:
             send_result = 'pass' 
          else:
             logging.info("TRAFFIC FAIL: Traffic sent from %s to %s was less than %s \
                           sum sent bps = %s, sum received bps = %s") % \
                           (src_obj.name, dst_obj.name, traffic_pass_perc, sum_sent, sum_rcvd)
             send_result = 'fail'
 
          if sum_rev_rcvd > sum_rev_sent * traffic_pass_perc:
             rev_result = 'pass'
          else:
             logging.info("TRAFFIC FAIL: Reverse traffic sent from %s to %s was less than %s \
                           sum sent bps = %s, sum received bps = %s") % \
                           (src_obj.name, dst_obj.name, traffic_pass_perc, sum_sent, sum_rcvd) 
             rev_result = 'fail'
         
          if send_result == 'pass' and rev_result == 'pass':
              return 1, {}
          else:
              return 0, {'sum_sent': sum_sent, 'sum_rcvd':sum_rcvd, 'sum_rev_sent':sum_rev_sent, \
                         'sum_rev_rcvd':sum_rev_rcvd}

        except:
            logging.error("Error: traffic_run_handler failed to execute properly")
            pdb.set_trace()
            return 0, {}

    elif src_obj.topo['traffic_mode'] == 'os' and \
           dst_obj.topo['traffic_mode'] == 'os':
        #src_engine_ip = src_obj.topo['traffic_engine_ip']
        #src_dest_ip = str(re.search('([0-9.]+)/[0-9]+', \
        #   dst_obj.topo['traffic_engine_int_ip']).group(1))
        #dst_engine_ip = dst_obj.topo['traffic_engine_ip'] 
        pdb.set_trace()
        dst_lxd_inst_name = dst_obj.topo['traffic_instance_name']

        script = 'iperf3-server-lxd.yml'
        extra_vars = 'traffic_engine_int_ip=%s traffic_instance_name=%s traffic_port=%s' \
                      % (src_dest_ip, dst_lxd_inst_name, traffic_port)
        ansible_cmd = 'ansible-playbook -i %s, "sdn_dp/conf/ansible/playbooks/%s" \
                         --extra-vars "%s"' % (dst_engine_ip, script, extra_vars)
        out = subprocess.check_output(ansible_cmd, shell=True)
        time.sleep(2)


















