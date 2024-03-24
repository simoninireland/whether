# Sensor driver for a tipping-bucker rain gauge
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


class Raingauge(Counter):
    '''Driver for a tipping-bucket rain gauge. Each tick of the switch
    corresponds to a single emptying of the bucket.

    :param settings: settings dict
    '''

    RAININTENSITY = "rainfall"                 #: Event tag for rain intensity in mm/h.

    # One tip represents 0.2794mm
    TIPRAINFALL = 0.2794 * (60 * 60)           #: Rainfall in mm/h corresponding to one tip/s.

    def __init__(self, settings):
        super().__init__(settings)

    def rainfall(self, n, dt):
        '''Return the rainfall intensity indicated by n counts in the period dt.

        :param n: the number of counts
        :param dt: the elapsed time
        :returns: the rainfall intensity'''
        return (self.TIPRAINFALL * n) / dt

    def sample(self):
        '''Convert the count into rainfall intensityevent.

        :returns: a dict'''
        c = self.count()
        r = self.rainfall(c, self.period())
        return {self.RAININTENSITY: r}
