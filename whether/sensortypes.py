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

import time
import asyncio
import keypad
from whether import logger


class Sensor:
    '''A sensor.

    Sensors are intended to be used as coroutines, running autonomously
    to collect data. Each sensor is associated with a ring buffer and a
    reporting periods, and should report an event to the buffer at the
    end of each period. (This doesn't have to happen, and some sensors
    may decide not to report if nothing has happened.)

    :param id: a unique id
    :param ring: the ring buffer to receive events
    :param period: reporting period in seconds (defaults to 1s)
    '''

    TIMESTAMP = "time"  #: Event tag for timestamp, in Unix epoch seconds.
    ID = "id"           #: Event tage for the sensor id.


    def __init__(self, id, ring, period = 1):
        self._id = id
        self._ring = ring
        self._period = period

    def id(self):
        '''Return the sensor's identifier.

        :returns: the sensor id'''
        return self._id

    def ring(self):
        '''Return the ring buffer the sensor reports to.

        :returns: the ring buffer'''
        return self._ring

    def period(self):
        '''Return the sensor's sensing period.

        :returns: a time in seconds'''
        return self._period

    def sample(self):
        '''Take a sample, returning an event. This method must be
        overridden by sub-classes.

        :returns: a dict'''
        raise NotImplementedError("sample")

    def pushEvent(self, ev):
        '''Push an event to the sensor's ring buffer.

        :param ev: the event'''
        self.ring().push(ev)


    # ---------- Coroutine interface ----------

    async def run(self):
        '''Coroutine to run the sensor.'''
        raise NotImplementedError("run")


class Sampler(Sensor):
    '''A sensor that takes a single sample once in event period.

    :param id: the sensort's identifier
    :param ring: the ring buffer for reporting events
    :param period: the reporting period, which is the same as the reporting period'''

    def __init__(self, id, ring, period = 1):
        super().__init__(id, ring, period)


    # ---------- Coroutine interface ----------

    async def run(self):
        '''Coroutine to take a sample every period and place
        the data into the sensor's ring buffer.'''
        while True:
            # construct the event
            ev = self.sample()
            if ev is not None:
                ev[self.TIMESTAMP] = time.time()
                ev[self.ID] = self.id()

                # push into the sensor's ring buffer
                self.pushEvent(ev)
                logger.debug('Sensor {id} pushed sample {ev}'.format(id=self.id(),
                                                                     ev=ev))

            # wait for the next period
            await asyncio.sleep(self.period())


class Counter(Sensor):
    '''A sensor that counts transitions on a pin.

    A counter monitors a GPIO pin looking for rising edges. When it
    sees one it calls its :meth:`edge` to record the event.

    :param id: sensor identifier
    :poram pin: the GPIO pin to monitor
    :param ring: the ring buffer
    :param period: the reporting period (defaults to 1s)
    :param rising: count rising or falling edges (defaults to True)
    :param polling: the polling period (defaults to 10ms)
    '''

    COUNT = "count"     #: Event tag for the count.


    def __init__(self, id, pin, ring,
                 period = 1,
                 rising = True, polling = 0.01):
        super().__init__(id, ring, period)
        self._pin = pin
        self._rising = rising
        self._polling = polling

        # debouncing
        self._key = keypad.Keys([pin], value_when_pressed=rising, pull=False)

        # counter state
        self._count = 0           # initial count

    def count(self):
        '''Return the count of transitions.

        :returns: the number of transitions seen'''
        return self._count

    def reset(self):
        '''Reset the counter.'''
        self._count = 0

    def edge(self):
        '''Called when an edge is seen. The default increments the counter.'''
        self._count += 1

    def sample(self):
        '''Create an event corresponding to the count.

        :returns: a dict'''
        ev = {self.COUNT: self.count()}
        return ev


    # ---------- Coroutine interface ----------

    async def polling(self):
        '''Coroutine to run the sensor's counting loop.'''
        while True:
            event = self._key.events.get()
            if event and event.pressed:
                # detected an edge of the right sense
                self.edge()

            await asyncio.sleep(self._polling)

    async def reporting(self):
        '''Coroutine to report events at each period.'''
        while True:
            # wait for the next sampling period
            await asyncio.sleep(self.period())

            # post the event
            ev = self.sample()
            if ev is not None:
                ev[self.TIMESTAMP] = time.time()
                ev[self.ID] = self.id()

                # push into the sensor's ring buffer
                self.pushEvent(ev)
                logger.debug('Sensor {id} pushed count {ev}'.format(id=self.id(),
                                                                    ev=ev))
            # reset the counter
            self.reset()


    async def run(self):
        '''Coroutine to start the sampling and reporting coroutines.'''
        pt = asyncio.create_task(self.polling())
        rt = asyncio.create_task(self.reporting())
        await asyncio.gather(pt, rt)
