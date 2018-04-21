# brewerslabng

This project is a clean-reworking of [Brewerslab](https://github.com/allena29/brewerslab) which is looking to provide an datamodel and associated implementation for a small brewery.

The data for the brewery will use a strong data model (YANG), and will use [**PyConfHoard**](pyconfhoard/README.md) to store and manage the data.


## Setup

1. [Raspberry PI Basic Setup](Documentation/RaspberryPi.md)


## Hardware 

- Raspberry Pi 
- DS18B20 - 1 Wire Temperature Probes



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
env FAKE_DS18B20_RESULT_DIR=/tmp/1wire ./launch --thing things/temperature/TemperatureProviderDs18B20.py
```


