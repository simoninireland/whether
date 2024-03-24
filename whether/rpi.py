# Sensor driver for various Raspberry Pi sensors
#
# Copyright (C) 2023 Simon Dobson
#
# This file is part of whether, a modular IoT weather station
#
# whether is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# whether is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with whether. If not, see <http://www.gnu.org/licenses/gpl.html>.

import os
import re
from whether import Sampler

# Approach to temperature taken from
# https://www.pragmaticlinux.com/2020/06/check-the-raspberry-pi-cpu-temperature/


class RPi(Sampler):
    '''Driver for thr Raspberry Pi's onboard sensors.

    :param settings: settings dict
    '''

    THERMAL_ZONE_FILE = "/sys/class/thermal/thermal_zone0/temp"  #: File for the CPU's thermal zone.
    WIFI_FILE = "/proc/net/wireless"                             #: File for wifi information.

    CPU_TEMPERATURE = "temperature"                              #: Event tag for CPU temperature.
    WIFI_SIGNAL_STRENGTH = "rssi"                                #: Event tag for wifi signal strength.

    def __init__(self, settings):
        super().__init__(settings)

    def sampleTemperature(self):
        '''Return the current CPU temperature.

        :returns: the CPU temperature in C'''
        if os.path.isfile(self.THERMAL_ZONE_FILE):
            with open(self.THERMAL_ZONE_FILE) as fd:
                line = fd.readline().strip()
            if line.isdigit():
                return float(line) / 1000

        # if we get here we can't read the temperature
        return None

    def sampleWifi(self):
        '''Return the current wifi signal strength. By convention
        this is a number between 0 and 70.

        :returns: the signal strength'''
        if os.path.isfile(self.WIFI_FILE):
            lines = []
            with os.popen(f'cat {self.WIFI_FILE}') as f:
                l = f.readlines()

            # tokenise the last line
            tks = re.split(r'\s+', l[-1])

            # compute RSSI
            rssi = int(float(tks[3]))
            return rssi

        # if we get here we can't sample the wifi
        return None

    def sample(self):
        '''Take a sample.

        :returns: a dict'''
        t = self.sampleTemperature()
        s = self.sampleWifi()

        d = {self.CPU_TEMPERATURE: t,
             self.WIFI_SIGNAL_STRENGTH: s}
        return d
