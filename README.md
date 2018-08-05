# brewerslabng

This project is a clean-reworking of [Brewerslab](https://github.com/allena29/brewerslab) which is looking to provide an datamodel and associated implementation for a small brewery.

The data for the brewery will use a strong data model (YANG), and will use [**PyConfHoard**](pyconfhoard/README.md) to store and manage the data.


## Setup

1. [Raspberry PI Basic Setup](Documentation/RaspberryPi.md)


## Hardware 

- Raspberry Pi 
- DS18B20 - 1 Wire Temperature Probes



# Given, When, Then - Tests

The best way to see how this project and code behaves is by running the approval testing, this will run through a set of tests. This will create a datastore will be created in a temporary directory and removed after the test is compelted. 

The test harness follows Behaviour Driven Development approach which ensures asserts conditions in response to certain actions.

The testharness will create and remove artefacts under a fresh (unique) directory under `/tmp`. At the end of all tests (including failures) this directory will be cleaned up.

```bash
behave

Creating datastore in a temporary directory... /tmp/tmpypyzbx1g
Launching Rest Server....
[2018-06-17 00:53:29 +0100] [25815] [INFO] Starting gunicorn 19.7.1
[2018-06-17 00:53:29 +0100] [25815] [INFO] Listening at: http://127.0.0.1:8599 (25815)
[2018-06-17 00:53:29 +0100] [25815] [INFO] Using worker: sync
[2018-06-17 00:53:29 +0100] [25835] [INFO] Booting worker with pid: 25835
Feature: Basic Setup of the Brewrey # features/00_hardware_setup.feature:1

  Scenario: Create Temperature Probes  # features/00_hardware_setup.feature:3
    When we send the following CLI     # features/steps/cli_steps.py:13 0.000s
      """
      configure
      create brewhouse temperature hardware probe 28-000hlt
      commit
      """

Feature: Heat-Mash-Water # features/05_heat_mash_water.feature:1

  Scenario: Simple Mash Heating the water                      # features/05_heat_mash_water.feature:3
    Given We set the HLT temperature for the mash to 69.0 degC # features/steps/cli_steps.py:23 0.000s

Feature: Mash # features/10_mash.feature:1

  Scenario: Simple Mash Heating the water                      # features/10_mash.feature:3
    Given We set the HLT temperature for the mash to 69.0 degC # features/steps/cli_steps.py:23 0.000s

Closing Rest Server....
Removing datastore from temporary directory
[2018-06-17 00:53:34 +0100] [25835] [INFO] Worker exiting (pid: 25835)
[2018-06-17 00:53:34 +0100] [25815] [INFO] Handling signal: term
3 features passed, 0 failed, 0 skipped
3 scenarios passed, 0 failed, 0 skipped
3 steps passed, 0 failed, 0 skipped, 0 undefined
Took 0m0.000s
[2018-06-17 00:53:34 +0100] [25815] [INFO] Shutting down: Master
```

It is also possible to run the test harness with a pre-existing datastore/rest server with the environment variable `env PYCONF_DATASTORE=/tmp/datastore` - the contents of the datastore will remain.

To start a rest server with you can use, this will remove anything left over in /tmp/datastore. When launching the REST server in throwaway mode we don't actually remove the data afterwards - however in most systems we expect that `/tmp/` would be destroyed on reboot.

```
# Terminal 1 - this will listen on port 8599
launch --throwaway

# Terminal 2
set -g -x PYCONF_PORT 8599
set -g -x PYCONF_DATASTORE /tmp/datastore 
behave
```

Sometimes it is good to rule out the test harness

```
# Terminal 1 - this will listen on port 8600
./launch --rest

# Terminal 2 - a thing
set -g -x PYCONF_DATASTORE /tmp/datastore/
set -g -x FAKE_DS18B20_RESULT_DIR /tmp/1wire
./launch --thing things/temperature/TemperatureProviderDs18B20.py

# Terminal 3
set -g -x PYCONF_PORT 8599
set -g -x PYCONF_DATASTORE /tmp/datastore 
./launch --cli
conf
set brewhouse temperature mash setpoint 67
commit
```


# Things

## Temperature Monitoring (DS18B20 1-Wire Sensors)

The temperature monitor uses 1-wire DS18B20 probes, which write their data into `/sys/bus/w1/devices/28-0415014ba0ff/w1_slave` in a simple text format. Each probe has a unique burned-in ID (e.g. 0415014ba0ff in this case), if multiple probes are present a unique directory for each probe will be created and each will have a w1\_slave file instide. The contents of the w1\_slave file is as below. 

If the CRC checksum for the reading is not valid we will see NO at the end of the first line. It shoudl be noted that we can receive results with a CRC checksum which is correct but the temperature reading itself is not correct. In many cases 85000 appears. 

The temperature itself is shown on the end of the second line, in this case the result would have been 16.625degC.


> 0a 01 55 00 7f ff 0c 10 64 : crc=64 YES  
> 0a 01 55 00 7f ff 0c 10 64 t=16625



```bash
# Launching - with real hardware
./launch --thing things/temperature/TemperatureProviderDs18B20.py

# Launching - with FAKE directories.
set -g -x PYCONF_DATASTORE /tmp/datastore/
set -g -x FAKE_DS18B20_RESULT_DIR /tmp/1wire
./launch --thing things/temperature/TemperatureProviderDs18B20.py
```



