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
from whether import Sampler

# Approach taken from
# https://www.pragmaticlinux.com/2020/06/check-the-raspberry-pi-cpu-temperature/


class RPi(Sampler):
    '''Driver for thr Raspberry Pi's onboard sensors.

    :param id: sensor identifier
    :param ring: the ring buffer
    :param period: the sampling perdiod in seconds
    '''

    THERMAL_ZONE_FILE = "/sys/class/thermal/thermal_zone0/temp"  #: File for the CPU's thermal zone.
    CPU_TEMPERATURE = "temperature"                              #: Event tag for CPU temperature.


    def __init__(self, id, ring, period = 1):
        super().__init__(id, ring, period)

    def sample(self):
        '''Take a sample.

        :returns: a dict'''
        cput = 0.0
        if os.path.isfile(self.THERMAL_ZONE_FILE):
            with open(self.THERMAL_ZONE_FILE) as fd:
                line = fd.readline().strip()
            if line.isdigit():
                cput = float(line) / 1000

        return {self.CPU_TEMPERATURE: cput}
