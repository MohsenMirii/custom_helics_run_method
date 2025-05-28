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
            
            
            
def print_changed_flags(fed):
    """Prints only flags that were modified from their true defaults."""
    # Verified defaults for HELICS 3.x (most common cases)
    default_flags = {
        "TERMINATE_ON_ERROR": False,  # Default: False
        "DEBUGGING": False,           # Default: False
        "REALTIME": False,            # Default: False (except for dedicated real-time cores)
        "UNINTERRUPTIBLE": True,      # Default: True (federates are uninterruptible by default!)
        "OBSERVER": False,            # Default: False
        "SOURCE_ONLY": False,         # Default: False
        "ONLY_TRANSMIT_ON_CHANGE": False,  # Default: False
        "ONLY_UPDATE_ON_CHANGE": False,    # Default: False
        "WAIT_FOR_CURRENT_TIME_UPDATE": False,  # Default: False
        "RESTRICTIVE_TIME_POLICY": False,   # Default: False
        "ROLLBACK": False,            # Default: False
        "FORWARD_COMPUTE": True,      # Default: True (allows time requests beyond current time)
        "EVENT_TRIGGERED": False,     # Default: False
        "SINGLE_THREAD_FEDERATE": False,  # Default: False
        "IGNORE_TIME_MISMATCH_WARNINGS": False,  # Default: False
        "FORCE_LOGGING_FLUSH": False,  # Default: False
        "DUMPLOG": False,             # Default: False
        "SLOW_RESPONDING": False,     # Default: False
    }

    flag_ids = {
        "TERMINATE_ON_ERROR": h.HELICS_FLAG_TERMINATE_ON_ERROR,
        "DEBUGGING": h.HELICS_FLAG_DEBUGGING,
        "REALTIME": h.HELICS_FLAG_REALTIME,
        "UNINTERRUPTIBLE": h.HELICS_FLAG_UNINTERRUPTIBLE,
        "OBSERVER": h.HELICS_FLAG_OBSERVER,
        #"STRICT_CONFIG_CHECKING": h.HELICS_FLAG_STRICT_CONFIG_CHECKING,
        "SOURCE_ONLY": h.HELICS_FLAG_SOURCE_ONLY,
        "ONLY_TRANSMIT_ON_CHANGE": h.HELICS_FLAG_ONLY_TRANSMIT_ON_CHANGE,
        "ONLY_UPDATE_ON_CHANGE": h.HELICS_FLAG_ONLY_UPDATE_ON_CHANGE,
        "WAIT_FOR_CURRENT_TIME_UPDATE": h.HELICS_FLAG_WAIT_FOR_CURRENT_TIME_UPDATE,
        "RESTRICTIVE_TIME_POLICY": h.HELICS_FLAG_RESTRICTIVE_TIME_POLICY,
        "ROLLBACK": h.HELICS_FLAG_ROLLBACK,
        "FORWARD_COMPUTE": h.HELICS_FLAG_FORWARD_COMPUTE,
        "EVENT_TRIGGERED": h.HELICS_FLAG_EVENT_TRIGGERED,
        "SINGLE_THREAD_FEDERATE": h.HELICS_FLAG_SINGLE_THREAD_FEDERATE,
        "IGNORE_TIME_MISMATCH_WARNINGS": h.HELICS_FLAG_IGNORE_TIME_MISMATCH_WARNINGS,
        "FORCE_LOGGING_FLUSH": h.HELICS_FLAG_FORCE_LOGGING_FLUSH,
        "DUMPLOG": h.HELICS_FLAG_DUMPLOG,
        "SLOW_RESPONDING": h.HELICS_FLAG_SLOW_RESPONDING,
    }

    print("\nCHANGED FLAGS (Non-Default) ")
    changed_count = 0
    for name, default_value in default_flags.items():
        current_value = h.helicsFederateGetFlagOption(fed, flag_ids[name])
        if current_value != default_value:
            print(f"{name.ljust(30)}: {str(current_value).ljust(5)} (Default: {default_value})")
            changed_count += 1
    
    if changed_count == 0:
        print("No flags changed from defaults.")