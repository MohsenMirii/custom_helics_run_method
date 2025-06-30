# -*- coding: utf-8 -*-
"""
Created on Wed Jun 08 16:40:30 2025

@author: Mohsen
"""

from BaseFederate import BaseFederate
import helics as h
from FederateConfig import TimingConfigs
import logging


class MessageDrivenType(BaseFederate):
    def run_federate(self):
        # Enter execution mode
        h.helicsFederateEnterExecutingMode(self.fed)
        
        timing_config = TimingConfigs(**self.federate_config.timing_configs)

        max_iterations = timing_config.int_max_iterations        

        requested_time = h.HELICS_TIME_MAXTIME
        
        granted_time = h.helicsFederateRequestTime(self.fed, requested_time)
        
        ep_name, ep = next(iter(self.endpoints.items()))

        # while h.helicsFederateGetState(self.fed) == h.HELICS_STATE_EXECUTION:
        while granted_time < max_iterations:
                            
            print("*********************************************************************************")
            print(f"request time is {requested_time}")
            print(f"granted time is {granted_time}")  
            
            
            while h.helicsEndpointHasMessage(ep):                
                msg = h.helicsEndpointGetMessage(ep)
                data = h.helicsMessageGetString(msg)
                source = h.helicsMessageGetOriginalSource(msg)                    
                print(f"Received Message: {data} From: {source} At: {granted_time}")
                self.process_message(ep_name, msg, granted_time)
                # logger.debug(f'\tReceived message from endpoint {source} at time {grantedtime} with SOC {currentsoc}')
                
            granted_time = h.helicsFederateRequestTime(self.fed, requested_time)

           
    def process_message(self, endpoint_name, message, time):
        """Override this method to handle endpoint messages"""
        if self.endpoints:
                for key, pub in self.endpoints.items():
                        default_dest = h.helicsEndpointGetDefaultDestination(pub)
                        message = f"message: {time}" 
                        h.helicsEndpointSendMessageRaw(pub, default_dest, message)                    
                        print(f"{key}: send {message} to distination: {default_dest}  at time {time}")
        pass 


           


if __name__ == "__main__":
    from BaseFederate import main
    main(MessageDrivenType)