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

from whether import ProcessTreeFileParserException


# ---------- Angular lookup helper ----------

# Angle table for wind cardinal point directions
windDirectionAngle = dict()
a = 0
for d in ["N", "NNE", "NE", "ENE",
          "E", "ESE", "SE", "SSE",
          "S", "SSW", "SW", "WSW",
          "W", "WNW", "NW", "NNW"]:
    windDirectionAngle[d] = a
    a += 360 / 16


# ---------- YAML parser helpers ----------

def onlyDictElement(d, e):
    '''Check that d contains exactly one key, which is e.

    :param d: a dict
    :param e: the only permitted key
    :returns: the value associated with that key
    '''
    ks = d.keys()
    if len(ks) == 0:
        raise ProcessTreeFileParserException(f'No required element {e}')
    elif len(ks) > 1:
        if e not in ks:
            raise ProcessTreeFileParserException(f'No required element {e}')
        else:
            xs = set(ks) - set([e])
            raise ProcessTreeFileParserException(f'Extraneous elements {xs}')
    elif e not in ks:
        raise ProcessTreeFileParserException(f'No required element {e}')
    return d[e]


def onlyDictElements(l, e):
    '''Check that l is a list containing dicts of only one
    key e.

    :param l a list
    :param e: the only permitted element in dicts of the list
    :returns: a list of the values associated with that key
    '''
    es = list(map(lambda d: onlyDictElement(d, e), l))
    return es




def angleForDirection(d):
    '''Return the angle corresponding to the given cardinal direction.

    :param d: the cardinal point as a string
    :returns: the angle'''
    return windDirectionAngle[d]


def modalTagValue(evs, tag):
    '''Compute the modal value associated with the given tag,
    which really needs to be discrete to make sense.

    :param evs: the events
    :param tag: the event tag
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


def meanTagValue(evs, tag):
    '''Compute the mean value associated with the given tag, which
    needs to be numeric to make sense.

    :param evs: the events
    :param tag: the event tag
    :returns: the mean value'''
    v, n = 0.0, 0
    for ev in evs:
        v += ev[tag]
        n += 1
    if n == 0:
        return 0
    else:
        return  v / n

def maxTagValue(evs, tag):
    '''Compute the maximum value associated with the given tag, which
    needs to be numeric to make sense.

    :param evs: the events
    :param tag: the event tag
    :returns: the maximum value'''
    v = 0.0
    for ev in evs:
        v =max(v, ev[tag])
    return  v
