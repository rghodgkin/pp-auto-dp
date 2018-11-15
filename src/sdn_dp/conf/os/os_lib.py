#!/usr/bin/env python
# encoding: utf-8

def os_create_tenant_net(neutron, name, **kwargs):
    '''
    This Openstack function will configure a vxlan network.
            name = name assigned inside Openstack
    '''

    try:
        if kwargs.has_key('port_security'): 
            if kwargs['port_security'].lower() == "true":
                ps = 'True' 
            else:
                ps = 'False'
        if kwargs.has_key('shared'):
            if kwargs['shared'].lower() == "false":
                share = 'False'
            else:
                share = 'True' 
        body = {
            'name': net_name,
            'port_security_enabled': OSPRECONFIG.port_security,
            'shared': 'True'
        }
        out = neutron.create_network({'network':body}) 
        return 1, out

    except:
        logging.error("os_create_tenant failed for network %s" % name)
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
            if kwargs['port_security'].lower() == "true":
                ps = 'True'
            else:
                ps = 'False'
        if kwargs.has_key('shared'):
            if kwargs['shared'].lower() == "false":
                share = 'False'
            else:
                share = 'True'
        body = {
            'name': net_name,
            'port_security_enabled': OSPRECONFIG.port_security,
            'shared': 'True'
        }
        out = neutron.create_network({'network':body})
        return 1, out

    except:
        logging.error("os_create_tenant failed for network %s" % name)
        return 0, {}





