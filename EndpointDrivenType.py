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
        
        # Enter execution mode
        h.helicsFederateEnterExecutingMode(self.fed)
        
        timing_config = TimingConfigs(**self.federate_config.timing_configs)
        max_iterations = timing_config.int_max_iterations
        #period = timing_config.time_period
        granted_time = 0.0
        start_time = 0.0        
        requested_time = start_time
        granted_time = h.helicsFederateRequestTime(self.fed, 10000)
        
        
        while start_time < max_iterations:
            
            print(f"*********************************************************************************")        
            print(f"***************** iteration {granted_time} ********************")        
            
            
            print(f"request time is {requested_time}")
            print(f"granted time is {granted_time}")
            
            # if granted_time > 3.0:
            #     raise Exception("Fake Exceptions to test its impact on the performance of other federates !")


            has_event = False

            # Check subscriptions for new data
            if self.subscriptions:
                for key, sub in self.subscriptions.items():
                    while h.helicsInputIsUpdated(sub):
                        has_event = True
                        value = h.helicsInputGetDouble(sub)                        
                        
                        print(f"{self.federate_config.name}: Received event {key} = {value} at time {granted_time}")                       
                        
                        # Process the event here
                        self.process_event(key, value, granted_time)
                        
            # Check endpoints for messages
            if self.endpoints:
                for name, ep in self.endpoints.items():
                    while h.helicsEndpointHasMessage(ep):
                        has_event = True
                        msg = h.helicsEndpointGetMessage(ep)
                        
                        # Extract message content
                        source = h.helicsMessageGetSource(msg)
                        data = h.helicsMessageGetString(msg)
                        time = h.helicsMessageGetTime(msg)
                        print(f"{self.federate_config.name}: Received {data} from {source} at {name} at time {time}")
                        # Process the message here
                        self.process_message(name, msg, granted_time)
            
            
            # Only advance time if we had an event or we're at time zero
            if has_event:
                # Publish any outputs if needed
                if self.publications:
                    for key, pub in self.publications.items():
                        value = self.generate_output(key, granted_time)
                        h.helicsPublicationPublishDouble(pub, value)
                        print(f"{self.federate_config.name}: Published {key} = {value} at time {granted_time}")
            
            
            # Always request time advancement to maintain time synchronization
            #requested_time = min(granted_time + period, total_time)
            granted_time = h.helicsFederateRequestTime(self.fed, requested_time)
            requested_time = granted_time
            has_event = False
            start_time += granted_time
            
            
            
            
    def process_event(self, key, value, time):
        """Override this method to handle subscription events"""
        pass
    
    def process_message(self, endpoint_name, message, time):
        """Override this method to handle endpoint messages"""
        pass
    
    def generate_output(self, publication_key, time):
        """Override this method to generate output values when events occur"""
        return time * 0.1  # Default implementation
            
            
           


if __name__ == "__main__":
    from BaseFederate import main
    main(EventDrivenType)