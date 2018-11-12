#!/usr/bin/env python
# encoding: utf-8

import os
import keystoneclient.v2_0.client as kclient
import pdb

def return_keystone_creds(username, passwd, auth_url, tenant):
    d = {} 
    d['username'] = username
    d['password'] = passwd
    d['auth_url'] = auth_url
    d['tenant_name'] = tenant
    return d

def return_keystone_token(username, passwd, auth_url, tenant):
    creds = return_keystone_creds(username, passwd, auth_url, tenant)
    keystone = kclient.Client(**creds)
    print("keystone token = %s" % keystone.auth_token)
    return keystone.auth_token




