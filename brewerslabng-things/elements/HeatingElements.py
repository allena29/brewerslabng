#!/usr/bin/python

import os
import re
import time
import PyConfHoard


class HeatingElementProviderSSR(PyConfHoard.Thing):

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

    def start(self):
        print('null')


class Launch:

    def __init__(self, start=False):
        try:
            self.thing = HeatingElementProviderSSR('HeatingElementProvider', 'brewerslab', '/brewhouse/power/heating')
            if start:
                self.thing.start()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    Launch()
