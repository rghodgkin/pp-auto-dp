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
    src_engine_gw = src_obj.topo['provider_ip']
    src_dest_ip = str(re.search('([0-9.]+)/*[0-9]*', \
         dst_obj.topo['traffic_engine_int_ip']).group(1))
    src_dest_gw = dst_obj.topo['provider_ip']
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
      if src_obj.traffic_running == 0:  
        try:

          # Run short traffic set below to ensure datapath
          prime_success = 0
          for loop in range(5):
              logging.info("Running prime traffic procedure...")
              # Execute ansible playbook to start iperf server
              script = 'iperf3-server.yml'
              extra_vars = 'address=%s traffic_port=%s gateway=%s' \
                        % (src_dest_ip, traffic_port, src_dest_gw)
              ansible_cmd = 'ansible-playbook -i %s, "sdn_dp/conf/ansible/playbooks/%s" \
                         --extra-vars "%s"' % (dst_engine_ip, script, extra_vars)
              out = subprocess.check_output(ansible_cmd, shell=True)
              time.sleep(2)

              script = 'iperf3-client-tcp.yml'
              extra_vars_prime = 'address=%s traffic_time=5 traffic_port=%s, gateway=%s' % \
                        (src_dest_ip, traffic_port, src_engine_gw)
              ansible_cmd_prime = 'ansible-playbook -i %s, "sdn_dp/conf/ansible/playbooks/%s" \
                         --extra-vars "%s"' % (src_engine_ip, script, extra_vars_prime)
              out_prime = subprocess.check_output(ansible_cmd_prime, shell=True)
              
              if str(out_prime.find('unable to connect to server')) != '-1':
                   # Execute ansible playbook to kill iperf server process
                  script = 'iperf3-server-kill.yml'
                  ansible_cmd = 'ansible-playbook -i %s, "sdn_dp/conf/ansible/playbooks/%s" \
                          --extra-vars "%s"' % (dst_engine_ip, script, extra_vars)
                  out = subprocess.check_output(ansible_cmd, shell=True)
                  time.sleep(3)
              else:
                  prime_success = 1
                  break
                   
          if prime_success == 1:
            logging.info("Running main traffic generation...")
            extra_vars = 'address=%s traffic_time=%s traffic_port=%s, gateway=%s' % \
                          (src_dest_ip, traffic_time, traffic_port, src_engine_gw) 
            ansible_cmd = 'ansible-playbook -i %s, "sdn_dp/conf/ansible/playbooks/%s" \
                           --extra-vars "%s" -vvv' % (src_engine_ip, script, extra_vars)
            #subprocess.check_output(ansible_cmd_prime, shell=True)
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
          else:
              logging.error("traffic_run_handler: traffic prime failed - not executing main traffic")
              return 0, {}

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

def traffic_start_handler(src_obj, dst_obj, **kwargs):
    # src vars below represent source traffic generator
    src_engine_ip = src_obj.topo['traffic_engine_ip']
    src_engine_gw = src_obj.topo['provider_ip']
    src_dest_ip = str(re.search('([0-9.]+)/*[0-9]*', \
         dst_obj.topo['traffic_engine_int_ip']).group(1))
    src_dest_gw = dst_obj.topo['provider_ip']
    dst_engine_ip = dst_obj.topo['traffic_engine_ip']

    extra_vars = ''
    traffic_time = 10000
    traffic_prot = 'tcp'
    traffic_bw = '1G'
    traffic_send_port = 5201
    traffic_rev_port = 5202
    if kwargs.has_key('traffic_time'):
        traffic_time = kwargs['traffic_time']
    if kwargs.has_key('traffic_bw'):
        traffic_bw = kwargs['traffic_bw']
    if kwargs.has_key('traffic_prot'):
        traffic_prot = kwargs['traffic_prot']
    if kwargs.has_key('traffic_send_port'):
        traffic_port = kwargs['traffic_send_port']
    if kwargs.has_key('traffic_rev_port'):
        traffic_port = kwargs['traffic_rev_port']

    if src_obj.topo['traffic_mode'] == 'external' and \
           dst_obj.topo['traffic_mode'] == 'external':
      if src_obj.traffic_running == 0:
        try:

          # Run short traffic set below to ensure datapath
          script = 'iperf3-server-bg.yml'
          extra_vars = 'address=%s traffic_send_port=%s traffic_rev_port=%s' \
                   % (src_dest_ip, traffic_send_port, traffic_rev_port)
          ansible_cmd = 'ansible-playbook -i %s, "sdn_dp/conf/ansible/playbooks/%s" \
                  --extra-vars "%s"' % (dst_engine_ip, script, extra_vars)
          #logging.info("iperf3 server: %s" % ansible_cmd)
          out = subprocess.check_output(ansible_cmd, shell=True)
          time.sleep(1)
  
          #logging.info("Starting background traffic for %s <-> %s..." \
          #              % (src_obj.name, dst_obj.name))
          script = 'iperf3-client-tcp-bg.yml'
          extra_vars = 'address=%s traffic_time=%s traffic_send_port=%s traffic_rev_port=%s' % \
                        (src_dest_ip, traffic_time, traffic_send_port, traffic_rev_port)
          ansible_cmd = 'ansible-playbook -i %s, "sdn_dp/conf/ansible/playbooks/%s" \
                         --extra-vars "%s"' % (src_engine_ip, script, extra_vars)
          #logging.info("iperf3 client: %s" % ansible_cmd)

          out_result = subprocess.check_output(ansible_cmd, shell=True)

          src_obj.traffic_running = 1

          return 1, {}

        except:
          logging.error("Error: traffic_start_handler failed to execute properly")
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



def traffic_stop_handler(src_obj, dst_obj, **kwargs):
    # src vars below represent source traffic generator
    src_engine_ip = src_obj.topo['traffic_engine_ip']
    src_engine_gw = src_obj.topo['provider_ip']
    src_dest_ip = str(re.search('([0-9.]+)/*[0-9]*', \
         dst_obj.topo['traffic_engine_int_ip']).group(1))
    src_dest_gw = dst_obj.topo['provider_ip']
    dst_engine_ip = dst_obj.topo['traffic_engine_ip']

    extra_vars = ''
    traffic_send_port = 5201
    traffic_rev_port = 5202
    if kwargs.has_key('traffic_send_port'):
        traffic_port = kwargs['traffic_send_port']
    if kwargs.has_key('traffic_rev_port'):
        traffic_port = kwargs['traffic_rev_port']

    if src_obj.topo['traffic_mode'] == 'external' and \
           dst_obj.topo['traffic_mode'] == 'external':
      if src_obj.traffic_running == 1:
        try:

            # Execute ansible playbook to kill iperf client processes
            script = 'iperf3-client-tcp-bg-kill.yml'
            extra_vars = 'address=%s traffic_send_port=%s traffic_rev_port=%s' \
                          % (src_dest_ip, traffic_send_port, traffic_rev_port)
            ansible_cmd = 'ansible-playbook -i %s, "sdn_dp/conf/ansible/playbooks/%s" \
                           --extra-vars "%s"' % (dst_engine_ip, script, extra_vars)
            logging.info("iperf3 kill client: %s" % ansible_cmd)
            out = subprocess.check_output(ansible_cmd, shell=True)

            # Execute ansible playbook to kill iperf server processes
            script = 'iperf3-server-bg-kill.yml'
            extra_vars = 'address=%s traffic_send_port=%s traffic_rev_port=%s' \
                          % (src_dest_ip, traffic_send_port, traffic_rev_port)
            ansible_cmd = 'ansible-playbook -i %s, "sdn_dp/conf/ansible/playbooks/%s" \
                           --extra-vars "%s"' % (dst_engine_ip, script, extra_vars)
            logging.info("iperf3 kill server: %s" % ansible_cmd)
            out = subprocess.check_output(ansible_cmd, shell=True)

            src_obj.traffic_running = 0
            return 1, {}

        except:
            logging.error("Error: traffic_stop_handler failed to execute properly")
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


def traffic_stop_iperf3_all(engine_ip, **kwargs):
    '''
    This function will log into the engine_ip provided and kill all iperf3 processes
    that are currently running.
    '''

    try:

        # Execute ansible playbook to kill iperf client processes
        script = 'iperf3-kill-all.yml'
        ansible_cmd = 'ansible-playbook -i %s, "sdn_dp/conf/ansible/playbooks/%s"' \
                       % (engine_ip, script)
        logging.info("Killing all iperf3 processes on engine %s" % engine_ip)
        out = subprocess.check_output(ansible_cmd, shell=True)

        return 1, {}

    except:
        logging.error("Error: traffice_stop_iperf3_all: failed to execute properly")
        pdb.set_trace()
        return 0, {}

def return_sys_util(cloud_obj, **kwargs):
    '''
    This procedure finds the engine upon which the cloud object is running and
    returns the system utilization for cpu, mem, etc
    Return string values are:
                { 
                  CPU: {user:<value>, sys:value, idle:value, load:<value>}
                  MEM: {kbfree:<value>, kbused:<value>, percused:<value>}
                  DISK: {tps:<value>, rkbs:<value>, wkbsp:<value>, util:<value>}
                  INT: {rps:<value>, tps:<value>, rbs:<value>, tbs:<value>}}
                }

                CPU: "USER=$3 SYS=$4 IDLE=$8"
                MEM: "KBFREE=$2 KBUSED=$4 PERCUSED=$5"
                DISK: "TPS=$3 RKBS=$4 WKBS=$5 UTIL=$10"
                INT:  "RPS=$3 TPS=$4 RBS=$5 TBS=$6"
    '''

    try:

       engine_name = cloud_obj.topo['engine']
       engine_ip = cloud_obj.common.config['devices']['engines'][engine_name]
       
       script = 'return_sys_util.yml'
       ansible_cmd = 'ansible-playbook -i %s, "sdn_dp/conf/ansible/playbooks/%s"' \
                       % (engine_ip, script)
       logging.info("Pulling system utilization stats for %s" % engine_ip)
       out = subprocess.check_output(ansible_cmd, shell=True)
       kw = {}
       ret_klist = {}
       kw['cpu'] = ["CPU-USER", "CPU-SYS", "CPU-IDLE"]
       kw['cpuload'] = ["PSIZE", "QSIZE", "LAVG1", "LAVG5", "LAVG15"]
       kw['mem'] = ["MEM-KBFREE", "MEM-KBUSED", "MEM-PERCUSED"]
       kw['disk'] = ["DISK-TPS", "DISK-RKBS", "DISK-WKBS", "DISK-UTIL"]
       kw['int'] = ["INT-RPS", "INT-TPS", "INT-RBS", "INT-TBS"]
       key_list = ["cpu", "cpuload", "mem", "disk", "int"]
       for key in key_list:
           ret_klist[key] = {}
           for key_sub in kw[key]:
               search_str = "%s=([0-9.a-zA-Z]+)" % key_sub
               ret_klist[key][key_sub] = re.search(search_str, out).group(1)

       return 1, ret_klist

    except:
       logging.error("Error: return_sys_util: failed to execute properly")
       pdb.set_trace()
       return 0, {}

def verify_gws_up(net_obj, **kwargs):
    '''
    This procedure verifies the LXD status of all gateways in a net object.
    Returns 1 if all are in 'running' state, 0 otherwise.  Also returns a list
    of those running and down in a keyed list as secondary value.
                return 0|1, {'running':[<list>], 'down': [<list]}
    '''
    
    try:

        return_status = 1
        running_list = []
        stopped_list = []
        for gw in net_obj.edge_list:
            engine_ip = gw.common.config['devices']['engines'][gw.topo['engine']]
            lxc_instance = gw.topo['instance_name']
            
            script = 'lxd-inst-info.yml'
            extra_vars = 'instance=%s version=info' % lxc_instance 
            ansible_cmd = 'ansible-playbook -i %s, "sdn_dp/conf/ansible/playbooks/%s" \
                      --extra-vars "%s"' % (engine_ip, script, extra_vars)
            out = subprocess.check_output(ansible_cmd, shell=True)
            if re.search('Status: +Running', out):
                running_list.append(gw.name)
            else:
                stopped_list.append(gw.name)
                return_status = 0
 
        return return_status, {'running':running_list, 'stopped':stopped_list}

    except:
        logging.error("Error: verify_gws_up: failed to execute properly")
        pdb.set_trace()
        return 0, {}














