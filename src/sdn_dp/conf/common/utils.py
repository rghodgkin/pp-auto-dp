#!/usr/bin/python

import yaml
import pdb
import os
import logging
import subprocess
import ipaddress

def import_yaml_to_dict(file):
    """
        This function takes a filename in yaml format and returns
         it as a dict type
    """
    try:
        f = open(file)
        data = yaml.safe_load(f)

    except:
        logging.error("import_yaml_to_dict: Issues importing yaml file")
        return 0, {}

    return 1, data 

def return_ip_subnets(network, newprefix, **kwargs):
    """
    This function will take an IP network and newprefix as inpus 
    and return all subnets as per the mask specified
         network = 10.0.0.0/16  (assumes string input)
         newprefix = 24   
         Arguments:
             skip_zero=True|False
    """
    return_list = []
    uni_net = unicode(network, "utf-8")
    newprefix = int(newprefix)
    net = ipaddress.ip_network(uni_net)
    for item in net.subnets(new_prefix=newprefix):
        return_list.append(item.with_prefixlen)
    return_list.reverse()
    if kwargs.has_key('skip_zero'):
        if kwargs['skip_zero'] == True:
            return_list.pop() 
            return return_list

    return return_list


def ssh_exec(host, command, **kwargs):
    """
    This function executes a basic ssh command based on the ther
    arguments provided.
          host = x.x.x.x or hostname
          command = string command to execute
          user = user other than default
          key = path to non-default private ssh key

    """
    cmd = "ssh "
    if kwargs.has_key('key'):
        cmd += '-i %s ' % kwargs['key']
    if kwargs.has_key('user'):
        cmd += '%s@' % kwargs['user']
    cmd += '%s %s' % (host, command)
    try:
        out = subprocess.check_output(cmd, shell=True)
        return 1, out
    except:
        return 0, {}
    return 





    
     

