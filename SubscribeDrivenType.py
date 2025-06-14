# -*- coding: utf-8 -*-
"""
Created on Wed Jun 07 16:40:30 2025

@author: Mohsen
"""

from BaseFederate import BaseFederate
import helics as h
from FederateConfig import TimingConfigs
from multiprocessing import Pool


class SubscribeDrivenType(BaseFederate):

    def run_federate(self):
        
        # Enter execution mode
        h.helicsFederateEnterExecutingMode(self.fed)
        
        timing_config = TimingConfigs(**self.federate_config.timing_configs)
        max_iterations = timing_config.int_max_iterations
        granted_time = 0.0
        requested_time = 0.0
        granted_time = h.helicsFederateRequestTime(self.fed, requested_time)
        start_time = 0.0
        small_increasement_step = 0.5
        
        while granted_time < max_iterations:
            
            print(f"***************** iteration {granted_time} ********************")
            print(f"request time is {requested_time}")
            print(f"granted time is {granted_time}")            
           
            # Reset event flag at start of each iteration
            has_event = False

            # Check subscriptions for updates
            if self.subscriptions:
                for key, sub in self.subscriptions.items():
                    if h.helicsInputIsUpdated(sub):
                        has_event = True
                        value = h.helicsInputGetDouble(sub)
                        print(f"{self.federate_config.name}: Received {key} = {value} at {granted_time}")
                        # Process event immediately (no parallel pool needed for event-driven)
                        self.process_event(key, value, granted_time)           
            
            
            # Event-driven time request logic
            if has_event or granted_time == 0.0:            
                # Advance time
                granted_time = h.helicsFederateRequestTime(self.fed, requested_time)            
                requested_time = granted_time
            else:
                start_time = start_time + small_increasement_step
                requested_time = start_time
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
    main(SubscribeDrivenType)