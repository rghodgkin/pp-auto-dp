#!/usr/bin/env python
# encoding: utf-8

import logging
import pdb
import time
import re

def os_create_tenant_net(neutron, name, **kwargs):
    '''
    This Openstack function will configure a vxlan network.
            name = name assigned inside Openstack
    '''
    
    try:
        
        if kwargs.has_key('port_security'): 

            if str(kwargs['port_security']).lower() == "true":
                ps = 'True' 
            else:
                ps = 'False'
        if kwargs.has_key('shared'):
            if kwargs['shared'].lower() == "false":
                share = 'False'
            else:
                share = 'True' 
        body = {
            'name': name,
            'port_security_enabled': ps,
            'shared': 'True'
        }

        out = neutron.create_network({'network':body}) 
        return 1, out

    except:
        logging.error("os_create_tenantnet failed for network %s" % name)
        return 0, {}


def os_create_provider_net(neutron, name, phys_net, seg_id, **kwargs):
    '''
    This Openstack function will configure a provider network.  
            name = name assigned inside Openstack
            phys_net = bridge_mapping tag on compute node
            seg_id = vlan id to use for provider facing L2 network
    '''

    try:
        if kwargs.has_key('port_security'):
            if kwargs['port_security'] == 1:
                ps = 'True'
            else:
                ps = 'False'
        if kwargs.has_key('shared'):
            if kwargs['shared'].lower() == "false":
                share = 'False'
            else:
                share = 'True'

        in_body = {
                     'name': name,
                     'port_security_enabled': ps,
                     'shared': 'True',
                     'provider:network_type': 'vlan',
                     'provider:segmentation_id': seg_id,
                     'provider:physical_network': phys_net
                  }

        body_net = {
                     'network' : in_body
                   }
        out = neutron.create_network(body=body_net)
        return 1, out

    except:
        logging.error("os_create_provider failed for network %s" % name)
        return 0, {}


def os_create_subnet(neutron, name, net_id, cidr, **kwargs):
    '''
    This Openstack function will configure a provider network.
            name = name assigned inside Openstack
            net_id = Network ID to attach subnet to
            cidr = IP subnet/mask to create subnet with

            kwargs:
              enable_dhcp=True|False
              gateway_ip=x.x.x.x
    '''

    try:

        in_body_subnet = {
                           'name': name,
                           'network_id': net_id,
                           'cidr': cidr,
                           'ip_version':4
                         }

        body_subnet = {
                        'subnets':[
                                    in_body_subnet
                                  ]
                      }
        if kwargs.has_key('enable_dhcp'):
            if kwargs['enable_dhcp'] == 1:
                body['enable_dhcp'] = 'True'
            else:
                body['enable_dhcp'] = 'False'

        if kwargs.has_key('gateway_ip'):
            body['gateway_ip'] = kwargs['gateway_ip']
        
        out = neutron.create_subnet(body=body_subnet)
        return 1, out

    except:
        logging.error("os_create_subnet failed for network %s" % name)
        return 0, {}

def os_create_port(neutron, name, server_id, net_id, **kwargs):
    '''
    This Openstack function will create a port on specified network:
            name = name assigned inside Openstack
            server_id = server device to connect port
            net_id = Network ID to attach subnet to

            kwargs:
               None
    '''

    try:

        in_body = {
                      'admin_state_up': True, 
                      'name': name,
                      'device_id': server_id,
                      'network_id': net_id
                  }

        body = {
                  'port':[
                              in_body
                         ]
               }

        out = neutron.create_port(body=body)
        return 1, out

    except:
        logging.error("os_create_port failed for network %s" % name)
        return 0, {}

def os_create_server(nova, name, image, flavor, net_list, **kwargs):
    '''
    This Openstack function will create a new server using the given
    parameters
           
    '''

    try:

        server_str = "name, image, flavor"

        out = nova.servers.create(server_str) 

        time.sleep(5)

    except:
        logging.error("os_create_server failed for server %s" % name)
        return 0, {}

def os_apply_port_qos(neutron, qos_policy_name, port_ip):
    '''
    This procedure will apply the given qos policy to the given port inside 
    Openstack
    '''

    out = neutron.list_qos_policies()
    for policy in out['policies']:
        if policy['name'] == qos_policy_name:
            qos_policy_id = policy['id']
            break

    out = neutron.list_ports()
    for port in out['ports']:
        if re.search(str(port_ip), str(port['fixed_ips'])):
                port_id = port['id']

    # Execute OS command to apply the qos policy
    neutron.update_port(port_id, {'port': {'qos_policy_id':qos_policy_id}})

    return 1, {}








