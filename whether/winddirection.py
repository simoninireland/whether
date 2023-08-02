# Sensor driver for a resistoir network wind direction sensor
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
import board
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
from whether import Sampler


class WindDirection(Sampler):
    '''Driver for a resistor network wind direction sensor. The
    sensor is connected to an analogue-to-digital converter through
    the SPI interface.

    The object takes a calibration table mapping cardinal points to
    raw ADC values that is used to translate the sensor readings
    into meaningful form.

    :param id: the sensor's id
    :param cs: the chip select pin for the SPI device
    :param ch: the a2d channel for the resistor network
    :param cal: calibration table
    :param ring: the ring buffer to receive events
    :param period: the reporting period

    '''

    DIRECTION = "winddir"    #: Event tag for wind direction as a string.
    RAW = "windrawadc"       #: Event tag for raw ADC value.


    def __init__(self, id, cs, ch, cal, ring, period = 1):
        super().__init__(id, ring, period)

        # calibration data
        self._calibration = cal

        # SPI interface (assumed to be SPI0)
        self._spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
        self._cs = digitalio.DigitalInOut(cs)

        # create the MCP3008
        self._mcp = MCP.MCP3008(self._spi, self._cs)

        # resistor network channel
        self._channel = AnalogIn(self._mcp, ch)

    def direction(self, r):
        '''Return the wind direction.

        :param r: the raw wind direction reading
        :returns: a pair of a direction string and a rotation in degrees'''

        # extract the nearest matching raw value
        bestMatch, bestDirection = None, None
        for (d, v) in self._calibration.items():
            diff = abs(r - v)
            if (bestMatch is None) or (diff < bestMatch):
                bestMatch, bestDirection = diff, d

        # return the best direction
        return bestDirection

    def sample(self):
        '''Take a sample from the sensor.

        :returns: a dict'''
        r = self._channel.value
        return {self.DIRECTION: self.direction(r),
                self.RAW: r}
