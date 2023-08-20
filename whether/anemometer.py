# Sensor driver for a rotation-counting anemometer
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

from whether import Counter


class Anemometer(Counter):
    '''Driver for a reed switch anemometer. Each tick of the switch
    corresponds to a single rotation of the gauge.

    :param id: the sensor's id
    :param pin: the GPIO pin of the reed switch
    :param ring: the ring buffer to receive events
    :param period: the reporting period
    '''

    WINDSPEED = "windspeed"                 #: Event tag for windspeed in m/s.

    # One rotation per second indicates a windpseed of 2.4km/h
    SPEEDPERROTATION = 2400 / (60 * 60)    #: Windspeed in m/s corresponding to one rotation/s.

    def __init__(self, id, pin, ring, period = 1):
        super().__init__(id, pin, ring, period)

    def speed(self, n, dt):
        '''Return the windspeed indicated by n counts in the period dt.

        :param n: the number of counts
        :param dt: the elapsed tim
        :returns: the windspeed'''
        return (self.SPEEDPERROTATION * n) / dt

    def sample(self):
        '''Convert the count into a windspeed event.

        :returns: a dict'''
        c = self.count()
        s = self.speed(c, self.period())
        return {self.WINDSPEED: s}
