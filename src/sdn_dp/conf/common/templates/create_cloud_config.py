#!/usr/bin/env python3
# This is just an example program that outputs a blob of json in place of what
# Kato will deliver as part of the ConfigDrive user-data at a future date.

import json
import yaml

isVpn = False
#isVpn = True
vpn_psk = {
        "ipsec": {
            #"ikeVersion": "1",
            "ikeVersion": "2",
            "authType": "psk",
            "vpnRouterIp": "169.0.1.200",
            "ike": {
                "encryption": "aes128gcm16",
                "prf": "prfsha256",
                "dhGroup": "ecp256"
                },
            "esp": {
                "encryption": "aes128gcm16",
                "dhGroup": "ecp256"
            },
            "authentication": {
                "psk": """4xBu7DZ7NsOZeY/3pVorhgaoRsP1GRqINq7RsK4T2ID/taMwap0/3K40EgbSCC9PIwTz2XhzoI7/bGyEABOmCQ=="""
                },
            "trafficSelectors": [
                {
                    "local": "10.6.6.0/24",
                    "remote": "172.16.1.0/24",
                    },
                {
                    "local": "10.6.5.0/24",
                    "remote": "172.16.1.0/24",
                    }
                ]
            },
        "nat": {
            "enabled": True,
            "sourceAddresses": [
                "100.101.0.1",
                "100.101.0.2"
                ],
            "blocks": [
                "100.101.1.0/20",
                "100.101.2.0/20"
                ],
            "mappings": [
                {
                    "nativeCidr": "10.6.6.2/32",
                    "natCidr": "100.101.1.2/32"
                    },
                {
                    "nativeCidr": "10.6.5.0/24",
                    "natCidr": "100.101.2.0/24"
                    }
                ]
            },
        "controllerIp": "198.18.0.3"
        }


aws_cloud = {
        "nat": {
            "enabled": False,
            "sourceAddresses": [
                "100.100.1.1",
                "100.100.1.2"
                ],
            "blocks": [
                "100.100.1.0/20",
                "100.100.5.0/20"
                ],
            "mappings": [
                {
                    "nativeCidr": "172.16.1.10/32",
                    "natCidr": "100.100.1.10/32"
                    },
                {
                    "nativeCidr": "172.16.1.0/24",
                    "natCidr": "100.100.1.0/24"
                    }
                ]
            },
        "controllerIp": "198.18.1.9",
        "ppAsn": "394351",
        "cloudGw": {
            "ip": "169.0.1.200",
            "asn": "7224",
            "bgpPasswd": "somekindofpassword"
            }
        }

# work around issue with yaml lib sorting a single dict and having runcmd come
# out before write_files which is the wrong order.
# An OrderedDict does not give the output I want. There are other solutions on
# the web that are more involved. This was just quicker and easier.
wf_dict = {
        'write_files': [
            {
                'encoding': 'b64',
                'owner': 'root:root',
                'path': '/tmp/katodata.json',
                'permission': '0644'
                }
            ]
        }
if isVpn:
    wf_dict['write_files'][0]['content'] = json.dumps(vpn_psk).encode('utf-8')
else:
    wf_dict['write_files'][0]['content'] = json.dumps(aws_cloud).encode('utf-8')

rc_dict = {
        'runcmd': [
            ['cloud-init-per', 'once', 'configure-net', '/usr/local/bin/configure']
            ]
        }

# write out a yaml file appropriate to use with OpenStack
# this yaml will write out a json blob that other scripts will use for
# configuring ipsec and frr, then will run the "configure" script that actually
# runs these commands. Order is important.
with open('./cloud-config.yml', "w") as kd:
    kd.write('#cloud-config\n')
    # the below replace is required because OpenStack's yaml will error on the
    # "!!binary" part
    kd.write(yaml.dump(wf_dict).replace("!!binary ", ""))
    kd.write(yaml.dump(rc_dict))
    kd.write('\n')