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
from winddirectioncalibration import windDirections


class WindDirection(Sampler):
    '''Driver for a resistor network wind direction sensor. The sensor
    is connected to anMCP3008 analogue-to-digital converter through
    the SPI interface.

    The object takes a calibration table mapping cardinal points to
    raw ADC values that is used to translate the sensor readings
    into meaningful form.

    Settings should include:

    - mcp_select: the chip select pin for the SPI device
    - mcp_channel: the MCP channel for the resistor network

    :param settings: the settings dict
    '''

    DIRECTION = "winddir"    #: Event tag for wind direction as a string.
    RAW = "windrawadc"       #: Event tag for raw ADC value.

    @staticmethod
    def mcpChannelFromName(ch):
        '''Expand the channel name using the MCP module. This lets us
        use names like "P0" in settings that are expanded to
        "MCP.P0" for use in code.

        :param ch: the channel name
        :returns: the channel'''
        module = __import__('adafruit_mcp3xxx.mcp3008')
        channel = module.__dict__[ch]
        return channel

    def __init__(self, settings):
        super().__init__(settings)

        # calibration data
        self._calibration = windDirections

        # SPI interface (assumed to be SPI0)
        self._spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
        self._cs = digitalio.DigitalInOut(settings.get('mcp_select'))

        # create the MCP3008
        self._mcp = MCP.MCP3008(self._spi, self._cs)

        # resistor network channel
        ch = settings.get('mcp_channel')
        self._channel = AnalogIn(self._mcp, self.mcpChannelFromName(ch))

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
