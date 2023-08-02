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
import adafruit_mcp3xxx.mcp3008 as MCP
import adafruit_logging as logging
from whether import RingBuffer, logger, DHT22, Anemometer, WindDirection
from winddirectioncalibration import windDirections

# Pin settings for Raspberry Pi
TempHumPin = board.D4    # DHT22
WindPin = board.D17      # Anemometer reed switch
WindDirPin = board.D5    # Wind direction resistor network (also SPI0)
WindDirChannel = MCP.P0  # Wind direction channel
RainPin = board.D27      # Rain gauge reed switch

# Set the logger
logger.setLevel(logging.DEBUG)

async def main():
    # Create the sensor ring buffers
    thbuf = RingBuffer(100)
    wsbuf = RingBuffer(100)
    wdbuf = RingBuffer(100)

    # Create the sensors
    th = DHT22('temperature-humidity', TempHumPin, thbuf, 2)
    ws = Anemometer('windspeed', WindPin, wsbuf, 2)
    wd = WindDirection('wind-direction', WindDirPin, WindDirChannel, windDirections, wdbuf, 2)

    # Start the coroutines
    tht = asyncio.create_task(th.run())
    wst = asyncio.create_task(ws.run())
    wdt = asyncio.create_task(wd.run())
    await asyncio.gather(tht, wst, wdt)

asyncio.run(main())
