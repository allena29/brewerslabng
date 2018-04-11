#!/usr/bin/python

import os
import re
import time
import PyConfHoard



class TemperatureProviderDs18B20(PyConfHoard.Thing):

    """
    This is an example of a basic temperature provider with basic logic
    included to filter out known bad results.

    This is the first process to make use of the new pattern of using
    an in-meory data structure (pyangbind) based which is periodically 
    flushed to disk/ramdisk.

    This is an implementation providing temperature measurment for the
    1wrire DS18B20 temperature probes.

    This includes basic logic to filter out known bad results.

    IIn this case the 1wire temperature probes can return spurious readings
    if multiple probes are on the same bus and there is interference -
    typically this means a reading of 85deg C is returned.

    In the use case of the brewery there is never a reading which suddenly
    becomes 85deg C - the boil and heating sparge water may return 85 deg
    but there will be a steady rise/fall in temperature because it takes
    a lot of energy to heat the large of volume of liquor.

    Potentially Tilt Hydrometers could be an alternative provide but I
    would prbably stick with DS18B20 probes even if I went for a Tilt (of
    course that would provide a new SpecificGravityProvider ;-) but nothing
    says we have to care about the temperature it sends us.

    """

    def setup(self):
        self.rxTemp = re.compile("^.*t=(\d+)")

        # odd readings
        self.odd_readings = {}
        self.currentTemperatures = {}

        # we need to supress results of 0 and 85 if they are the instant result
        self.lastResult = {}

        if os.path.exists("simulator"):
            self.one_wire_temp_result_directory = "test/artefacts/sys_bus_w1_devices"
            self.log.warning('Using fake 1wire directory')
        else:
            self.one_wire_temp_result_directory = "/sys/bus/w1/devices/"

    def _reject_result(self, probe, temperature, reason="unspecified"):
        self.odd_readings[probe].append(temperature)
        self.log.info('rejecting result %s %s (reason: %s)' % (probe, temperature, reason))
        self.currentTemperatures[probe] = {'timestamp': time.time(), 'temperature': temperature, 'valid': False}

    def _accept_adjust_and_add_a_reading(self, probe, temperature):
        adjust = 0
        probe_offsets = self.get_config("/hardware/probe[id='%s']/offsets" % (probe))

        for offset in probe_offsets:
            offset_min = float(offset.low)
            offset_max = float(offset.high)
            offset_amount = float(offset.offset)
            if temperature >= offset_min and temperature < offset_max:
                adjust = offset_amount
                temperature = temperature + adjust
                break

        self.log.info("Accepting result %s lastResult %s (Adjusted by %s)" % (temperature, self.lastResult[probe], adjust))
        self.currentTemperatures[probe] = {'timestamp': time.time(), 'temperature': temperature, 'valid': True}
        self.lastResult[probe] = temperature
        self.odd_readings[probe] = []

    def _read_temperature_from_external_probe(self, probe):
        temperature = 0
        probe_reading_ok = False
        text = "NON"

        try:
            o = open("%s/%s/w1_slave" % (self.one_wire_temp_result_directory, probe))
            text = o.readline()
            temp = o.readline()
            o.close()
        except Exception:
            pass

        if text.count("YES") and self.rxTemp.match(temp):		# CRC=NO for failed results
            (temp,) = self.rxTemp.match(temp).groups()
            temperature = float(temp) / 1000
            probe_reading_ok = True

        return (temperature, probe_reading_ok)

    def _get_probes_to_monitor(self):
        probes = []
        for probe in os.listdir(self.one_wire_temp_result_directory):
            if probe[0:2] == "28":
                self.log.debug('Checking if we should monitor %s' % (probe))
                probes.append(probe)
        return probes

    def _error_reading_from_external_temperature_probe(self, probe):
        """
        A reading of exactly 85 can be an error from the 1wire probe.
        This rejects a reading of exactly 85 if the preceeding reading isn't
        close enough.
        """
        if self.lastResult[probe] > 80 and self.lastResult[probe] < 85:
            pass
        elif self.lastResult[probe] > 85:
            pass
        else:
            self._reject_result(probe, 85, '85 indicates mis-read')
            return True
        return False

    def getResult(self):
        self.log.debug('getResult - %s' % (self._get_probes_to_monitor()))
        for probe in self._get_probes_to_monitor():
            # A place to store odd results
            if not self.odd_readings.has_key(probe):
                self.odd_readings[probe] = []

            (temperature, ok) = self._read_temperature_from_external_probe(probe)
            if ok:
                if not self.lastResult.has_key(probe):
                    self.lastResult[probe] = 0

                # Exactly 85 indictes misread
                if temperature == 85 and self._error_reading_from_external_temperature_probe(probe):
                    return

                if (self.lastResult[probe]) == 0 or len(self.odd_readings[probe]) > 5:
                    self._accept_adjust_and_add_a_reading(probe, temperature)
                else:
                    if (temperature > self.lastResult[probe] * 1.05 or
                            temperature < self.lastResult[probe] * 0.95):
                        self._reject_result(probe, temperature, '+/- 55% swing')
                    else:
                        self._accept_adjust_and_add_a_reading(probe, temperature)

                time.sleep(1.0)

    def start(self):
        while True:
            self.getResult()
            time.sleep(1)


if __name__ == '__main__':
    try:
        MONSTER = TemperatureProviderDs18B20('TemperatureProvider', 'brewerslab', '/brewhouse/temperature')
        MONSTER.start()
    except KeyboardInterrupt:
        pass
