# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 14:53:29 2025

@author: Mohsen
"""

from pydantic import BaseModel
from typing import List, Dict, Optional,Any



from dataclasses import dataclass
from typing import List, Dict, Optional, Union

@dataclass
class TimingConfigs:
    time_period: float
    real_period: float
    time_offset: float
    time_stop: float
    time_delta: float
    int_max_iterations:int    
    start_time: str
    timeout: int
   
    

@dataclass
class Flags:
    terminate_on_error: bool
    debugging: bool
    realtime: bool
    uninterruptible: bool
    observer: bool
    strict_config_checking: bool
    source_only: bool
    only_transmit_on_change: bool
    only_update_on_change: bool
    wait_for_current_time_update: bool
    restrictive_time_policy: bool
    rollback: bool
    forward_compute: bool
    event_triggered: bool
    single_thread_federate: bool
    ignore_time_mismatch_warnings: bool
    force_logging_flush: bool
    dumplog: bool
    slow_responding: bool

@dataclass
class ConnectionEndpoint:
    key: str
    type: str
    unit: str

@dataclass
class Endpoint:
    key: str
    type: str
    destination : str
    default_destination : str

@dataclass
class FederateConfig:
    name: str
    core_type: str
    log_level: str
    
    timing_configs: TimingConfigs
    flags: Flags    
    endpoints: List[Endpoint]    
    subscriptions: List[ConnectionEndpoint]
    publications: List[ConnectionEndpoint]
    memory: List[str]
