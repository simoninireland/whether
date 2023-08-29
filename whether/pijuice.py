# Sensor driver for the PiJuice battery HAT
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

from whether import Sampler
import pijuice


class PiJuice(Sampler):
    '''Driver for a PiJuice power HAT.

    :param id: sensor identifier
    :param ring: the ring buffer
    :param period: the sampling perdiod in seconds
    '''

    BATTERY_STATUS = "status"              #: Event tag for battery status.
    BATTERY_CHARGE_PERCENTAGE = "charge"   #: Event tag for battery charge percentage.
    BATTERY_TEMPERATURE = "temperature"    #: Event tag for battery temperature.
    BATTERY_VOLTAGE = "voltage"            #: Event tag for battery voltage in mV.
    BATTERY_CURRENT = "current"            #: Event tag for battery current in mA.


    def __init__(self, id, ring, period = 1):
        super().__init__(id, ring, period)
        self._pijuice = pijuice.PiJuice(1, 0x14)

    def sample(self):
        '''Take a sample from the bettery.

        :returns: a dict'''
        return {self.BATTERY_STATUS: self._pijuice.status.GetStatus()['data']['battery'],
                self.BATTERY_CHARGE_PERCENTAGE: self._pijuice.status.GetChargeLevel()['data'],
                self.BATTERY_TEMPERATURE: self._pijuice.status.GetBatteryTemperature()['data'],
                self.BATTERY_VOLTAGE: self._pijuice.status.GetBatteryVoltage()['data'],
                self.BATTERY_CURRENT: self._pijuice.status.GetBatteryCurrent()['data']}
