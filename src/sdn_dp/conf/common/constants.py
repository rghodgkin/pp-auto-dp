import os

class TopoTemps(object):
    sdn = {'name':'', 'network':[], 'other':''}
    network = {'name':'', 'tenant_net_name':'', 'tenant_cidr':'', 'edge_list':[], \
            'os_data':{}}
    netrouter = {'type':'netrouter', 'name':'', 'engine':'', 'tenant_net_name':'', \
            'tenant_net':'', 'tenant_ip':'', 'tenant_mac': '', 'os_data':{}}
    #network = {'name':'', 'sdn_description':'', 'sdn_account': '', \
    #           'sdn_network_type': '', 'sdn_zone': '', 'edge_list':[]}
    cloud = {'name':'', 'cloud_provider':'', 'engine':'', 'physical_net':'', \
            'segment_id':'', 'tenant_net_name':'', 'tenant_net':'', 'tenant_ip':'', \
            'tenant_mac':'', 'provider_net_name': '', 'provider_net':'', \
            'provider_ip':'', 'provider_mac':'', 'traffic_state':0, \
            'os_data':{}, 'type':'cloud'}
    #cloud = {'name':'', 'sdn_description':'', 'sdn_network':'', \
    #         'sdn_cloud_provider':'', 'aws_cloud_region':'', \
    #         'sdn_cloud_location':'', 'aws_cloud_account':'', \
    #         'IPv4_CIDR_block':'', 'type':'cloud'} 
    site = {'type':'site', 'name':'', 'engine':'', 'tenant_net_name':'', \
            'tenant_net':'', 'tenant_ip':'', 'tenant_mac':'', 'vpn_net':'', 'os_data':{}}
    #site = {'name':'', 'sdn_description':'', \
    #        'sdn_network':'', 'sdn_zone':'', 'type':'site'}
    mobile = {'type':'mobile', 'name':'', 'engine':'', 'mobile_net':'', 'os_data':{}}
    #mobile = {'name':'', 'sdn_description':'', \
    #        'sdn_network':'', 'sdn_zone':'', 'type':'mobile'}

class SDNVLAN(object):
    AWS_VLAN_START = 160
    AWS_VLAN_MAX = 199 
    GOOGLE_VLAN_START = 210
    GOOGLE_VLAN_MAX = 249

class SDNCIDR(object):
    OS_TENANT_IP_START = '10.1.0.0/16'
    OS_TENANT_PREFIX = 24
    AWS_PROVIDER_IP_START = '168.0.0.0/16'
    AWS_PROVIDER_PREFIX = 24
    GOOGLE_PROVIDER_IP_START = '169.0.0.0/16'
    GOOGLE_PROVIDER_PREFIX = 24

class OSBRIDGEMAPPING(object):
    OS_PHYSICAL_NET = 'vlan'
           
class OSPRECONFIG(object):
    images = [
#               {'name':'image_netrouter', 'path':'/tmp/images/vpn-sgw-image-ubuntu18.04-0.2.1.tar.gz', \
#            'container_format':'bare', 'disk_format':'raw'},
               {'name':'image_cloud', 'path':'/tmp/images/vpn-sgw-image-ubuntu18.04-0.2.1.tar.gz', \
            'container_format':'bare', 'disk_format':'raw'},
#               {'name':'image_site', 'path':'/tmp/images/vpn-sgw-image-ubuntu18.04-0.2.1.tar.gz', \
#            'container_format':'bare', 'disk_format':'raw'}
             ]
    flavors = [
               {'name':'c1.small', 'vcpus':1, 'ram':'1024', 'disk':'1'}
              ]
    port_security = 'False'

class OSCLOUDIMAGE(object):
    netrouter = 'ubuntu-18.04-vpn'
    cloud = 'ubuntu-18.04-vpn'
    site = 'ubuntu-18.04-vpn'
    mobile = 'ubuntu-18.04-vpn'

class OSCLOUDFLAVOR(object):
    netrouter = 'c1.small'
    cloud = 'ubuntu-18.04-vpn'
    site = 'ubuntu-18.04-vpn'
    mobile = 'ubuntu-18.04-vpn'

class TRAFFICINFO(object):
    # The below will configure external traffic gen ints with x.x.x.200/24
    EXTERNAL_IP = 200
    EXTERNAL_IP_MASK = 24




    
