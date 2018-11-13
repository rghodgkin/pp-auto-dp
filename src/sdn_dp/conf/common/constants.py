import os

class TopoTemps(object):
    sdn = {'name':'', 'network_list':[]}
    network = {'name':'', 'tenant_net_name':'', 'tenant_cidr':'', 'edge_list':[], \
            'os_data':{}}
    netrouter = {'name':'', 'engine':'', 'tenant_ip':'', 'os_data':{}}
    #network = {'name':'', 'sdn_description':'', 'sdn_account': '', \
    #           'sdn_network_type': '', 'sdn_zone': '', 'edge_list':[]}
    cloud = {'name':'', 'cloud_provider':'', 'engine':'', 'physical_net':'', \
            'segment_id':'', 'tenant_ip':'', 'provider_net':'', 'provider_ip':'', \
            'os_data':{}}
    #cloud = {'name':'', 'sdn_description':'', 'sdn_network':'', \
    #         'sdn_cloud_provider':'', 'aws_cloud_region':'', \
    #         'sdn_cloud_location':'', 'aws_cloud_account':'', \
    #         'IPv4_CIDR_block':'', 'type':'cloud'} 
    site = {'name':'', 'engine':'', 'vpn_net':'', 'os_data':{}}
    #site = {'name':'', 'sdn_description':'', \
    #        'sdn_network':'', 'sdn_zone':'', 'type':'site'}
    mobile = {'name':'', 'engine':'', 'mobile_net':'', 'os_data':{}}
    #mobile = {'name':'', 'sdn_description':'', \
    #        'sdn_network':'', 'sdn_zone':'', 'type':'mobile'}

class SDNVLAN(object):
    AWS_VLAN_START = 150
    AWS_VLAN_MAX = 199 
    GOOGLE_VLAN_START = 200
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
           
class SDNNetTrans(object):
    aws = {'us-east-1':'Ashburn, VA', \
           'us-west-1':'San Jose, CA', \
           'x':'Seattle, WA'}

class SDNCloudTrans(object):
    aws = {'us-east-2':'US East (Ohio)', \
           'us-east-1':'AWS US-East N Virginia', \
           'us-west-1':'AWS US-West N California', \
           'us-west-2':'AWS US-West Oregon'}  

class SDNSiteTrans(object):
    aws = {'us-east-1':'Ashburn, VA', \
           'us-west-1':'San Jose, CA', \
           'x':'Seattle, WA'} 

class AwsVpc(object):
    VPC_SUP_IP = '10.0.0.0'
    VPC_SUP_MASK = '8'
    VPC_SUB_PREFIX = '16'

class AwsVgw(object):
    AWS_BGP_ASN = 7224 

