# -*- coding: utf-8 -*-
"""
Created on Sat Mar 22 22:34:09 2025

@author: Mohsen
"""

import helics as h

def apply_flag_configs(fedinfo, flags_config):
    """
    Dynamically set HELICS flag options based on a JSON configuration.
    
    Args:
        fedinfo: The federate info object.
        flags_config: A dictionary containing flag configurations (e.g., {"terminate_on_error": True}).
    """
    # Prefix for HELICS flag constants
    flag_prefix = "helics_flag_"

    # Apply flags dynamically
    for key, value in flags_config.items():
        # Construct the HELICS flag name
        flag_name = flag_prefix + key.lower()

        # Check if the flag exists in the helics module
        if hasattr(h, flag_name):
            # Get the HELICS flag constant
            helics_flag = getattr(h, flag_name)
            # Set the flag
            h.helicsFederateInfoSetFlagOption(fedinfo, helics_flag, value)
        else:
            print(f"Warning: Unsupported flag '{key}' will be ignored.")