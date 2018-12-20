#!/usr/bin/env python
# encoding: utf-8

import logging
import subprocess
import yaml
import os
import time
import re
import jinja2
import pdb
import sdn_dp.conf.common.utils as utils
import sdn_dp.conf.common.sdn_utils as sdn_utils
import sdn_dp.conf.common.ansible_utils as ansible_utils
from sdn_dp.conf.common.constants import SDNCIDR
from sdn_dp.conf.common.constants import OSCLOUDIMAGE
from sdn_dp.conf.common.constants import OSCLOUDFLAVOR
from sdn_dp.conf.common.constants import CLOUDCONFIGTEMPS
from sdn_dp.conf.common.constants import CLOUDPROVINFO
from sdn_dp.conf.common.constants import TRAFFICINFO

class SdnNetObj(object):
    def __init__(self, topo_dict, common):
        self.topo = topo_dict
        self.common = common
        self.tenant_cidr = self.topo['tenant_cidr']
        self.tenant_net_name = self.topo['tenant_net_name']
        self.tenant_net_obj = ""
        self.tenant_net_subnet_obj = ""
        self.edge_list = []
        self.edge_name_list = {'netrouter':{}, 'cloud':{}, 'site':{}, \
                                'mobile':{}}
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
            tmp_obj = SdnNetrouterCloudObj(topo_dict, self.common, self)
            self.edge_netrouter_list.append(tmp_obj)
            self.edge_list.append(tmp_obj)
            self.edge_name_list['netrouter'][topo_dict['name']] = tmp_obj

        elif type == "cloud":
            tmp_obj = SdnEdgeCloudObj(topo_dict, self.common, self)
            self.edge_cloud_list.append(tmp_obj) 
            self.edge_list.append(tmp_obj)
            self.edge_name_list['cloud'][topo_dict['name']] = tmp_obj

        elif type == "site":
            tmp_obj = SdnEdgeSiteCloudObj(topo_dict, self.common, self)
            self.edge_site_list.append(tmp_obj) 
            self.edge_list.append(tmp_obj)
            self.edge_name_list['site'][topo_dict['name']] = tmp_obj

        elif type == "mobile":
            tmp_obj = SdnEdgeMobileCloudObj(topo_dict, self.common, self)
            self.edge_mobile_list.append(tmp_obj)
            self.edge_list.append(tmp_obj)
            self.edge_name_list['mobile'][topo_dict['name']] = tmp_obj

    def list_edge_inst(self):
        '''
        This function will list all the 'edge' instances from
        the various *_cloud_list arrays 
        ''' 
        return self.edge_list 
        

class SdnEdgeParent(object):
    def __init__(self, topo_dict, common, net_obj):
        self.topo = topo_dict.copy()
        self.name = self.topo['name']
        self.common = common
        self.network = net_obj
        self.os = {'networks':{'tenant':{'net_obj':'', 'subnet_obj':'', \
                   'port_name':'', 'port_obj':''}}, 
                   'server':{'server_obj':''}}
        self.traffic_info = {}
        self.deploy_state = 0
        self.traffic_state = 0
        self.traffic_running = 0

    def destroy(self):
        server = self.os['server']['server_obj'] 
        logging.info("destroy: deleting server %s" % self.name)
        server.delete()

        self.deploy_state = 0


class SdnNetrouterCloudObj(SdnEdgeParent):
    def __init__(self, topo_dict, common, net_obj):
        SdnEdgeParent.__init__(self, topo_dict, common, net_obj)

    def deploy(self):
        if self.deploy_state == 0:
            nova = self.common.os['clients']['nova']['client']

            image = nova.glance.find_image('%s' % OSCLOUDIMAGE.netrouter)
            flavor_name = OSCLOUDFLAVOR.netrouter
            flavor = nova.flavors.find(name=flavor_name)
            net_tenant = self.os['networks']['tenant']['net_obj']['network']['id']
            nics = [{'net-id': net_tenant, 'name': 'tenant-port'}]
            # Openstack has some inconsistency where the instance ID does not always
            #   get populated in the object.  If not present kill and respawn
            userdata = '#cloud-config\nruncmd:\n- [cloud-init-per, once, configure-net, /usr/local/bin/configure]\n\n'

            for respawn in range(5):
                instance = nova.servers.create(name=self.name, image=image, \
                                           flavor=flavor, nics=nics, \
                                           availability_zone=self.topo['engine'], \
                                           userdata=userdata) 

                time.sleep(5)
                dir(instance)
                if instance._info['OS-EXT-SRV-ATTR:instance_name'] != '':
                    break
                else:
                    instance.delete()
                    time.sleep(5)

            instance_net_info = instance.interface_list()
            self.topo['tenant_ip'] = instance_net_info[0].fixed_ips[0]['ip_address']
            self.topo['tenant_mac'] = instance_net_info[0].mac_addr
            self.os['server']['server_obj'] = instance
            self.topo['instance_name'] = instance._info['OS-EXT-SRV-ATTR:instance_name']

            self.deploy_state = 1

            return 1


        else:
            logging.info("SdnNetrouterCloudObj: deploy of %s failed b/c \
                          already in deployed state" % selfname)
            return 0


class SdnEdgeCloudObj(SdnEdgeParent):
    def __init__(self, topo_dict, common, net_obj):
        SdnEdgeParent.__init__(self, topo_dict, common, net_obj)
        # Initialize cloud specific Openstack dict keys
        self.os['networks']['provider'] = {'net_obj':'', 'port_obj':''}

    def deploy(self):
        if self.deploy_state == 0:

            nova = self.common.os['clients']['nova']['client']

            image = nova.glance.find_image('%s' % OSCLOUDIMAGE.cloud)
            flavor_name = OSCLOUDFLAVOR.cloud
            flavor = nova.flavors.find(name=flavor_name)
            net_tenant = self.os['networks']['tenant']['net_obj']['network']['id']
            net_provider = self.os['networks']['provider']['net_obj']['network']['id']
            nics = [{'net-id': net_tenant, 'name': '%s-tenant-port' % self.name},
                    {'net-id': net_provider, 'name': '%s-provider-port' % self.name}]
            # For now we are going to leverage Dave's 'create_cloud_config.py' file as
            #  intermediate.   It will be placed into the '/src/sdn_dp/conf/common/templates'
            #   directory as 'create_cloud_config.j2'.  This file needs to be updated 
            #   for following jinja substitutions:
            #       controller_ip_1 = Controller IP address of first RR
            #       controller_ip_2 = Controller IP address of second RR
            #       cloud_prov_ip = AWS/Google cloud provider ip
            #       cloud_prov_asn = AWS/Goodle ASN number
            #      

            j2_env = jinja2.Environment(loader=jinja2.FileSystemLoader('sdn_dp/conf/common/templates/'))
            template = j2_env.get_template(CLOUDCONFIGTEMPS.cloud)
            # Find netrouter/controller IP addresses assigned
            controller_ip = {1:'', 2:''}
            for nr_index in range(len(self.network.edge_netrouter_list)):
                controller_ip[nr_index + 1] = str(self.network.edge_netrouter_list[nr_index].topo['tenant_ip']) 
            # All edge container devices will be auto configured to x.x.x.200/24
            host_ip_list = utils.return_ip_subnets(self.topo['provider_net'], 32, skip_zero=True)
            regex_match = re.search("([0-9.]+)/[0-9]+", host_ip_list[255 - int(TRAFFICINFO.EXTERNAL_IP)])
            traf_gen_ip = '%s' % regex_match.group(1)
            # Create render keyed-list for jinja overlay
            render_klist = {'controller_ip_1':controller_ip[1], 'controller_ip_2':controller_ip[2], \
                            'cloud_prov_ip':traf_gen_ip, 'cloud_prov_asn':CLOUDPROVINFO.AWSDEFAULTBGPID}
            file_render = template.render(render_klist)
            outfile = 'sdn_dp/conf/common/templates/' + CLOUDCONFIGTEMPS.cloud.rsplit('.', 1)[0] + '.py'
            outfile_name = CLOUDCONFIGTEMPS.cloud.rsplit('.', 1)[0] + '.py'
            with open(outfile, 'w') as fp:
                fp.write(file_render)
            os.chmod(outfile, 0700)
            subprocess.check_output('./%s' % outfile_name, cwd='sdn_dp/conf/common/templates/', shell=True) 
            with open('sdn_dp/conf/common/templates/cloud-config.yml', 'r') as fp:
                userdata = fp.read()

            # Openstack has some inconsistency where the instance ID does not always
            #   get populated in the object.  If not present kill and respawn
            for respawn in range(5):
                instance = nova.servers.create(name=self.name, image=image, \
                                           flavor=flavor, nics=nics, \
                                           availability_zone=self.topo['engine'], \
                                           userdata=userdata)
                time.sleep(1)
                dir(instance)
                if instance._info['OS-EXT-SRV-ATTR:instance_name'] != '':
                    break
                else:
                    instance.delete()
                    time.sleep(5)

            self.os['server']['server_obj'] = instance
            self.topo['instance_name'] = instance._info['OS-EXT-SRV-ATTR:instance_name']

            for loop in range(10):
                time.sleep(2)
                print("Loop cntr =: %s" % loop)
                instance_net_info = instance.interface_list()
                if len(instance_net_info) == 2:
                    break

            # The below ensures to grab correct interface IP for tenant vs provider,
            #  Openstack is not always consistent 
            tenant_regex = re.search('([0-9]+\.[0-9]+)\.', SDNCIDR.OS_TENANT_IP_START).group(1)
            for cntr in range(2):
                ip_tmp = instance_net_info[cntr].fixed_ips[0]['ip_address']
                if re.search(tenant_regex, ip_tmp):
                    self.topo['tenant_ip'] = ip_tmp
                    self.topo['tenant_mac'] = instance_net_info[cntr].mac_addr
                else:
                    self.topo['provider_ip'] = ip_tmp 
                    self.topo['provider_mac'] = instance_net_info[cntr].mac_addr


            self.deploy_state = 1
   
            return 1

        else:
            logging.info("SdnNetrouterCloudObj: deploy of %s failed b/c \
                          already in deployed state" % selfname)
            return 0 

    def traffic_run(self, dest_name, **kwargs):
        '''
        This method runs traffic in foreground for x number of seconds, default
        being 10 seconds and verifies that sent versus received is within 99% of
        each other
                 Args:  traffic_time=x   (default 10)
                        traffic_port=x   (default 5201) 
        '''

        if self.traffic_state == 0:
        # If traffic_state = 0 then we need to configure the subinterface
        #   and routes on each gateway device for reachability
          if self.topo['traffic_mode'] == "external":
            # The below will configure traffic requirements for all
            #  gateways in same network as this device - thus traffic
            #  can be sent anywhere
            # 'ansible_traffic_routes' sets 'obj.traffic_state'->1
            ansible_utils.ansible_traffic_subint(self)
            ansible_utils.ansible_traffic_routes(self)

          elif self.topo['traffic_mode'] == "os":
              pass

        # Start iperf3 foreground instance 
        logging.info("Starting traffic between %s and %s" % (self.name, dest_name))
        dst_obj = self.network.edge_name_list['cloud'][dest_name]
        output = sdn_utils.traffic_run_handler(self, dst_obj, **kwargs)[0] 
        if output == 1:
            logging.info("Traffic for %s -> %s passed" % (self.name, dest_name))
            return 1
        else:
            logging.info("Traffic for %s -> %s failed" % (self.name, dest_name))
            return 0

    def traffic_start(self, dest_name, **kwargs):
        '''
        This method starts background traffic between source gw and dst gw
        and leaves running for x seconds.   Stdout will be written into a tmp
        file upon traffic_stop located in '/tmp/<src>-<dst>-<pid>.log'
        iperf3 pid info will be writen into 'self.traffic_info{} data structure
        such that 'traffic_stop' and other routines can access later.
        '''

        if self.traffic_state == 0:
        # If traffic_state = 0 then we need to configure the subinterface
        #   and routes on each gateway device for reachability 
          if self.topo['traffic_mode'] == "external":
            # The below will configure traffic requirements for all
            #  gateways in same network as this device - thus traffic
            #  can be sent anywhere
            # 'ansible_traffic_routes' sets 'obj.traffic_state'->1
            ansible_utils.ansible_traffic_subint(self)
            ansible_utils.ansible_traffic_routes(self)

          elif self.topo['traffic_mode'] == "os":
            pass

        if self.traffic_running == 0:
          logging.info("Starting background traffic between %s and %s" \
                        % (self.name, dest_name))
          dst_obj = self.network.edge_name_list['cloud'][dest_name]
          output = sdn_utils.traffic_start_handler(self, dst_obj, **kwargs)[0]

          return 1

        else:
          logging.info("Error: traffic_start: cannot start traffic, already \
                          in running state")
          return 0

    def traffic_stop(self, dest_name, **kwargs):
        '''
        This method stops background traffic between source gw and dst gw.
        This method accompanies the 'traffic_start' method.
        '''

        if self.traffic_running == 1:
          logging.info("Stopping background traffic between %s and %s" \
                        % (self.name, dest_name))
          dst_obj = self.network.edge_name_list['cloud'][dest_name]
          output = sdn_utils.traffic_stop_handler(self, dst_obj, **kwargs)[0]

          return 1

        else:
          logging.info("Error: traffic_stop: cannot stop traffic, already \
                          in stopped state")
          return 0


class SdnEdgeSiteCloudObj(SdnEdgeParent):
    def __init__(self, topo_dict, common, net_obj):
        SdnEdgeParent.__init__(self, topo_dict, common, net_obj) 

    def deploy(self):
        pass


class SdnEdgeMobileCloudObj(SdnEdgeParent):
    def __init__(self, topo_dict, common, net_obj):
        SdnEdgeParent.__init__(self, topo_dict, common, net_obj)

    def deploy(self):
        pass


        

