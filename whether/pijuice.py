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

    Settings may also include:

    - i2c: the I2C interface the PiJuice os attached to (defaults to 1)
    - i2c_addr: the I2C slave address for the PiJuice (defaults to 0x14)

    :param settings: settings dict
    '''

    BATTERY_STATUS = "status"              #: Event tag for battery status.
    BATTERY_CHARGE_PERCENTAGE = "charge"   #: Event tag for battery charge percentage.
    BATTERY_TEMPERATURE = "temperature"    #: Event tag for battery temperature.
    BATTERY_VOLTAGE = "voltage"            #: Event tag for battery voltage in mV.
    BATTERY_CURRENT = "current"            #: Event tag for battery current in mA.


    def __init__(self, settings):
        super().__init__(settings)
        i2c = settings.get('i2c', 1)
        i2c_addr = settings.get('i2c_addr', 0x14)
        self._pijuice = pijuice.PiJuice(i2c, i2c_addr)

    def sample(self):
        '''Take a sample from the bettery.

        :returns: a dict'''
        return {self.BATTERY_STATUS: self._pijuice.status.GetStatus()['data']['battery'],
                self.BATTERY_CHARGE_PERCENTAGE: self._pijuice.status.GetChargeLevel()['data'],
                self.BATTERY_TEMPERATURE: self._pijuice.status.GetBatteryTemperature()['data'],
                self.BATTERY_VOLTAGE: self._pijuice.status.GetBatteryVoltage()['data'],
                self.BATTERY_CURRENT: self._pijuice.status.GetBatteryCurrent()['data']}
