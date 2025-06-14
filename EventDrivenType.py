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
        granted_time = 0.0
        requested_time = 0.0
        granted_time = h.helicsFederateRequestTime(self.fed, requested_time)
        start_time = 0.0
        small_increasement_step = 0.5
        
        
        while granted_time < max_iterations:
            
            print("*********************************************************************************")        
            # print(f"***************** iteration {requested_time} ********************")
            print(f"request time is {requested_time}")
            print(f"granted time is {granted_time}")
            
            # if granted_time > 3.0:
            #     raise Exception("Fake Exceptions to test its impact on the performance of other federates !")


            # Reset event flag at start of each iteration
            has_event = False

            # ----------------------------
            # 1. Check Endpoints for Messages
            # ----------------------------
            if self.endpoints:
                for ep_name, endpoint in self.endpoints.items():
                    while h.helicsEndpointHasMessage(endpoint):
                        msg = h.helicsEndpointGetMessage(endpoint)
                        msg_time = h.helicsMessageGetTime(msg)
                
                        # Only process messages for current or past time
                        if msg_time <= granted_time:
                            has_event = True
                            source = h.helicsMessageGetSource(msg)
                            data = h.helicsMessageGetString(msg)
                            print(f"Endpoint[{ep_name}] Received: {data} from {source}")
                        else:
                            # Return future-dated messages to queue
                            h.helicsEndpointSendMessageRaw(endpoint, source, data, msg_time)
                        break
            
            
            
            # ----------------------------
            # 2. Check Subscriptions for Updates
            # ----------------------------
                
            # Check subscriptions for updates
            if self.subscriptions:
                for key, sub in self.subscriptions.items():
                    if h.helicsInputIsUpdated(sub):
                        has_event = True
                        value = h.helicsInputGetDouble(sub)
                        print(f"{self.federate_config.name}: Received {key} = {value} at {granted_time}")
                        # Process event immediately (no parallel pool needed for event-driven)
                        self.process_event(key, value, granted_time) 
            
            # ----------------------------
            # 3. Handle Publications if Events Occurred
            # ----------------------------
            # if has_event or granted_time == 0:
            #     if self.publications:
            #         for pub_name, publication in self.publications.items():
            #             pub_value = granted_time
            #             h.helicsPublicationPublishDouble(publication, pub_value)
            #             print(f"Published {pub_name} = {pub_value}")
                
            
            
            # # Event-driven time request logic
            # if has_event or granted_time == 0.0:            
            #     # Advance time
            #     granted_time = h.helicsFederateRequestTime(self.fed, requested_time)            
            #     requested_time = granted_time
            # else:
            #     granted_time = h.helicsFederateRequestTime(self.fed, requested_time)      
            #     requested_time = granted_time
            
            granted_time = h.helicsFederateRequestTime(self.fed, requested_time)            
            requested_time = granted_time
            
    
    def generate_output(self, publication_key, time):
        """Override this method to generate output values when events occur"""
        return time * 0.1  # Default implementation
            
            
    def process_event(self, key, value, time):
        """Override this method to handle subscription events"""
        # Publish any outputs if needed
        if self.publications:
            for key, pub in self.publications.items():
                value = self.generate_output(key, time)
                h.helicsPublicationPublishDouble(pub, value)
                print(f"{self.federate_config.name}: Published {key} = {value} at time {time}")     


if __name__ == "__main__":
    from BaseFederate import main
    main(EventDrivenType)