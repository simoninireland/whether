# Calibration script for wind direction sensor
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

from datetime import datetime
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

# A2D input is on SPI0
spi = busio.SPI(clock=board.GP2, MISO=board.GP4, MOSI=board.GP3)
cs = digitalio.DigitalInOut(board.GP5)

# create the MCP3008
mcp = MCP.MCP3008(spi, cs)

# resistor network is on channel 0 of the MCP3008
channel = AnalogIn(mcp, MCP.P0)

fn = "windDirections.py"
sensitivity = 0.04
directions = ["N", "NNE", "NE", "ENE",
              "E", "ESE", "SE", "SSE",
              "S", "SSW", "SW", "WSW",
              "W", "WNW", "NW", "NNW"]

# get the starting position
input("Position the wind direction sensor pointing North, and hit <Return>")
print("Rotate the sensor slowly clockwise (when viewed from above) for one rotation")
print("Make sure that the values change when the vane is in the right direction")

values = {}

# read the initial (north) value
v = channel.value
values[directions[0]] = v
print("{dir}: {val}".format(dir=directions[0], val=v))

# read the rest
for i in range(1, len(directions)):
    # wait for the value to change by the sensitivity
    while True:
        vnow = channel.value
        if abs(v - vnow) > v * sensitivity:
            break

    # we have a new value
    v = vnow
    values[directions[i]] = v
    print("{dir}: {val}".format(dir=directions[i], val=v))

# check we get back to North at the right point
while True:
    vnow = channel.value
    if abs(v - vnow) > v * sensitivity:
        break
print("{dir}: {val}".format(dir=directions[0], val=vnow))
if abs(vnow - values[directions[0]]) > vnow * sensitivity:
    print("Hmmm... we didn't seem to return to North")
    exit(1)

# write out the calibrated constants
ts = datetime.now()
with open(fn, "w") as fh:
    # add header
    print("# windDirections.py: Wind direction sensor calibration values", file=fh)
    print(f"# Collected {ts}", file=fh)
    print("", file=fh)

    # output the calibration values
    print("windDirections = dict(", file=fh)
    for i in range(len(directions)):
        dir = directions[i]
        val = values[dir]
        print(f"   {dir}={val},", file=fh)
    print(")", file=fh)
    print(f"windDirectionSensitivity = {sensitivity}", file=fh)
print(f"The calibration values have been written to {fn}")
