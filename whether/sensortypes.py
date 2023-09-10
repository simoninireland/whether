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

    The settings should include at least the following values:

    - id: a unique id for the sensor
    - period: the reporting period in seconds

    Sub-classes may add other settings.

    :param settings: dict of settings
    '''

    TIMESTAMP = "time"  #: Event tag for timestamp, in Unix epoch seconds.
    ID = "id"           #: Event tage for the sensor id.


    def __init__(self, settings):
        self._id = settings.get('id')
        self._period = settings.get('period')
        self._rings = []


    # ---------- Helper methods ----------

    @staticmethod
    def boardPinFromName(pin):
        '''Expand the pin name using board module. This lets us
        use names like "D14" in settings that are expanded to
        "board.D14" for use in code.

        :param pin: the pin name
        :returns: the pin object'''
        module = __import__('board')
        p = module.__dict__[pin]
        return p


    # ---------- Access ----------

    def id(self):
        '''Return the sensor's identifier.

        :returns: the sensor id'''
        return self._id

    def addOutput(self, ring):
        '''Add a ring buffer to which the sensor sends samples.

        :param ring: the ring buffer'''
        self._rings.append(ring)

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
        '''Push an event to the sensor's ring buffers.

        :param ev: the event'''
        for ring in self._rings:
            ring.push(ev)


    # ---------- Coroutine interface ----------

    async def run(self):
        '''Coroutine to run the sensor.'''
        raise NotImplementedError("run")


class Sampler(Sensor):
    '''A sensor that takes a single sample once in event period.

    :param settings: dict of settings
    '''

    def __init__(self, settings):
        super().__init__(settings)


    # ---------- Coroutine interface ----------

    async def run(self):
        '''Coroutine to take a sample every period and place
        the data into the sensor's ring buffer.'''
        while True:
            try:
                # construct the event
                ev = self.sample()
                if ev is not None:
                    ev[self.TIMESTAMP] = time.time()
                    ev[self.ID] = self.id()

                    # push into the sensor's ring buffer
                    self.pushEvent(ev)
                    logger.debug('Sensor {id} pushed sample {ev}'.format(id=self.id(),
                                                                         ev=ev))
            except Exception as err:
                logger.error("{id}: {e}".format(id=self.id(),
                                                e=err))

            # wait for the next period
            await asyncio.sleep(self.period())


class Counter(Sensor):
    '''A sensor that counts transitions on a pin.

    A counter monitors a GPIO pin looking for rising edges. When it
    sees one it calls its :meth:`edge` to record the event.

    The settings should include at least the following values:

    - gpio: the GPIO pin to count pulses in
    - rising: True (the default) to count rising pulses, False to count falling pulses
    - counting_period: the counting (polling) period (defaults to 10ms)

    Sub-classes may add other settings.

    :param settings: dict of settings
    '''

    COUNT = "count"     #: Event tag for the count.


    def __init__(self, settings):
        super().__init__(settings)
        self._pin = self.boardPinFromName(settings.get('gpio'))
        self._rising = settings.get('rising', True)
        self._polling = settings.get('counting_period', 0.01)

        # debouncing
        self._key = keypad.Keys([self._pin], value_when_pressed=self._rising, pull=False)

        # counter state
        self._count = 0           # initial count

    def pin(self):
        '''Returns the GPIO pin being sampled.

        :returns: the pin'''
        return self._pin

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

            try:
                # post the event
                ev = self.sample()
                if ev is not None:
                    ev[self.TIMESTAMP] = time.time()
                    ev[self.ID] = self.id()

                    # push into the sensor's ring buffer
                    self.pushEvent(ev)
                    logger.debug(f'Sensor {self.id()} pushed count {ev}')
            except Exception as err:
                logger.error(f'{self.id()}: {err}')

            # reset the counter
            self.reset()

    async def run(self):
        '''Coroutine to start the sampling and reporting coroutines.'''
        pt = asyncio.create_task(self.polling())
        rt = asyncio.create_task(self.reporting())
        await asyncio.gather(pt, rt)
