#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 14:53:29 2025

@author: Mohsen
"""

import argparse
import yaml
import helics as h
import time
import json
from FederateConfig import FederateConfig,ConnectionEndpoint,TimingConfigs
from TimingUtilities import apply_timing_configs  
from FlagUtilities import apply_flag_configs 
import logging
 

def load_config(yaml_file):
    with open(yaml_file, 'r') as f:
        config = yaml.safe_load(f)
        
    return config

def create_federate(config: FederateConfig):
    # Create Federate Info object
    fedinfo = h.helicsCreateFederateInfo()
    h.helicsFederateInfoSetCoreName(fedinfo, config.name)
    
    #h.helicsFederateInfoSetCoreTypeFromString(fedinfo, config.core_type)
    
    core_type_mapping = {
        "zmq": h.helics_core_type_zmq,
        "tcp": h.helics_core_type_tcp,
        "udp": h.helics_core_type_udp,
        "ipc": h.helics_core_type_ipc,
        "inproc": h.helics_core_type_inproc,
        # Add other core types as needed
    }
    if config.core_type.lower() in core_type_mapping:
        h.helicsFederateInfoSetCoreType(fedinfo, core_type_mapping[config.core_type.lower()])
    else:
        raise ValueError(f"Unsupported core type: {config.core_type}") 
    
    
    # Set logging level    
    log_level = config.log_level
    h.helicsFederateInfoSetIntegerProperty(fedinfo, h.HELICS_PROPERTY_INT_LOG_LEVEL, 
                                         getattr(h, f"HELICS_LOG_LEVEL_{log_level.upper()}"))
    
    # Apply timing configurations dynamically
    apply_timing_configs(fedinfo, config.timing_configs) 
    
    # Apply flag configurations dynamically
    apply_flag_configs(fedinfo, config.flags)
    
    # Create value federate
    fed = h.helicsCreateValueFederate(config.name, fedinfo)
    
    # Register publications if they exist
    publications = {}
    if config.publications is not None:
        for pub in config.publications:
            pub_name = config.name + "/" + pub['key']
            publications[pub['key'] ]= h.helicsFederateRegisterGlobalTypePublication(
            fed, pub_name, pub['type'], pub.get("unit", ""))
            
            
    
    # Register subscriptions if they exist
    subscriptions = {}
    if config.subscriptions is not None:
        for sub in config.subscriptions:
            subscriptions[sub["key"]] = h.helicsFederateRegisterSubscription(
                fed, sub["key"], sub.get("unit", ""))
    
    
    
    # Register endpoints if they exist
    endpoints = {}
    if config.endpoints is not None:
        for ep in config.endpoints:
            endpoints[ep["name"]] = h.helicsFederateRegisterEndpoint(fed, ep["name"], ep.get("type", ""))
    
    
    return fed, publications, subscriptions, endpoints


def run_federate(fed, config: FederateConfig, publications, subscriptions, endpoints):
    
    # Enter execution mode
    h.helicsFederateEnterExecutingMode(fed)
    
    timing_config = TimingConfigs(**config.timing_configs)

    total_time = timing_config.int_max_iterations  # simulation time in seconds
    period = timing_config.time_period  # time interval between updates    
    granted_time=0.0
    start_time=0.0
    real_period=timing_config.real_period
    request_time=0.0
    while start_time < total_time:

        # For publishers, publish values

        print(f"*********************************************************************************")        
        print(f"***************** iteration with real period is {start_time} ********************")        
        
        print(f"request time is {request_time}")
        print(f"granted time is {granted_time}")
        
        if publications:
            for key, pub in publications.items():
                value = start_time  # Simple example: publish the current time as value
                h.helicsPublicationPublishDouble(pub, value)
                print(f"{config.name}: Published {key} = {value} at time {start_time}")
        
        # For subscribers, get subscribed values
        if subscriptions:
            for key, sub in subscriptions.items():
                value = h.helicsInputGetDouble(sub)
                print(f"{config.name}: Received {key} = {value} at time {start_time}")
        
        # Request time advance
        request_time = granted_time + period
        granted_time = h.helicsFederateRequestTime(fed, request_time)
        start_time += real_period


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", help="YAML configuration file for the federate")
    parser.add_argument("--loglevel", default="warning", help="Log level for the federate")
    args = parser.parse_args()
    
    config = load_config(args.config_file)
    config["log_level"] = args.loglevel
        
    json_string = json.dumps(config) 
    
    # Convert back to dict if needed
    data_dict = json.loads(json_string)

    result = FederateConfig(**data_dict)

    fed, publications, subscriptions, endpoints = create_federate(result)
    
    try:
        run_federate(fed, result, publications, subscriptions, endpoints)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        h.helicsFederateDestroy(fed)

if __name__ == "__main__":
    main()