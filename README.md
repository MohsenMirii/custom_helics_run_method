# HELICS Co-Simulation Event Driven with Custom Runner
This repository contains customized HELICS co-simulation runners that provide greater flexibility for tailoring co-simulations and improve the readability and usability of simulation results.
It includes  **Three different runner types for Time-Based federates** and **Three different runner types for Event-Based federates** .




## Key Features:
**1- Three different runner types for Time-Based federates** 

When observing the iterations of the co-simulation system, we use a `while` loop that performs the following actions:

• **Subscribe to and publish values**

• **Send and receive messages**

• **Request and advance to the granted time**

In RunnerType1.py, RunnerType2.py, and RunnerType3.py, these actions are executed in three different orders, as described above.

**Reference:** https://github.com/GMLC-TDC/HELICS-Examples/blob/main/user_guide_examples/fundamental/fundamental_default/Charger.py

<br>

**2- Three different runner types for Event-Based federates**

An Event-Based Federate in HELICS operates by reacting to discrete events, such as incoming messages or value updates, rather than progressing in fixed time steps. It advances simulation time only when an event occurs, making it well-suited for systems where actions are triggered by external signals or state changes.

For this purpose, I created three types of event-based runners:

• **ValueDrivenType.py** : Used for federates whose events are triggered solely by value updates.

• **MessageDrivenType.py** : Used for federates whose events are triggered solely by incoming messages.

• **CombinedDrivenType.py** : Used for federates whose events are triggered by either value updates **OR** incoming messages.


**NOTE** : All of RunnerType1.py, RunnerType2.py, RunnerType3.py, ValueDrivenType.py, MessageDrivenType.py, and CombinedDrivenType.py inherit from BaseFederate.py. The BaseFederate.py handles the basic initialization configurations common to all federates, such as applying timing configurations, applying flag configurations, registering publications, registering subscriptions, and registering endpoints.
When we want to run each federate differently, we use one of the time-based or event-based runners unique to it.
It is worth noting that each federate may have unique flag or timing configurations; BaseFederate.py reads and sets these configurations for each federate.



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



