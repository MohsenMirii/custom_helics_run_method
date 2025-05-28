# -*- coding: utf-8 -*-
"""
Created on Mon Apr  7 15:29:30 2025

@author: Mohsen
"""



import helics as h
import logging
import threading
import os
from subprocess import PIPE, run
from CustomRunner import HelicsCustomRunner


def main_run(run_path):
    print('start running the co-simulation')
    
    
    # command = ["helics", "-v", "run", "--path=%s"%run_path]
    # result = run(command, stdout=PIPE, stderr=PIPE, text=True)
    # print(result.returncode, result.stdout, result.stderr)
    
    runner = HelicsCustomRunner(run_path)
    
    try:
        print("Starting simulation...")
        runner.start()  # This will block until completion or interruption
    except KeyboardInterrupt:
        print("\nInterrupt received...")
    finally:
        runner.stop()
   




# Example usage
if __name__ == "__main__":
    logging.basicConfig(filename="log.txt", level=logging.INFO, 
                        format="%(asctime)s - %(levelname)s - %(message)s")    

    # run multi-processing
    main_run('./federates/runner.json')
    #  end multi-processing

    logging.info("broker is stoped")


    
    
    
    
    