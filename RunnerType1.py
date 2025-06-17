#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 14:53:29 2025

@author: Mohsen
"""

from BaseFederate import BaseFederate
import helics as h
from FederateConfig import TimingConfigs
from FlagUtilities import apply_flag_configs 
import struct


class RunnerType1(BaseFederate):
    def run_federate(self):
        # Enter execution mode
        h.helicsFederateEnterExecutingMode(self.fed)
        
        timing_config = TimingConfigs(**self.federate_config.timing_configs)
        max_iterations = timing_config.int_max_iterations
        period = timing_config.time_period
        granted_time = 0.0
        start_time = 0.0
        request_time = 0.0
        real_period = timing_config.real_period
        
        while granted_time < max_iterations:
            
           
            # Federate-specific logic here
            request_time = granted_time + period
            granted_time = h.helicsFederateRequestTime(self.fed, request_time) 
            
            print(f"*********************************************************************************")        
            print(f"***************** iteration with real period is {granted_time} ********************")        
            
            print(f"request time is {request_time}")
            print(f"granted time is {granted_time}")            
            
            if self.subscriptions:
                for key, sub in self.subscriptions.items():
                    value = h.helicsInputGetDouble(sub)
                    print(f"{self.federate_config.name}: Received {key} = {value} at time {granted_time}")

            
            if self.publications:
                for key, pub in self.publications.items():
                    value = granted_time  # Your battery-specific value calculation
                    if granted_time % 5 == 0.0:
                        h.helicsPublicationPublishDouble(pub, value)
                        print(f"{self.federate_config.name}: Published {key} = {value} at time {granted_time}")
                    

            if self.endpoints:
                    for key, pub in self.endpoints.items():
                        if granted_time % 5 == 0.0:
                            value = granted_time
                            message = f"message: {value}" 
                            default_dest = h.helicsEndpointGetDefaultDestination(pub)
                            h.helicsEndpointSendMessageRaw(pub, default_dest, message)                    
                            print(f"{key}: send {value} to distination: {default_dest}  at time {granted_time}")
                   


if __name__ == "__main__":
    from BaseFederate import main
    main(RunnerType1)