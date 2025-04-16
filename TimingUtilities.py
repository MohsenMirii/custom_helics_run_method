
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 22 22:04:07 2025

@author: Mohsen
"""
import helics as h
from datetime import datetime, timezone

def apply_timing_configs(fed, timing_configs):
    """
    Apply timing configurations dynamically with proper type handling and error checking.
    
    Args:
        fed: HELICS federate
        timing_configs: Dictionary of timing configurations
    """
    # Property type mapping (prefix to property type)
    property_types = {
        'time_': {
            'prefix': 'HELICS_PROPERTY_TIME_',
            'setter': h.helicsFederateSetTimeProperty,
            'converter': float
        },
        'int_': {
            'prefix': 'HELICS_PROPERTY_INT_',
            'setter': h.helicsFederateSetIntegerProperty,
            'converter': int
        },
        '': {
            'prefix': 'HELICS_PROPERTY_',
            'setter': h.helicsFederateSetFlagOption,
            'converter': lambda x: h.HELICS_TRUE if x else h.HELICS_FALSE
        }
    }

    
    # Special cases that need custom handling
    special_cases = {
        'start_time': lambda f, v: h.helicsFederateSetTimeProperty(
            f, 
            h.HELICS_PROPERTY_TIME_STARTTIME,
            datetime.strptime(v, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp()
        ),
        'timeout': lambda f, v: h.helicsFederateSetIntegerProperty(
            f,
            h.HELICS_PROPERTY_INT_INPUT_DELAY,
            int(v) * 1000  # Convert seconds to milliseconds
        )
    }

    for key, value in timing_configs.items():
        try:
            # Handle special cases first
            if key in special_cases:
                special_cases[key](fed, value)
                continue

            # Try to find matching property
            found = False
            for prefix, prop_info in property_types.items():
                if key.startswith(prefix):
                    property_name = prop_info['prefix'] + key[len(prefix):].upper()
                    helics_property = getattr(h, property_name, None)
                    
                    if helics_property is not None:
                        converted_value = prop_info['converter'](value)
                        #prop_info['setter'](fed, helics_property, converted_value)
                        
                        h.helicsFederateInfoSetTimeProperty(fed,helics_property, converted_value)
                        found = True
                        break
            
            if not found:
                print(f"Warning: Configuration '{key}' doesn't match any known HELICS property")
                
        except (ValueError, TypeError) as e:
            print(f"Error processing property '{key}': {str(e)}")
        except AttributeError:
            print(f"Warning: Property '{key}' not found in HELICS constants")
        except Exception as e:
            print(f"Unexpected error setting property '{key}': {str(e)}")
