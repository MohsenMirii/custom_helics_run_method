# -*- coding: utf-8 -*-
"""
Created on Wed Jun 08 16:40:30 2025

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
            print(f"***************** iteration {granted_time} ********************")             
            print(f"request time is {requested_time}")
            print(f"granted time is {granted_time}")
            
            # Reset event flag at start of each iteration
            has_event = False
                        
            # Check ALL endpoints for messages at current time
            if self.endpoints:
                for name, ep in self.endpoints.items():
                    while h.helicsEndpointHasMessage(ep):
                        msg = h.helicsEndpointGetMessage(ep)
                        msg_time = h.helicsMessageGetTime(msg)
                
                        # Only process messages for current time
                        if msg_time <= granted_time:
                            has_event = True
                            source = h.helicsMessageGetSource(msg)
                            data = h.helicsMessageGetString(msg)
                            print(f"Received message at {granted_time}: {data} from {source}")
                            self.process_message(name, msg, granted_time)
                        else:
                            # Return message to queue if it's for future
                            h.helicsEndpointSendMessageRaw(ep, source, data, msg_time)
                            break
            
            
            
            # Event-driven time request logic
            if has_event:            
                # Advance time
                granted_time = h.helicsFederateRequestTime(self.fed, requested_time)            
                requested_time = granted_time
            
            
    
    def process_message(self, endpoint_name, message, time):
        """Override this method to handle endpoint messages"""
        pass            
           


if __name__ == "__main__":
    from BaseFederate import main
    main(EventDrivenType)