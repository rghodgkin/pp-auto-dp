#!/usr/bin/env python
# encoding: utf-8

import os
from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client as kclient
from glanceclient import client as gclient
from novaclient import client as nclient
from neutronclient.neutron import client as neuclient
from sdn_dp.conf.common.constants import OSPRECONFIG 
from sdn_dp.conf.common.constants import OSBRIDGEMAPPING
import pdb


def return_keystone_sess(os_config):
    try:
        os_user = os_config['os_user']
        os_pass = os_config['os_pass']
        os_authurl = os_config['os_authurl']
    
        auth = v3.Password(auth_url=os_authurl, username=os_user, \
               password=os_pass, project_name="admin", \
               user_domain_id="default", project_domain_id="default")
        sess = session.Session(auth=auth)
        return 1, sess

    except:
        logging.error("return_keystone_sess: Issue getting Openstack \
                       session object")
        return 0, {}

def gen_os_clients(self):
    try:
        output = {}
        # Grab handles to each client type
        keystone = kclient.Client(session=self.os['sess'])
        output['keystone'] = {}
        output['keystone']['client'] = keystone
                 
        glance = gclient.Client(2, session=self.os['sess']) 
        output['glance'] = {}
        output['glance']['client'] = glance
    
        nova = nclient.Client(2, session=self.os['sess'])
        output['nova'] = {}
        output['nova']['client'] = nova 
    
        neutron = neuclient.Client(2, session=self.os['sess'])
        output['neutron'] = {}
        output['neutron']['client'] = neutron 

        return 1, output

    except:
        logging.error("return_keystone_sess: Issue getting Openstack \
                       session object")
        return 0, {} 

def config_os_pre(self):
    try:
        # Grab 'images' dict key and upload each one specified in list
#        image_list = OSPRECONFIG.images
#        glance = self.os['clients']['glance']['client']
#
#        for item in image_list:
#            image = glance.images.create(name=item['name'], \
#                                         container_format='bare', \
#                                         disk_format='qcow2')
#            glance.images.upload(image.id, open(item['path'], 'rb'))

        # Configure 'small' flavor inside of nova
        flavor_list = OSPRECONFIG.flavors
        nova = self.os['clients']['nova']['client'] 
        self.os['flavors'] = {}
        for item in flavor_list:
            check = 0 
            check = nova.flavors.find(name=item['name'])
            if check == 0:
                flavor = nova.flavors.create(name=item['name'],\
                                             ram=item['ram'],\
                                             vcpus=item['vcpus'],\
                                             disk=item['disk'])
                self.os['flavors'][item['name']] = flavor
            else:
                self.os['flavors'][item['name']] = check

        return 1, {}

    except:
        logging.error("config_os_prefix: Issue configuring required \
                       pre-infra on Openstack - images, flavors, etc")
        return 0, {}

def config_os_networks(self):
    '''
    This procedure will walk through the self.topo['networks'] list and
    configure all tenant and provider networks inside Openstack.
    '''
    try:
        net_list = self.topo['network']
        neutron = self.os['clients']['neutron']['client'] 
        for net in net_list:
            net_name = net['tenant_net_name']
            tenant_cidr = net['tenant_cidr'] 
            edge_list = net['edge_list']
            
            # Configure the 'tenant' VXLAN network in Openstack 
            body = {
                    'name': net_name,
                    'port_security_enabled': OSPRECONFIG.port_security,
                    'shared': 'True'
                    #'provider:network_type': 'vxlan',
                    #'provider:segmentation_id': 
                    #'provider:physical_network': OSBRIDGEMAPPING.OS_PHYSICAL_NET
                    } 
            out = neutron.create_network({'network':body})
            net.os['tenant']=out 
            net.os['tenant_id'] = out.id
    except:
        pass
            


#OBdef config_os_network(client, type, topo):
#    try:
#        if type == 'tenant': 
#            body = {
#                    'name': topo 
#                   } 
#
#        elif type == 'provider':
#            body = 






