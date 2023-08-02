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


def modalTagValue(self, tag, evs):
    '''Compute the modal value associated with the given tag,
    which really needs to be discrete to make sense.

    :param tag: the event tag
    :param evs: the events
    :returns: the modal value'''
    values = dict()
    modalCount, modalValue = None, None
    for ev in evs:
        v = ev[tag]
        if v not in values:
            values[v] = 1
        else:
            values[v] += 1

        # update the mode if needed
        if (modalCount is None) or (values[v] > modalCount):
            modalCount = values[v]
            modalValue = v

    return modalValue


def meanTagValue(self, tag, evs):
    '''Compute the mean value associated with the given tag, which
    needs to be numeric to make sense.

    :param tag: the event tag
    :param evs: the events
    :returns: the mean value'''
    v, n = 0.0, 0
    for ev in evs:
        v += ev[tag]
        n += 1
    return  v / n
