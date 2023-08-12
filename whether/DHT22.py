# Sensor driver for the DHT22 temperature/humidity sensor
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

import asyncio
from whether import Sampler
import adafruit_dht


class DHT22(Sampler):
    '''Driver for a DHT22 temperature and humidity sensor.

    :param id: sensor identifier
    :param pin: the data pin
    :param ring: the ring buffer
    :param period: the sampling perdiod in seconds
    '''

    TEMPERATURE = "temp"   #: Event tag fopr temperature in degrees Celsius.
    HUMIDITY = "hum"       #: Event tag for relative humidity in percent.

    def __init__(self, id, pin, ring, period = 1):
        super().__init__(id, ring, period)
        self._pin = pin
        self._dht = adafruit_dht.DHT22(pin)

    def sample(self):
        '''Take a sample from the sensor.

        :returns: a dict'''
        return {self.TEMPERATURE: self._dht.temperature,
                self.HUMIDITY: self._dht.humidity}
