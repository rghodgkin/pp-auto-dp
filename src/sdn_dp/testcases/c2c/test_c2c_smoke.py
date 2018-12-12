#!/usr/bin/env python
# encoding: utf-8

import pytest
import logging
import time
import pdb
import random
import pprint
import sdn_dp.conf.common.sdn_utils as sdn_utils

class TestC2CTraffic:

    @classmethod
    def before_class(cls, common):
        logging.info("inside before_class")
        pass

    @classmethod
    def after_class(cls, common):
        logging.info("inside after_class")
        pass
        #pdb.set_trace()
        #if common.topo['other']['traffic'] == 'external':
        #    for cloud in common.config['devices']['traffic'].keys():
        #      sdn_utils.traffic_stop_iperf3_all(common.config['devices']['traffic'][cloud]['engine_ip'])

    def before_each_func(self, common):
        logging.info("inside before_each_func")
        pass

    def after_each_func(self, common):
        logging.info("inside after_each_func")
        pass


    def test_c2c_dp_traffic_step(self, common, dp_setup):
        '''
        This testcase will run stepped traffic starting with 'base' number of nets
        and incrementing in steps as per 'num_nets_step' until reaching the final
        of 'num_nets'.
                 Variables:
                             num_nets = Total end number of nets to run traffic
                             base = Starting point from which to take first data point
                             num_nets_step = Number of nets to step up from base until
                                              reaching 'num_nets' total
        '''
        logging.info("Executing testcase: test_c2c_dp_traffic_step")
        print("dp_setup setup_status is: %s" % dp_setup.setup_status)

        ############### MANUALLY CONFIG THESE VALUES ##############
        num_nets = 4
        base = 2 
        num_nets_step = 1
        time_sleep = 10
        ###########################################################

        # Set some needed variable values
        result_klist = {}
        high_cntr = int(base)
        num_nets_step_cnt = (num_nets - base) / num_nets_step
        net_list = random.sample(range(len(common.sdn)), num_nets)
        net_cntr = 0

        # Verify that all nets are up prior to starting test
        pass_flag = 1
        gw_fail_list = []
        for net in common.sdn:
            out = sdn_utils.verify_gws_up(net)
            if out[0] == 0:
                pass_flag = 0
                gw_fail_list.append(out[1]['stopped'])

        if pass_flag == 0:
            logging.error("The following gws are in STOPPED state: %s" % gw_fail_list)
            pdb.set_trace()
        elif pass_flag == 1:
            logging.info("All gateways are in UP state, proceeding with test...")

        pdb.set_trace()
        # Test
#        import sdn_dp.conf.os.os_lib as os_lib 
#        neutron = common.os['clients']['neutron']['client']
#        net0=common.sdn[0]
#        cgw1 = net0.edge_cloud_list[0]
#        port_ip=cgw1.topo['provider_ip']
#        os_lib.os_apply_port_qos(neutron, 'bw-limiter', port_ip)

        # Dump base system utilization prior to starting traffic
        cgw1 = common.sdn[0].edge_cloud_list[0]
        cgw2 = common.sdn[0].edge_cloud_list[1]
        result_klist[0] = {}
        result_klist[0][cgw1.topo['engine']] = sdn_utils.return_sys_util(cgw1)
        #result_klist[0][cgw2.topo['engine']] = sdn_utils.return_sys_util(cgw2)

        # Configure traffic for Base number of nets
        for cnt in range(0, base):
            net = common.sdn[net_list[net_cntr]]
            cgw1 = net.edge_cloud_list[0]
            cgw2 = net.edge_cloud_list[1]
            cgw1.traffic_start(cgw2.name)
            net_cntr += 1

        logging.info("Sleeping for %s seconds to soak traffic..." % time_sleep)
        time.sleep(time_sleep)

        logging.info("Recording results for %s number of cloud networks" \
                      % (net_cntr))
        result_klist[net_cntr] = {}
        result_klist[net_cntr][cgw1.topo['engine']] = sdn_utils.return_sys_util(cgw1)
        #result_klist[net_cntr + 1][cgw2.topo['engine']] = sdn_utils.return_sys_util(cgw2)

        print("### Engine utilization stats with %s networks for: %s ###" % (net_cntr, cgw1.topo['engine']))
        pprint.pprint(result_klist[net_cntr][cgw1.topo['engine']])
        #print("### Engine utilization stats with %s networks for: %s ###" % (net_cntr, cgw2.topo['engine']))
        #pprint.pprint(result_klist[net_cntr + 1][cgw2.topo['engine']])

        for cntx in range(0, num_nets_step_cnt):
            for cnty in range(0, num_nets_step):
                net = common.sdn[net_list[net_cntr]]
                cgw1 = net.edge_cloud_list[0]
                cgw2 = net.edge_cloud_list[1]
                cgw1.traffic_start(cgw2.name)
                net_cntr += 1
            logging.info("Sleeping for %s seconds to soak traffic..." % time_sleep)
            time.sleep(time_sleep)
    
            logging.info("Recording results for %s number of cloud networks" \
                          % (net_cntr))
            result_klist[net_cntr] = {}
            result_klist[net_cntr][cgw1.topo['engine']] = sdn_utils.return_sys_util(cgw1)
            #result_klist[net_cntr + 1][cgw2.topo['engine']] = sdn_utils.return_sys_util(cgw2)
    
            print("### Engine utilization stats with %s networks for: %s ###" % (net_cntr, cgw1.topo['engine']))
            pprint.pprint(result_klist[net_cntr][cgw1.topo['engine']])
            #print("### Engine utilization stats with %s networks for: %s ###" % (net_cntr, cgw2.topo['engine']))
            #pprint.pprint(result_klist[net_cntr + 1][cgw2.topo['engine']])


        # Print the entire result_klist dict
        print("### Entire dictionary result for engine utilization ###")
        pprint.pprint(result_klist)

        # Loop through and stop traffic for all nets
        net_cntr = 0
        for cnt in range(net_cntr, num_nets):
            net = common.sdn[net_list[net_cntr]]
            cgw1 = net.edge_cloud_list[0]
            cgw2 = net.edge_cloud_list[1]
            logging.info("Stopping bidirectional traffic for %s <-> %s" \
                          % (cgw1.name, cgw2.name))
            cgw1.traffic_stop(cgw2.name)
            net_cntr += 1

        assert 1 


#    def test_c2c_dp_traffic_bg(self, common, dp_setup):
#        logging.info("Executing testcase: test_c2c_dp_traffic_bg")
#        print("dp_setup setup_status is: %s" % dp_setup.setup_status)
#
#        # Run basic traffic test from first cloud gateway
#        #  in each tenant network
#        result_all = 1
#        for net in common.sdn:
#            cgw1 = net.edge_cloud_list[0]
#            cgw2 = net.edge_cloud_list[1]
#            # Default traffic time is 10,000 seconds
#            result = cgw1.traffic_start(cgw2.name)
#
#            if result == 1:
#                logging.info("Traffic setup passed for net %s" % net.topo['name'])
#            else:
#                logging.info("Traffic setup failed for net %s" % net.topo['name'])
#                result_all = 0
#        
#        logging.info("Sleeping for 300 seconds to let traffic soak...")
#        time.sleep(300)
#
#        # Tear down traffic
#        for net in common.sdn:
#            cgw1 = net.edge_cloud_list[0]
#            cgw2 = net.edge_cloud_list[1]
#            # Default traffic time is 10,000 seconds
#            result = cgw1.traffic_stop(cgw2.name)
#
#        if result_all == 1:
#            info.logging("Background TCP bi-directional traffic testcase passed")
#            assert 1
#        else:
#            info.logging("Background TCP bi-directional traffic testcase failed")
#            assert 0

#    def test_c2c_dp_traffic_basic(self, common, dp_setup):
#        logging.info("inside testcase: test_c2c_dp_ping")
#        print("dp_setup setup_status is: %s" % dp_setup.setup_status)
#
#        # Run basic traffic test from first cloud gateway
#        #  in each tenant network
#        result_all = 1
#        for net in common.sdn:
#            cgw1 = net.edge_cloud_list[0]
#            cgw2 = net.edge_cloud_list[1]
#            # traffic_time=x
#            result = cgw1.traffic_run(cgw2.name, traffic_time=10)
#
#            if result == 1:
#                logging.info("Traffic passed for net %s" % net.topo['name'])
#            else:
#                logging.info("Traffic failed for net %s" % net.topo['name'])
#                result_all = 0 
#
#        pdb.set_trace()
#        if result_all == 1:
#            info.logging("Basic TCP bi-directional traffic testcase passed")
#            assert 1
#        else:
#            info.logging("Basic TCP bi-directional traffic testcase failed")
#            assert 0
#


