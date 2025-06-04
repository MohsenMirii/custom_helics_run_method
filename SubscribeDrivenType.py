# -*- coding: utf-8 -*-
"""
Created on Wed May 21 16:40:30 2025

@author: Mohsen
"""

from BaseFederate import BaseFederate
import helics as h
from FederateConfig import TimingConfigs
from multiprocessing import Pool




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
            
            # if granted_time > 3.0:
            #     raise Exception("Fake Exceptions to test its impact on the performance of other federates !")
            
            print(f"*********************************************************************************")        
            print(f"***************** iteration {granted_time} ********************")        
            
            
            print(f"request time is {requested_time}")
            print(f"granted time is {granted_time}")            
           

            # Check subscriptions for new data
            if self.subscriptions:
                for key, sub in self.subscriptions.items():
                    while h.helicsInputIsUpdated(sub):
                        has_event = True
                        value = h.helicsInputGetDouble(sub)                        
                        
                        print(f"{self.federate_config.name}: Received event {key} = {value} at time {granted_time}")                       
                        
                        # Process the event here
                        self.process_event(key, value, granted_time)            
            
            
            # In your main code:
            if self.subscriptions:
                with Pool() as pool:
                    args = []
                    for key, sub in self.subscriptions.items():
                        while h.helicsInputIsUpdated(sub):
                            value = h.helicsInputGetDouble(sub)
                            print(f"Received event {key} = {value}")
                            args.append((self, key, value, granted_time))
                    
                    pool.map(self.process_event_wrapper, args)
        
        
        
            granted_time = h.helicsFederateRequestTime(self.fed, requested_time)
            requested_time = granted_time
            has_event = False
            start_time += granted_time
            
            
            
    def process_event_wrapper(args):
      self_ref, key, value, time = args
      return self_ref.process_event(key, value, time)
  
    
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