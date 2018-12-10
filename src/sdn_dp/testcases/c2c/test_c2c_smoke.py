#!/usr/bin/env python
# encoding: utf-8

import pytest
import logging
from time import sleep
import pdb
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
        pdb.set_trace()
        if common.topo['other']['traffic'] == 'external':
            for cloud in common.config['devices']['traffic'].keys():
              sdn_utils.traffic_stop_iperf3_all(common.config['devices']['traffic'][cloud]['engine_ip'])

    def before_each_func(self, common):
        logging.info("inside before_each_func")
        pass

    def after_each_func(self, common):
        logging.info("inside after_each_func")
        pass

    def test_c2c_dp_traffic_step(self, common, dp_setup):
        '''
        This testcase configures 50% of num_nets with bi-directional traffic,
         and then begins stepping by 'num_nets_step' up to 100%, logging system resources
         at each step.
        '''
        logging.info("Executing testcase: test_c2c_dp_traffic_step")
        print("dp_setup setup_status is: %s" % dp_setup.setup_status)

        pdb.set_trace()
        num_nets = len(common.sdn)
        time_sleep = 60

        if num_nets % 10  != 0:
            logging.error("Error: test_c2c_dp_traffic_step, num_nets MUST be divisible \
                           by 10")
            assert 0
        else:
            # Testcase will configure 50% of nets and then step up by 10%
            base = num_nets * .5
            num_nets_step = num_nets / 10
            result_klist = {}

        # Loop through increments of num_net_steps until 100%
        while net_cntr < high_cntr:
            for net in range(net_cntr, high_cntr):
                cgw1 = net.edge_cloud_list[0]
                cgw2 = net.edge_cloud_list[1]
                logging.info("Starting bidirectional traffic for %s <-> %s" \
                              % (cgw1.name, cgw2.name))
                sdn_utils.traffic_start_handler(cgw1, cgw2)
                time.sleep(3)
                net_cntr += 1
            time.sleep(time_sleep)
            logging.info("Recording results for %s number of cloud networks" \
                          % (net_cntr + 1)) 
            result_klist[net_cntr + 1] = {}
            result_klist[net_cntr + 1][cgw1.name] = sdn_utils.return_sys_util(cgw1)
            result_klist[net_cntr + 1][cgw2.name] = sdn_utils.return_sys_util(cgw2)

            pprint.pprint(result_klist[net_cntr + 1][cgw1.name])
            pprint.pprint(result_klist[net_cntr + 1][cgw2.name])

            high_cntr += num_nets_step

        # Loop through and stop traffic for all nets
        net_cntr = 0
        while net_cntr < high_cntr:
            cgw1 = net.edge_cloud_list[0]
            cgw2 = net.edge_cloud_list[1]
            logging.info("Stopping bidirectional traffic for %s <-> %s" \
                          % (cgw1.name, cgw2.name))
            sdn_utils.traffic_stop_handler(cgw1, cgw2)
            net_cntr += 1
            time.sleep(3)



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


