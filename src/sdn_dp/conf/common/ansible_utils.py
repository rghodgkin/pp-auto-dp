import logging
import pdb
import subprocess
import time
import re


def ansible_deploy_lxd_ospf(common, cloud_obj):
    """
    This function executes Ansible playbook for configure of basic OSPF
    into the LXD FRR instance.
    """

    try:
        #server_obj = cloud_obj.os['server']['server_obj']
        # The line below is a workaround to refresh the 'server' object b/c
        #  it continually comes back with ._info data only half defined
        #dir(server_obj)
        #for loop in range(10):
        #    if server_obj._info.has_key('OS-EXT-SRV-ATTR:instance_name') == False:
        #        time.sleep(2)
        #        print("Loop cntr =: %s" % loop)
        #    else:
        #        lxd_inst_name = str(server_obj._info['OS-EXT-SRV-ATTR:instance_name'])
        #        break
        lxd_inst_name = cloud_obj.topo['instance_name']
        engine_ip = common.config['devices']['engines'][cloud_obj.topo['engine']]
        edge_type = cloud_obj.topo['type']

        if edge_type == "cloud":
            script = 'lxd-ospf-dual.yml'
        else:
            script = 'lxd-ospf-single.yml'

        ansible_cmd = 'ansible-playbook -i %s, "sdn_dp/conf/ansible/playbooks/%s" \
                       --extra-vars "container_name=%s"' % \
                       (engine_ip, script, lxd_inst_name)

        out = subprocess.check_output(ansible_cmd, shell=True)

        return 1, out
    except:
        logging.error("Error: ansible_deploy_ospf_lxd: failed to provision properly")
        pdb.set_trace()
        return 0, {}

def ansible_deploy_lxd_traffic_ospf(common, cloud_obj):
    """
    This function executes Ansible playbook for configure of basic OSPF
      for the traffic instance attached to a gateway
    """

    try:
        lxd_inst_name = cloud_obj.topo['traffic_instance_name']
        engine_ip = cloud_obj.topo['traffic_engine_ip']
        edge_type = cloud_obj.topo['type']
        script = 'lxd-ospf-single.yml'

        ansible_cmd = 'ansible-playbook -i %s, "sdn_dp/conf/ansible/playbooks/%s" \
                       --extra-vars "container_name=%s"' % \
                       (engine_ip, script, lxd_inst_name)

        out = subprocess.check_output(ansible_cmd, shell=True)

        return 1, out
    except:
        logging.error("Error: ansible_deploy_lxd_traffic_ospf: failed to provision properly")
        print("Command is: out = subprocess.check_output(ansible_cmd, shell=True) ")
        pdb.set_trace()
        return 0, {}


def ansible_traffic_subint(cloud_obj):
    '''
    This function executes Ansible playbook that configures basic subinterface with
      IP address for external traffic generation.  A cloud object is provided and
      all config parameters are derived from 'self.traffic_*'
    '''

    try:
        my_name = cloud_obj.name
        net_match = re.search('cloud-([0-9]+)-', my_name)
        my_net_index = int(net_match.group(1)) - 1
        script = 'traffic_subint.yml'

        for gw in cloud_obj.common.sdn[my_net_index].edge_list:
          if gw.topo['type'] == 'cloud':
            ansible_cmd = 'ansible-playbook -i %s, "sdn_dp/conf/ansible/playbooks/%s" \
                       --extra-vars "traffic_engine_int=%s segment_id=%s \
                       traffic_engine_int_ip=%s"' % \
                       (gw.topo['traffic_engine_ip'], \
                        script, \
                        gw.topo['traffic_engine_int'], \
                        gw.topo['segment_id'], \
                        gw.topo['traffic_engine_int_ip'])
            out = subprocess.check_output(ansible_cmd, shell=True)
             
          elif gw.topo['type'] == 'site':
              pass

          elif gw.topo['type'] == 'mobile':
              pass

        return 1, out

    except:
        logging.error("Error: ansible_traffic_subint: failed to provision properly")
        pdb.set_trace()
        return 0, {}


def ansible_traffic_routes(cloud_obj):
    '''
    This function will configure necessary routes on all gateways within the
      network of 'cloud_obj' such that bidirectional traffic can flow
    '''

    try:
      my_name = cloud_obj.name
      net_match = re.search('cloud-([0-9]+)-', my_name)
      my_net_index = int(net_match.group(1)) - 1
      edge_list = cloud_obj.common.sdn[my_net_index].edge_list
      script = 'traffic_routes.yml'
      for src_gw in edge_list:
        local_net = src_gw.topo['provider_net']
        src_name = src_gw.name
        for gw in edge_list:
          if gw.name != src_name:
            if gw.topo['type'] == 'cloud':
              remote_traffic_ip = gw.topo['traffic_engine_ip']
              remote_traffic_gw = gw.topo['provider_ip']
              # Add route to remote traffic gen for return traffic
              ansible_cmd = 'ansible-playbook -i %s, "sdn_dp/conf/ansible/playbooks/%s" \
                           --extra-vars "cidr=%s \
                           gateway_ip=%s"' % (remote_traffic_ip, script, \
                           local_net, remote_traffic_gw)

              out = subprocess.check_output(ansible_cmd, shell=True)

            elif gw.topo['type'] == 'site':
              pass

        gw.traffic_state = 1

    except:
        logging.error("Error: ansible_traffic_routes: failed to provision properly")
        return 0, {}


