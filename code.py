# Master weather station script
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
import board
import adafruit_logging as logging
from whether import RingBuffer, logger, DHT22, Anemometer

# Set the logger
logger.setLevel(logging.DEBUG)

async def main():
    # Create the ring buffers
    thbuf = RingBuffer(100)
    wsbuf = RingBuffer(100)

    # Create the sensors
    th = DHT22('temperature-humidity', board.D4, thbuf, 2)
    ws = Anemometer('windspeed', board.D17, wsbuf, 2)

    # Start the coroutines
    tht = asyncio.create_task(th.run())
    wst = asyncio.create_task(ws.run())
    await asyncio.gather(tht, wst)

asyncio.run(main())
