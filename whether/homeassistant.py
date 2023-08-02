# Uploader for Home Assistant
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

import adafruit_requests
from whether import angleForDirection, modalTagValue, meanTagValue


class HomeAssistant:
    '''Reporter for uploading dfata to a Home Assistant server.

    :param api: API endpoint
    :param token: API token
    :param sensors: dict mapping keys to sensors
    '''

    # Sensor type keys
    TEMPERATURE = "t"        #: Temperature sensor.
    HUMIDITY = "h"           #: Humidity sensor
    WINDSPEED = "ws"         #: Windspeed sensor.
    WINDDIRECTION = "wd"     #: Wind direction sensor.


    def __init__(self, api, token, sensors):
        super().__init__()
        self._api = api
        self._token  = token
        self._sensors = sensors

    def payload(self):
        '''Create the payload for the upload.

        :returns: a dict'''
        payload = dict()

        # temperature
        w = self._sensors[self.TEMPERATURE],
        d = meanTagValue(t.events(), t.TEMPERATURE)
        payload['sensor.winddir'] = d

        # humidity

        # windspeed

        # wind direction
        wd = self._sensors[self.WINDDIRECTION],
        d = modalTagValue(wd.events(), wd.DIRECTION)
        payload['sensor.winddir'] = d
        payload['sensor.winddeg'] = angleForDirection(d)
