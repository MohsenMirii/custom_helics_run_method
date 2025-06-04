import helics as h
import threading

def create_broker():
    initstring = "--federates=2"
    broker = h.helicsCreateBroker("zmq", "", initstring)
    print("Broker created")
    return broker

def run_publisher():
    fedinfo = h.helicsCreateFederateInfo()
    h.helicsFederateInfoSetCoreTypeFromString(fedinfo, "zmq")
    h.helicsFederateInfoSetTimeProperty(fedinfo, h.helics_property_time_delta, 1.0)
    
    vfed = h.helicsCreateValueFederate("publisher_fed", fedinfo)
    pub = h.helicsFederateRegisterGlobalPublication(vfed, "test", h.HELICS_DATA_TYPE_INT, "")
    
    h.helicsFederateEnterExecutingMode(vfed)
    print("Publisher entered execution mode")
    
    for value in range(1, 101):
        granted_time = h.helicsFederateRequestTime(vfed, value * 1.0)
        h.helicsPublicationPublishInteger(pub, value)
        print(f"Publisher sent value {value} at time {granted_time}")
    
    h.helicsFederateFinalize(vfed)
    print("Publisher finalized")

def run_subscriber():
    fedinfo = h.helicsCreateFederateInfo()
    h.helicsFederateInfoSetCoreTypeFromString(fedinfo, "zmq")
    h.helicsFederateInfoSetTimeProperty(fedinfo, h.helics_property_time_delta, 1.0)
    h.helicsFederateInfoSetFlagOption(fedinfo, h.HELICS_FLAG_WAIT_FOR_CURRENT_TIME_UPDATE, True)
    
    vfed = h.helicsCreateValueFederate("subscriber_fed", fedinfo)
    sub = h.helicsFederateRegisterSubscription(vfed, "test", "")
    
    h.helicsFederateEnterExecutingMode(vfed)
    print("Subscriber entered execution mode")
    
    for time_request in range(1, 101):
        granted_time = h.helicsFederateRequestTime(vfed, time_request * 1.0)
        if h.helicsInputIsUpdated(sub):
            value = h.helicsInputGetInteger(sub)
            print(f"Subscriber received value {value} at time {granted_time}")
        else:
            print(f"Subscriber got no update at time {granted_time}")
    
    h.helicsFederateFinalize(vfed)
    print("Subscriber finalized")

def main():
    broker_thread = threading.Thread(target=create_broker)
    broker_thread.start()
    
    # Give broker time to start
    import time; time.sleep(1)
    
    pub_thread = threading.Thread(target=run_publisher)
    sub_thread = threading.Thread(target=run_subscriber)
    
    pub_thread.start()
    sub_thread.start()
    
    pub_thread.join()
    sub_thread.join()
    
    broker_thread.join()
    print("Simulation completed")

if __name__ == "__main__":
    main()