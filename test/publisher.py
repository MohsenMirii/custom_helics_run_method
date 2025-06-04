# -*- coding: utf-8 -*-
"""
Created on Tue Jun  3 11:00:38 2025

@author: Mohsen
"""

import helics as h

fedinfo = h.helicsCreateFederateInfo()
h.helicsFederateInfoSetCoreTypeFromString(fedinfo, "zmq")
h.helicsFederateInfoSetCoreInitString(fedinfo, "--federates=1")
h.helicsFederateInfoSetTimeProperty(fedinfo, h.helics_property_time_delta, 1.0)

fed = h.helicsCreateValueFederate("PubFederate", fedinfo)
pub = h.helicsFederateRegisterGlobalPublication(fed, "pub1", h.HELICS_DATA_TYPE_INT, "")

h.helicsFederateEnterExecutingMode(fed)

# Publish at time 1.0
h.helicsFederateRequestTime(fed, 1.0)
h.helicsPublicationPublishInteger(pub, 1)
print("Published 1 at time", h.helicsFederateGetCurrentTime(fed))

h.helicsFederateFinalize(fed)
h.helicsCloseLibrary()
