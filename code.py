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
from whether import RingBuffer, logger, DHT22, Anemometer, WindDirection, Raingauge, HomeAssistant

# Load calibration of the wind direction resistor network
from winddirectioncalibration import windDirections

# Pin settings for Raspberry Pi
TempHumPin = board.D4    # DHT22
WindPin = board.D17      # Anemometer reed switch
WindDirPin = board.D5    # Wind direction resistor network (also SPI0)
WindDirChannel = MCP.P0  # Wind direction channel
RainPin = board.D27      # Rain gauge reed switch

# Set the logger
logger.setLevel(logging.DEBUG)

# Load the credentials we need
load_dotenv()

async def main():
    # Create the sensor ring buffers
    thbuf = RingBuffer(100)
    wsbuf = RingBuffer(100)
    wdbuf = RingBuffer(100)
    rgbuf = RingBuffer(100)

    # Create the sensors
    th = DHT22('temperature-humidity', TempHumPin, thbuf, 1)
    ws = Anemometer('windspeed', WindPin, wsbuf, 1)
    wd = WindDirection('wind-direction', WindDirPin, WindDirChannel, windDirections, wdbuf, 1)
    rg = Raingauge('rainfall', RainPin, rgbuf, 1)

    # Create the reporter
    ha = HomeAssistant(environ["MQTT_SERVER"], environ["MQTT_USERNAME"], environ["MQTT_PASSWORD"],
                       "homeassistant/sensor/whether/state",
                       {HomeAssistant.TEMPERATURE: th,
                        HomeAssistant.HUMIDITY: th,
                        HomeAssistant.WINDSPEED: ws,
                        HomeAssistant.WINDDIRECTION: wd,
                        HomeAssistant.RAININTENSITY: rg},
                       period=5)

    # Start the coroutines
    tht = asyncio.create_task(th.run())
    wst = asyncio.create_task(ws.run())
    wdt = asyncio.create_task(wd.run())
    rgt = asyncio.create_task(rg.run())
    hat = asyncio.create_task(ha.run())
    await asyncio.gather(tht, wst, wdt, rgt, hat)

asyncio.run(main())
