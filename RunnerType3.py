# -*- coding: utf-8 -*-
"""
Created on Mon Apr 21 21:21:28 2025

@author: Mohsen
"""


from BaseFederate import BaseFederate
import helics as h
from FederateConfig import TimingConfigs


class RunnerType3(BaseFederate):
    def run_federate(self):
        # Enter execution mode
        h.helicsFederateEnterExecutingMode(self.fed)
        
        timing_config = TimingConfigs(**self.federate_config.timing_configs)
        total_time = timing_config.int_max_iterations
        period = timing_config.time_period
        granted_time = 0.0
        start_time = 0.0
        request_time=0.0
        real_period = timing_config.real_period
        
        while start_time < total_time:
            
            print(f"*********************************************************************************")        
            print(f"***************** iteration with real period is {start_time} ********************")        
            
            print(f"request time is {request_time}")
            print(f"granted time is {granted_time}")
            
            # Federate-specific logic here
            request_time = granted_time + period
            granted_time = h.helicsFederateRequestTime(self.fed, request_time)
            
            if self.publications:
                for key, pub in self.publications.items():
                    value = start_time  # Your battery-specific value calculation
                    h.helicsPublicationPublishDouble(pub, value)
                    print(f"{self.federate_config.name}: Published {key} = {value} at time {start_time}")
            
            if self.subscriptions:
                for key, sub in self.subscriptions.items():
                    value = h.helicsInputGetDouble(sub)
                    print(f"{self.federate_config.name}: Received {key} = {value} at time {start_time}")
            
            start_time += real_period


if __name__ == "__main__":
    from BaseFederate import main
    main(RunnerType3)