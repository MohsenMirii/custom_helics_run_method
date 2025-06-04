# -*- coding: utf-8 -*-
"""
Created on Tue Jun  3 11:02:38 2025

@author: Mohsen
"""

import helics as h

# Create broker using ZMQ core with 2 federates
broker = h.helicsCreateBroker("zmq", "", "--federates=2")

# Confirm the broker is connected and running
if h.helicsBrokerIsConnected(broker):
    print("Broker created and connected.")

# Wait until broker disconnects (blocking)
while h.helicsBrokerIsConnected(broker):
    pass

# Clean up
h.helicsCloseLibrary()
