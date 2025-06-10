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
        
        
        while granted_time < max_iterations:
            
            print("*********************************************************************************")        
            print(f"***************** iteration {requested_time} ********************")
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
            if self.subscriptions:
                for sub_name, subscription in self.subscriptions.items():
                    if h.helicsInputIsUpdated(subscription):
                        has_event = True
                        value = h.helicsInputGetDouble(subscription)  # Or appropriate type
                        print(f"Subscription[{sub_name}] Updated: {value}")
                        self.process_subscription_update(sub_name, value, granted_time)
                
                
            
            # ----------------------------
            # 3. Handle Publications if Events Occurred
            # ----------------------------
            if has_event or granted_time == 0:
                if self.publications:
                    for pub_name, publication in self.publications.items():
                        pub_value = granted_time
                        h.helicsPublicationPublishDouble(publication, pub_value)
                        print(f"Published {pub_name} = {pub_value}")
                
                
            # Event-driven time request logic
            if has_event:            
                # Advance time
                granted_time = h.helicsFederateRequestTime(self.fed, requested_time)            
                requested_time = granted_time            
            
    
    def generate_output(self, publication_key, time):
        """Override this method to generate output values when events occur"""
        return time * 0.1  # Default implementation
            
            
           


if __name__ == "__main__":
    from BaseFederate import main
    main(EventDrivenType)