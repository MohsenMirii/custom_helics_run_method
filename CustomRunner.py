# -*- coding: utf-8 -*-
"""
Created on Wed Apr 16 09:19:07 2025

@author: Mohsen
"""

import subprocess
import threading
import logging
from pathlib import Path
import json
import time
import signal
import sys
import os

class HelicsCustomRunner:
    def __init__(self, config_path):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.processes = []  # Stores (name, process) tuples
        self.loggers = {}
        self._stop_event = threading.Event()
        self.setup_logging()
        
    def _load_config(self):
        with open(self.config_path) as f:
            return json.load(f)
    
    def setup_logging(self):
        """Setup individual loggers for each federate and the main runner"""
        # Create logs directory if not exists
        Path("logs").mkdir(exist_ok=True)
        
        # Main runner logger
        self.loggers['runner'] = self._create_logger('runner')
        
        # Federate loggers
        for fed in self.config['federates']:
            fed_name = fed['name']
            self.loggers[fed_name] = self._create_logger(fed_name)
    
    def _create_logger(self, name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        
        
        # Add filter to exclude HELICS debug messages
        class HelicsFilter(logging.Filter):
            def filter(self, record):
                return "[console] [debug]" not in record.getMessage()
        
        # File handler
        fh = logging.FileHandler(f'logs/{name}.log')
        fh.setLevel(logging.DEBUG)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.addFilter(HelicsFilter())  # Add the filter

        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    def _run_federate(self, federate_config):
        """Run a single federate in a subprocess"""
        fed_name = federate_config['name']
        cmd = federate_config['exec'].split()
        
        try:
            self.loggers['runner'].info(f"Starting federate: {fed_name}")
            self.loggers[fed_name].info(f"Command: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                cwd=federate_config.get('directory', '.'),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes.append((fed_name, process))
            
            # Start output logging threads
            threading.Thread(
                target=self._log_stream,
                args=(process.stdout, fed_name, logging.INFO),
                daemon=True
            ).start()
            
            threading.Thread(
                target=self._log_stream,
                args=(process.stderr, fed_name, logging.ERROR),
                daemon=True
            ).start()
            
            return process
            
        except Exception as e:
            self.loggers[fed_name].error(f"Start failed: {str(e)}")
            raise
    
    def _log_stream(self, stream, name, level):
        """Log stream output in real-time with filtering"""
        logger = self.loggers[name]
        try:
            for line in iter(stream.readline, ''):
                if self._stop_event.is_set():
                    break
                if line.strip():
                    # Filter out HELICS debug messages
                    if "[console] [debug]" not in line:
                        logger.log(level, line.strip())
        except ValueError:
            pass  # Stream closed
    
    def _signal_handler(self, sig, frame):
        """Handle termination signals"""
        self.loggers['runner'].info("Received termination signal")
        self.stop()
        sys.exit(0)
    
    def start(self):
        """Start all federates in the correct order"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.loggers['runner'].info(f"Starting HELICS co-simulation: {self.config['name']}")
        
        # Start broker first
        broker_config = next(f for f in self.config['federates'] if f['name'] == 'mainbroker')
        broker_process = self._run_federate(broker_config)
        
        # Wait for broker to initialize
        time.sleep(2)
        
        # Start other federates
        for federate in [f for f in self.config['federates'] if f['name'] != 'mainbroker']:
            if self._stop_event.is_set():
                break
            self._run_federate(federate)
            time.sleep(0.5)
        
        # Monitor processes
        while not self._stop_event.is_set():
            time.sleep(1)
            for name, process in self.processes[:]:  # Create copy for iteration
                if process.poll() is not None:  # Process finished
                    self.loggers['runner'].warning(f"Federate {name} terminated")
                    self.processes.remove((name, process))
            
            if not self.processes:
                break
    
    def stop(self):
        """Cleanly stop all running processes"""
        self._stop_event.set()
        self.loggers['runner'].info("Stopping all federates...")
        
        # Terminate in reverse order (federates first, then broker)
        for name, process in reversed(self.processes):
            try:
                self.loggers[name].info("Terminating...")
                process.terminate()
                
                # Wait for process to end
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.loggers[name].warning("Force killing...")
                    process.kill()
                
                self.loggers[name].info("Stopped")
            except Exception as e:
                self.loggers[name].error(f"Stop failed: {str(e)}")
        
        self.processes.clear()
        self.loggers['runner'].info("All federates stopped")

    def is_running(self):
        """Check if any federates are still running"""
        return any(p.poll() is None for _, p in self.processes)