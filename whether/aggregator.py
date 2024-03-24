# Aggregators
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

import json
from whether import logger, onlyDictElement, onlyDictElements


class Channel:
    '''A channel of aggregated data.

    Settings should contain:

    - id: the channel id
    - source: the sensor id the channel aggregates
    - index: (optional) the element within the reported results tuple
    - report: a list of values

    :param settings: settings dict
    '''

    def __init__(self, settings):
        self._id = settings['id']
        self._source = settings['source']
        self._values = {}

        self._parseReportedValues(onlyDictElements(settings['report'], 'value'))

    def _parseReportedValues(self, vds):
        '''Parse and create reported values from the list of descriptions.

        :param vds: the value descriptions'''
        for vd in vds:
            v = ReportedValue(vd)
            self.append(self._values, v)


class ReportedValue:
    '''A reported value.

    Settings should include:

    - name: the name of the value
    - operator: the aggregation operator to apply

    :param settings: settings dict
    '''

    def __int__(self, settings):
        self._id = settings['id']
        self._operator = settings['operator']


class Aggregator:
    '''Base class for aggregators.

    Aggregators take streams of sensor observations and produce
    summarised reports to be uploaded by reporters.

    The settings should include at least the following values:

    - period: the reporting period in seconds
    - channels: a list of channel specifiers

    Sub-classes may add other settings.

    :param settings: settings dict
    '''

    def __init__(self, settings):
        self._period = settings.get('period')
        self._rings = []
        self._channels = {}

        self._parseChannels(onlyDictElements(settings['channels'], 'channel'))

    def _parseChannels(self, chds):
        '''Parse and create channels from the list of descriptions.

        :param chds: the channel descriptions'''
        for chd in chd:
            ch = Channel(chd)
            self.append(self._channels, ch
