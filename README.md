# HELICS Co-Simulation with Custom Logging Control
This repository contains a customized HELICS co-simulation runner that provides enhanced control over logging output, making simulation results more readable and actionable.

**Key Features:**

# Intelligent Log Filtering:
Our custom runner automatically filters out noisy HELICS debug messages like:

![1](https://github.com/user-attachments/assets/9583a0c8-d5e9-418e-952a-5bb1defd5fbf)


while preserving your important simulation messages.

# Multi-Level Logging Architecture
  **File Logs:** Complete unfiltered logs for debugging (logs/*.log)

  **Console Output:** Clean, filtered output showing only relevant information

  **Per-Federate Logs:** Separate log files for each federate

# Customizable Filtering
Easily modify what gets logged by editing the filter patterns in custom_runner.py:
![2](https://github.com/user-attachments/assets/96ddafdd-b4a7-4db5-8eb5-ddafc6d6f6cf)


# Run the code:
Clone the repository then run this command:
**python helics.py**
you can see all log files in **logs** folder.



