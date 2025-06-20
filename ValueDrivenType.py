# -*- coding: utf-8 -*-
"""
Created on Wed Jun 07 16:40:30 2025

@author: Mohsen
"""

from BaseFederate import BaseFederate
import helics as h
from FederateConfig import TimingConfigs


class ValueDrivenType(BaseFederate):

    def run_federate(self):
        
        # Enter execution mode
        h.helicsFederateEnterExecutingMode(self.fed)
        
        timing_config = TimingConfigs(**self.federate_config.timing_configs)

        max_iterations = timing_config.int_max_iterations        

        requested_time = h.HELICS_TIME_MAXTIME
        
        granted_time = h.helicsFederateRequestTime(self.fed, requested_time)
        
        key, sub = next(iter(self.subscriptions.items()))
        
        # while h.helicsFederateGetState(self.fed) == h.HELICS_STATE_EXECUTION:
        while granted_time < max_iterations:

            
            print("*********************************************************************************")
            print(f"request time is {requested_time}")
            print(f"granted time is {granted_time}")            
            
            while h.helicsInputIsUpdated(sub):
                value = h.helicsInputGetDouble(sub)
                print(f"{self.federate_config.name}: Received {key} = {value} at {granted_time}")
                self.process_event(key, value, granted_time) 
                

            granted_time = h.helicsFederateRequestTime(self.fed, requested_time)
                              
  
    
    def process_event(self, key, value, time):
        """Override this method to handle subscription events"""
        # Publish any outputs if needed
        if self.publications:
            for key, pub in self.publications.items():
                value = self.generate_output(key, time)
                h.helicsPublicationPublishDouble(pub, value)
                print(f"{self.federate_config.name}: Published {key} = {value} at time {time}")
    
    def generate_output(self, publication_key, time):
        """Override this method to generate output values when events occur"""
        return time * 0.1  # Default implementation
            


if __name__ == "__main__":
    from BaseFederate import main
    main(ValueDrivenType)