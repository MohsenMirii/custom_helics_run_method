# -*- coding: utf-8 -*-
"""
Created on Wed May 21 16:40:30 2025

@author: Mohsen
"""

from BaseFederate import BaseFederate
import helics as h
from FederateConfig import TimingConfigs



class EventDrivenType(BaseFederate):
    def run_federate(self):
        
        # Set the uninterruptible flag
        #h.helicsFederateInfoSetFlagOption(self.fed, h.HELICS_FLAG_UNINTERRUPTIBLE, True)
        
        # Enter execution mode
        h.helicsFederateEnterExecutingMode(self.fed)
        
        timing_config = TimingConfigs(**self.federate_config.timing_configs)
        total_time = timing_config.int_max_iterations
        #period = timing_config.time_period
        period = 0.1
        granted_time = 0.0
        start_time = 0.0
        requested_time=0.0
        real_period = timing_config.real_period
        
        granted_time = h.helicsFederateRequestTime(self.fed, requested_time)
        requested_time = granted_time
        
        
        
        while start_time < total_time:
            
            print(f"*********************************************************************************")        
            print(f"***************** iteration with real period is {granted_time} ********************")        
            
            while h.helicsInputIsUpdated(sub):
                
                
            
            
            # Always request time advancement to maintain time synchronization
            #requested_time = min(granted_time + period, total_time)
            granted_time = h.helicsFederateRequestTime(self.fed, requested_time)
            requested_time = granted_time
            print(f"request time is {requested_time}")
            print(f"granted time is {granted_time}")
            
            # if granted_time > 3.0:
            #     raise Exception("Fake Exceptions to test its impact on the performance of other federates !")


            has_event = False

            # Check subscriptions for new data
            if self.subscriptions:
                for key, sub in self.subscriptions.items():
                    if h.helicsInputIsUpdated(sub):
                        has_event = True
                        value = h.helicsInputGetDouble(sub)
                        print(f"{self.federate_config.name}: Received event {key} = {value} at time {granted_time}")
                        # Process the event here
                        self.process_event(key, value, granted_time)
                        
            # Check endpoints for messages
            if self.endpoints:
                for name, ep in self.endpoints.items():
                    if h.helicsEndpointHasMessage(ep):
                        has_event = True
                        msg = h.helicsEndpointGetMessage(ep)
                        print(f"{self.federate_config.name}: Received message at {name} at time {granted_time}")
                        # Process the message here
                        self.process_message(name, msg, granted_time)
                        
            
            # Only advance time if we had an event or we're at time zero
            if has_event: # or granted_time == 0.0:
                # Publish any outputs if needed
                if self.publications:
                    for key, pub in self.publications.items():
                        value = self.generate_output(key, granted_time)
                        h.helicsPublicationPublishDouble(pub, value)
                        print(f"{self.federate_config.name}: Published {key} = {value} at time {granted_time}")
            else:
                # No events, wait for something to happen
                # We could add a small delay here to prevent busy waiting
                start_time += granted_time
                pass
            
            
            
            
    def process_event(self, key, value, time):
        """Override this method to handle subscription events"""
        pass
    
    def process_message(self, endpoint_name, message, time):
        """Override this method to handle endpoint messages"""
        pass
    
    def generate_output(self, publication_key, time):
        """Override this method to generate output values when events occur"""
        return 0.0  # Default implementation
            
            
           


if __name__ == "__main__":
    from BaseFederate import main
    main(EventDrivenType)