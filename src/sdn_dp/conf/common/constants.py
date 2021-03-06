import os

class TopoTemps(object):
    sdn = {'name':'', 'network':[], 'other':''}
    network = {'name':'', 'tenant_net_name':'', 'tenant_cidr':'', 'edge_list':[], \
            'os_data':{}}
    netrouter = {'type':'netrouter', 'name':'', 'engine':'', 'tenant_net_name':'', \
            'tenant_net':'', 'tenant_ip':'', 'tenant_mac': '', 'os_data':{}, \
            'instance_name':''}
    #network = {'name':'', 'sdn_description':'', 'sdn_account': '', \
    #           'sdn_network_type': '', 'sdn_zone': '', 'edge_list':[]}
    cloud = {'name':'', 'cloud_provider':'', 'engine':'', 'physical_net':'', \
            'segment_id':'', 'tenant_net_name':'', 'tenant_net':'', 'tenant_ip':'', \
            'tenant_mac':'', 'provider_net_name': '', 'provider_net':'', \
            'provider_ip':'', 'provider_mac':'', \
            'os_data':{}, 'type':'cloud', 'instance_name':''}
    #cloud = {'name':'', 'sdn_description':'', 'sdn_network':'', \
    #         'sdn_cloud_provider':'', 'aws_cloud_region':'', \
    #         'sdn_cloud_location':'', 'aws_cloud_account':'', \
    #         'IPv4_CIDR_block':'', 'type':'cloud'} 
    site = {'type':'site', 'name':'', 'engine':'', 'tenant_net_name':'', \
            'tenant_net':'', 'tenant_ip':'', 'tenant_mac':'', 'vpn_net':'', \
            'os_data':{}, 'instance_name':''}
    #site = {'name':'', 'sdn_description':'', \
    #        'sdn_network':'', 'sdn_zone':'', 'type':'site'}
    mobile = {'type':'mobile', 'name':'', 'engine':'', 'mobile_net':'', \
              'os_data':{}, 'instance_name':''}
    #mobile = {'name':'', 'sdn_description':'', \
    #        'sdn_network':'', 'sdn_zone':'', 'type':'mobile'}

class SDNVLAN(object):
    AWS_VLAN_START = 150
    AWS_VLAN_MAX = 349
    GOOGLE_VLAN_START = 350
    GOOGLE_VLAN_MAX = 549

class SDNCIDR(object):
    OS_TENANT_IP_START = '198.18.0.0/16'
    OS_TENANT_PREFIX = 24
    AWS_PROVIDER_IP_START = '168.0.0.0/16'
    AWS_PROVIDER_PREFIX = 24
    GOOGLE_PROVIDER_IP_START = '169.0.0.0/16'
    GOOGLE_PROVIDER_PREFIX = 24

class OSBRIDGEMAPPING(object):
    OS_PHYSICAL_NET = 'us-ral-1a-vlan'

class OSSITEINFO(object):
    OS_NET_NAME = 'us-ral-1a-public-1'
    OS_NET_CIDR = '10.198.1.0/24'
           
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
    netrouter = 'controller'
    cloud = 'cloud_gateway'
    site = 'vpn_site_gateway'
    mobile = 'ubuntu-18.04-vpn'
    traffic = 'traffic'

class OSCLOUDFLAVOR(object):
    netrouter = 'm1.tiny'
    cloud = 'm1.tiny'
    site = 'm1.tiny'
    mobile = 'c1.small'
    traffic = 'c1.small'

class CLOUDPROVINFO(object):
    AWSDEFAULTBGPID = 7224
    PPDEFAULTBGPID = 394351 

class CLOUDCONFIGTEMPS(object):
    netrouter = 'create_cloud_config.j2'
    cloud = 'create_cloud_config.j2'
    site = 'create_cloud_config_vpn.j2'

class TRAFFICINFO(object):
    # The below will configure external traffic gen ints with x.x.x.200/24
    EXTERNAL_IP = 200
    EXTERNAL_IP_MASK = 24
    TRAFFIC_PASS_PERCENT = float(99)




    
