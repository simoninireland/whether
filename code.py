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

from os import environ
import asyncio
from dotenv import load_dotenv
import board

import adafruit_mcp3xxx.mcp3008 as MCP
import adafruit_logging as logging
from whether import RingBuffer, logger, DHT22, Anemometer, WindDirection, Raingauge, PiJuice, RPi, HomeAssistant

# Load calibration of the wind direction resistor network
from winddirectioncalibration import windDirections

# Pin settings for Raspberry Pi
TempHumPin = board.D4    # DHT22
WindPin = board.D17      # Anemometer reed switch
WindDirPin = board.D5    # Wind direction resistor network (also SPI0)
WindDirChannel = MCP.P0  # Wind direction channel
RainPin = board.D27      # Rain gauge reed switch

# Load the credentials and configuration information  we need
load_dotenv()

# Set the logger
loglevel = environ.get('LOGLEVEL', None)
if loglevel is not None:
    # look up the log level
    level = 0
    if loglevel.isdigit():
        level = loglevel
    else:
        # Adafruit's logging doesn't allow strings as levels
        loglevel = loglevel.lower()
        for (v, l) in logging.LEVELS:
            if l.lower() == loglevel:
                level = v
                break
    logger.setLevel(level)

async def main():
    # Create the sensor ring buffers
    thbuf = RingBuffer(100)
    wsbuf = RingBuffer(100)
    wdbuf = RingBuffer(100)
    rgbuf = RingBuffer(100)
    pjbuf = RingBuffer(100)
    rpbuf = RingBuffer(100)

    # Create the sensors
    th = DHT22('temperature-humidity', TempHumPin, thbuf, 10)
    ws = Anemometer('windspeed', WindPin, wsbuf, 1)
    wd = WindDirection('wind-direction', WindDirPin, WindDirChannel, windDirections, wdbuf, 1)
    rg = Raingauge('rainfall', RainPin, rgbuf, 1)
    pj = PiJuice('pi-juice', pjbuf, 10)
    rp = RPi('pi', rpbuf, 10)

    # Create the reporter
    ha = HomeAssistant(environ["MQTT_SERVER"], environ["MQTT_USERNAME"], environ["MQTT_PASSWORD"],
                       "homeassistant/sensor/whether/state",
                       {HomeAssistant.TEMPERATURE: th,
                        HomeAssistant.HUMIDITY: th,
                        HomeAssistant.WINDSPEED: ws,
                        HomeAssistant.WINDDIRECTION: wd,
                        HomeAssistant.RAININTENSITY: rg,
                        HomeAssistant.BATTERY: pj,
                        HomeAssistant.CPU: rp},
                       period=30)

    # Start the coroutines
    tht = asyncio.create_task(th.run())
    wst = asyncio.create_task(ws.run())
    wdt = asyncio.create_task(wd.run())
    rgt = asyncio.create_task(rg.run())
    pjt = asyncio.create_task(pj.run())
    rpt = asyncio.create_task(rp.run())
    hat = asyncio.create_task(ha.run())
    await asyncio.gather(tht, wst, wdt, rgt, pjt, rpt, hat)

asyncio.run(main())
