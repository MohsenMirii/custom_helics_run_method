import subprocess
import logging
from pathlib import Path
import json
import time
import signal
import sys
import re

class HelicsCustomRunner:
    def __init__(self, config_path):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.processes = []
        self.setup_logging()
        
    def _load_config(self):
        with open(self.config_path) as f:
            return json.load(f)
    
    def setup_logging(self):
        """Setup logging with custom filtering"""
        self.logger = logging.getLogger('runner')
        self.logger.setLevel(logging.DEBUG)
        
        log_file = Path('logs/runner.log')
        log_file.parent.mkdir(exist_ok=True)
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.DEBUG)
        
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Custom formatter that filters HELICS debug logs
        class CustomFormatter(logging.Formatter):
            HELICS_DEBUG_PATTERN = re.compile(
                r'\[.*\] \[(console|debug)\] \[(debug|info)\].*|'
                r'::(receive|send|Granted|Time mismatch).*'
            )
            
            def format(self, record):
                msg = super().format(record)
                if self.HELICS_DEBUG_PATTERN.search(msg):
                    return ''  # Filter out HELICS debug messages
                return msg
        
        formatter = CustomFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
    
    def _run_federate(self, federate_config):
        """Run federate with reduced logging level"""
        fed_name = federate_config['name']
        cmd = federate_config['exec'].split()
        
        # Add log level control to federate commands
        if '--loglevel' not in ' '.join(cmd):
            cmd.extend(['--loglevel=warning'])  # Reduce HELICS internal logging
        
        try:
            self.logger.info(f"Starting federate: {fed_name}")
            
            log_dir = Path('logs')
            log_dir.mkdir(exist_ok=True)
            
            stdout_log = log_dir / f'{fed_name}.log'
            #stderr_log = log_dir / f'{fed_name}.error.log'
            
            with open(stdout_log, 'w') as out, open(stdout_log, 'w') as err:
                process = subprocess.Popen(
                    cmd,
                    cwd=federate_config.get('directory', '.'),
                    stdout=out,
                    stderr=err,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
            
            self.processes.append((fed_name, process, stdout_log, stdout_log))
            return process
            
        except Exception as e:
            self.logger.error(f"Failed to start federate {fed_name}: {str(e)}")
            raise
    
    def _signal_handler(self, sig, frame):
        """Handle termination signals"""
        self.logger.info("Received termination signal. Shutting down...")
        self.stop()
        sys.exit(0)
    
    def _all_federates_finished(self):
        """Check if all federates have completed"""
        return all(process.poll() is not None for (_, process, *_) in self.processes)
    
    def _monitor_output(self):
        """Monitor log files with custom filtering"""
        try:
            while not self._all_federates_finished():
                for fed_name, process, stdout_log, stderr_log in self.processes:
                    if process.poll() is not None:
                        continue
                    
                    # Custom output filtering
                    def filter_output(lines):
                        return [
                            line for line in lines 
                            if not re.search(
                                r'\[.*\] \[(console|debug)\] \[(debug|info)\].*|'
                                r'::(receive|send|Granted|Time mismatch).*',
                                line
                            )
                        ]
                    
                    # Print filtered stdout
                    if stdout_log.exists():
                        with open(stdout_log, 'r') as f:
                            lines = filter_output(f.readlines())
                            if lines:
                                print(f"[{fed_name}] " + lines[-1].strip())
                    
                    # Print filtered stderr
                    if stderr_log.exists():
                        with open(stderr_log, 'r') as f:
                            lines = filter_output(f.readlines())
                            if lines:
                                print(f"[{fed_name}-ERROR] " + lines[-1].strip())
                
                time.sleep(0.5)
            
            self.logger.info("All federates have completed")
            self.stop()
            
        except KeyboardInterrupt:
            self.stop()
    
    def start(self):
        """Start the co-simulation"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info(f"Starting co-simulation: {self.config['name']}")
        
        # Start broker first with reduced logging
        broker_config = next(f for f in self.config['federates'] if f['name'] == 'mainbroker')
        broker_cmd = broker_config['exec'].split()
        if '--loglevel' not in ' '.join(broker_cmd):
            broker_cmd.extend(['--loglevel=warning'])
        broker_config['exec'] = ' '.join(broker_cmd)
        self._run_federate(broker_config)
        time.sleep(1)
        
        # Start other federates
        for federate in [f for f in self.config['federates'] if f['name'] != 'mainbroker']:
            self._run_federate(federate)
            time.sleep(0.5)
        
        self.logger.info("All federates started. Monitoring output...")
        self._monitor_output()
    
    def stop(self):
        """Clean shutdown"""
        self.logger.info("Stopping all federates...")
        
        for name, process, *_ in reversed(self.processes):
            try:
                if process.poll() is None:
                    self.logger.info(f"Terminating {name}...")
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                    self.logger.info(f"{name} terminated")
            except Exception as e:
                self.logger.error(f"Error terminating {name}: {str(e)}")
        
        self.processes = []
        self.logger.info("All federates stopped")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python custom_runner.py <config.json>")
        sys.exit(1)
    
    runner = HelicsCustomRunner(sys.argv[1])
    try:
        runner.start()
    except Exception as e:
        logging.getLogger('runner').error(f"Fatal error: {str(e)}")
        runner.stop()
        raise