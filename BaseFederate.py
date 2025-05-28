#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 14:53:29 2025

@author: Mohsen
"""

import argparse
import yaml
import helics as h
import json
from FederateConfig import FederateConfig
from TimingUtilities import apply_timing_configs  
from FlagUtilities import apply_flag_configs ,print_changed_flags
from abc import ABC, abstractmethod



class BaseFederate(ABC):
    def __init__(self, config_file, loglevel="warning"):
        self.config = self.load_config(config_file)
        self.config["log_level"] = loglevel
        
        json_string = json.dumps(self.config) 
        data_dict = json.loads(json_string)
        self.federate_config = FederateConfig(**data_dict)
        
        self.fed, self.publications, self.subscriptions, self.endpoints = self.create_federate(self,self.federate_config)
        print_changed_flags(self.fed)

    @staticmethod
    def load_config(yaml_file):
        with open(yaml_file, 'r') as f:
            config = yaml.safe_load(f)
        return config
        

    @staticmethod
    def create_federate(self,config: FederateConfig):
        # Create Federate Info object
        fedinfo = h.helicsCreateFederateInfo()
        h.helicsFederateInfoSetCoreName(fedinfo, config.name)
        
        core_type_mapping = {
            "zmq": h.helics_core_type_zmq,
            "tcp": h.helics_core_type_tcp,
            "udp": h.helics_core_type_udp,
            "ipc": h.helics_core_type_ipc,
            "inproc": h.helics_core_type_inproc,
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
        
            
        if self.__class__.__name__ == "EventDrivenType":
            h.helicsFederateInfoSetFlagOption(fedinfo, h.HELICS_FLAG_UNINTERRUPTIBLE, False)
        
        
        # Create value federate
        fed = h.helicsCreateValueFederate(config.name, fedinfo)
        
        period_from_fed = h.helicsFederateGetTimeProperty(fed, h.HELICS_PROPERTY_TIME_PERIOD)
        offset_from_fed = h.helicsFederateGetTimeProperty(fed, h.HELICS_PROPERTY_TIME_OFFSET)
        
        delta_from_fed = h.helicsFederateGetTimeProperty(fed, h.HELICS_PROPERTY_TIME_DELTA)
        lag_from_fed = h.helicsFederateGetTimeProperty(fed, h.HELICS_PROPERTY_TIME_RT_LAG)
        lead_from_fed = h.helicsFederateGetTimeProperty(fed, h.HELICS_PROPERTY_TIME_RT_LEAD)
        tolerance_from_fed = h.helicsFederateGetTimeProperty(fed, h.HELICS_PROPERTY_TIME_RT_TOLERANCE)
        input_delay_from_fed = h.helicsFederateGetTimeProperty(fed, h.HELICS_PROPERTY_TIME_INPUT_DELAY)
        output_delay_from_fed = h.helicsFederateGetTimeProperty(fed, h.HELICS_PROPERTY_TIME_OUTPUT_DELAY)

        print(f"*********************************************************************************")        
        print(f"***************** summary of configurations ********************")        
        
        print('period', period_from_fed)
        print('offset', offset_from_fed)
        print('delta', delta_from_fed)
        print('lag', lag_from_fed)
        print('lead', lead_from_fed)        
        print('tolerance', tolerance_from_fed)
        print('input_delay', input_delay_from_fed)
        print('output_delay', output_delay_from_fed)        

        
        # Register publications if they exist
        publications = {}
        if config.publications is not None:
            for pub in config.publications:
                pub_name = config.name + "/" + pub['key']
                publications[pub['key']] = h.helicsFederateRegisterGlobalTypePublication(
                    fed, pub_name, pub['type'], pub.get("unit", ""))
                
                pubType = pub['type']
                unit = pub.get("unit", "")                
                print(f'publishes {pub_name} type {pubType} unit {unit}', )
                
        # Register subscriptions if they exist
        subscriptions = {}
        if config.subscriptions is not None:
            for sub in config.subscriptions:
                subscriptions[sub["key"]] = h.helicsFederateRegisterSubscription(
                    fed, sub["key"], sub.get("unit", ""))
                
                key = sub["key"]
                unit = sub.get("unit", "")
                print(f'subscribes {key} unit {unit}', )
        
        # Register endpoints if they exist
        endpoints = {}
        if config.endpoints is not None:
            for ep in config.endpoints:
                endpoints[ep["name"]] = h.helicsFederateRegisterEndpoint(fed, ep["name"], ep.get("type", ""))
                
                ep = ep["name"]
                epType = ep.get("type", "")
                print(f'endpoint {ep} type {epType}', )
                
        
        return fed, publications, subscriptions, endpoints

    @abstractmethod
    def run_federate(self):
        pass

    def execute(self):
        try:
            self.run_federate()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            h.helicsFederateDestroy(self.fed)


def main(federate_class):
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", help="YAML configuration file for the federate")
    parser.add_argument("--loglevel", default="warning", help="Log level for the federate")
    args = parser.parse_args()
    
    federate = federate_class(args.config_file, args.loglevel)
    federate.execute()


if __name__ == "__main__":
    # This allows the base class file to be run directly for testing with a specific federate class
    # In normal use, you would run the specific federate files instead
    from BatteryFederate import BatteryFederate
    main(BatteryFederate)