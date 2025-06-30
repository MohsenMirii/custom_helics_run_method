# HELICS Co-Simulation Event Driven with Custom Runner
This repository contains customized HELICS co-simulation runners that provide greater flexibility for tailoring co-simulations and improve the readability and usability of simulation results. It includes **Three different runner types for Time-Based federates** and **Three different runner types for Event-Based federates** .

# Key Features:

**1- Three different runner types for Time-Based federates**

When observing the iterations of the co-simulation system, we use a while loop that performs the following actions:

**• Subscribe to and publish values**

**• Send and receive messages**

**• Request and advance to the granted time**

In RunnerType1.py, RunnerType2.py, and RunnerType3.py, these actions are executed in three different orders, as described above.

**Reference**: https://github.com/GMLC-TDC/HELICS-Examples/blob/main/user_guide_examples/fundamental/fundamental_default/Charger.py

**2- Three different runner types for Event-Based federates**

An Event-Based Federate in HELICS operates by reacting to discrete events, such as incoming messages or value updates, rather than progressing in fixed time steps. It advances simulation time only when an event occurs, making it well-suited for systems where actions are triggered by external signals or state changes.

For this purpose, I created three types of event-based runners:

**• ValueDrivenType.py** : Used for federates whose events are triggered solely by value updates.

**• MessageDrivenType.py** : Used for federates whose events are triggered solely by incoming messages.

**• CombinedDrivenType.py** : Used for federates whose events are triggered by either value updates OR incoming messages.

**NOTE** : All of RunnerType1.py, RunnerType2.py, RunnerType3.py, ValueDrivenType.py, MessageDrivenType.py, and CombinedDrivenType.py inherit from BaseFederate.py. The BaseFederate.py handles the basic initialization configurations common to all federates, such as applying timing configurations, applying flag configurations, registering publications, registering subscriptions, and registering endpoints. When we want to run each federate differently, we use one of the time-based or event-based runners unique to it. It is worth noting that each federate may have unique flag or timing configurations; BaseFederate.py reads and sets these configurations for each federate.

**Reference**: https://github.com/GMLC-TDC/HELICS-Examples/blob/main/user_guide_examples/fundamental/fundamental_integration/Controller.py

**3- Federates Folder**

In this folder, we have the configuration files for four federates (Battery.yaml, Envelope.yaml, Family.yaml, HeatPump.yaml) in YAML format and runner.json. Each YAML file contains the following configurations:

1- name

2- core_type

3- log_level

4- timing_configs

5- flags

6- endpoints

7- Subscriptions

8- Publications

9- memory

**NOTE** : Each federate has relationships with others and can publish/subscribe to value(s) or send/receive message(s). In this case, the interaction schema is as follows:



![1](https://github.com/user-attachments/assets/8fd5129c-6c15-4fc8-b7c9-1307c732a32a)

**• Battery** : Subscribes nothing but publishes value to HeatPump, and sends message to Envelope and Family.

**• HeatPump(value driven federate)** : Subcribes value from Battery and publishes value to Family.

**• Envelope(message driven federate)** : Subscribes nothing, receives message from Battery and sends message to Family.

**• Family(message and value driven federate)** : Subscribes value from HeatPump, receives messages from Envelope and Battery.

**NOTE** :In runner.json, we introduce the federates to our co-simulation along with their desired runner type.

**4- Helics.py**

In this file, we specify the path to runner.json for the co-simulation. To run it, simply execute the following command in the command prompt: python helics.py

**5- CustomRunner.py**

In this file, we read the contents of runner.json and run each federate using a customized runner in multi-process mode. Additionally, the file monitors the federates during runtime and logs all events that occur in each federate into the "Logs" folder. When reading the federate configurations from the "Federates" folder, each configuration file is parsed into an object of FederateConfig.py, which is then used throughout the rest of the process.

In addition, during runtime, we use FlagUtilities.py and TimingUtilities.py to set the flags and timing configurations, respectively.

# Run the code:
Clone the repository then run this command: **python helics.py** you can see all log files in **logs** folder.

