# Utility functions
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


# Angle table for wind cardinal point directions
windDirectionAngle = dict()
a = 0
for d in ["N", "NNE", "NE", "ENE",
          "E", "ESE", "SE", "SSE",
          "S", "SSW", "SW", "WSW",
          "W", "WNW", "NW", "NNW"]:
    windDirectionAngle[d] = a
    a += 360 / 16


def angleForDirection(d):
    '''Return the angle corresponding to the given cardinal direction.

    :param d: the cardinal point as a string
    :returns: the angle'''
    return windDirectionAngle[d]
