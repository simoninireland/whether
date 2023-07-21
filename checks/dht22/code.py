# Wiring check for the DHT22
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

# DHT22 check strongly based on code from Adafruit
# https://learn.adafruit.com/dht/dht-circuitpython-code

import time
import board
import adafruit_dht

# GPIO10 for the I2C input
dht = adafruit_dht.DHT22(board.GP10)

while True:
    try:
        # query the sensor
        temperature = dht.temperature
        humidity = dht.humidity

        # print results to serial terminal
        print("Temp: {:.1f} *C \t Humidity: {}%".format(temperature, humidity))
    except RuntimeError as e:
        print("Reading from DHT failure: ", e.args)

    time.sleep(1)
