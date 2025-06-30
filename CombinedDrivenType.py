# -*- coding: utf-8 -*-
"""
Created on Wed May 21 16:40:30 2025

@author: Mohsen
"""

from BaseFederate import BaseFederate
import helics as h
from FederateConfig import TimingConfigs



class CombinedDrivenType(BaseFederate):
    def run_federate(self):
       
       # Enter execution mode
       h.helicsFederateEnterExecutingMode(self.fed)
       
       timing_config = TimingConfigs(**self.federate_config.timing_configs)

       max_iterations = timing_config.int_max_iterations        

       requested_time = h.HELICS_TIME_MAXTIME
       
       granted_time = h.helicsFederateRequestTime(self.fed, requested_time)
       
       ep_name, ep = next(iter(self.endpoints.items()))

       key, sub = next(iter(self.subscriptions.items()))

       
       # # while h.helicsFederateGetState(self.fed) == h.HELICS_STATE_EXECUTION:
       # while granted_time < max_iterations:
            
       #      print("*********************************************************************************")
       #      print(f"request time is {requested_time}")
       #      print(f"granted time is {granted_time}")
            
           
       #      while h.helicsEndpointHasMessage(ep) or h.helicsInputIsUpdated(sub):
       #          msg = h.helicsEndpointGetMessage(ep)
       #          data = h.helicsMessageGetString(msg)
       #          source = h.helicsMessageGetOriginalSource(msg) 
                
       #          #if not data:
       #          print(f"Received Message: {data} From: {source} At: {granted_time}")
                
       #          value = h.helicsInputGetDouble(sub)
       #          #if not value:
       #          print(f"{self.federate_config.name}: Received {key} = {value} at {granted_time}")
                

       #      granted_time = h.helicsFederateRequestTime(self.fed, requested_time)
       
       while granted_time < max_iterations:
           print("*********************************************************************************")
           print(f"request time is {requested_time}")
           print(f"granted time is {granted_time}")
           
           # Create a function to check if any endpoint has messages or any subscription is updated
           def has_messages_or_updates():
               # Check all endpoints
               for ep in self.endpoints.values():
                   if h.helicsEndpointHasMessage(ep):
                       return True
                   
               # Check all subscriptions
               for sub in self.subscriptions.values():
                   if h.helicsInputIsUpdated(sub):
                       return True
                   
               return False
    
           # Main processing loop
           while has_messages_or_updates():
               # Process all endpoints first
               for ep_name, ep in self.endpoints.items():
                   while h.helicsEndpointHasMessage(ep):
                       msg = h.helicsEndpointGetMessage(ep)
                       data = h.helicsMessageGetString(msg)
                       source = h.helicsMessageGetOriginalSource(msg)
                       print(f"Received Message from {ep_name}: {data} From: {source} At: {granted_time}")
        
               # Then process all subscriptions
               for key, sub in self.subscriptions.items():
                   if h.helicsInputIsUpdated(sub):
                       value = h.helicsInputGetDouble(sub)
                       print(f"{self.federate_config.name}: Received {key} = {value} at {granted_time}")
                       
           granted_time = h.helicsFederateRequestTime(self.fed, requested_time)
            
    
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
    main(CombinedDrivenType)