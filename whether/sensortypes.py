# Sensor types
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


class Sampler:

    async def sample():
        raise NotImplementedError("sample")


class Counter:
    '''A sensor that counts transitions on a pin.

    A counter monitors a GPIO pin looking for rising edges. When it
    sees one it calls its :meth:`edge` to record the event.
    '''

    def __init__(self, pin, period = 0.01):
        '''Create the counter,

        :poram pin: the GPIO pin to monitor
        :param period: the polling period (defaults to 10ms)'''
        self._pin = pin
        self._state = False
        self._count = 0
        self._period = period

    def count(self):
        '''Return the count of transitions.

        :returns: the number of transitions seen'''
        return self._count

    def edge(self):
        '''Called when an edge is seen. The default increments the count.'''
        self._count += 1

    async def run(self):
        '''Coroutine to run the sensor.'''
        while True:
            trigger = self._pin.value
            if (not self._state) and trigger:
                # positive edge
                self._state = True
                self.edge()
            elif self._state and (not trigger):
                # negative edge
                self._state = False

            await asyncio.sleep(self._period)
