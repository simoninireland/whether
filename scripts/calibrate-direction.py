#!/bin/env python

from sys import exit
from datetime import datetime
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D5)
mcp = MCP.MCP3008(spi, cs)

channel = AnalogIn(mcp, MCP.P0)

fn = "winddirectioncalibration.py"
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

exit(0)
