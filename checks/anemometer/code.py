# Wiring check for the reed-switch anemometer
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

# Very much guided by code from Adafruit
# https://learn.adafruit.com/key-pad-matrix-scanning-in-circuitpython/keys-one-key-per-pin

# We use the keypad driver to get debouncing, because to magnetic
# reed switch is sometimes noisy

import time
import board
import keypad
import digitalio

# GPIO10 for the magnetic reed switch
#key = keypad.Keys([board.GP17], value_when_pressed=True, pull=False)
# key = keypad.Keys([board.D17], value_when_pressed=True, pull=False)

# count = 0
# while True:
#     event = key.events.get()
#     if event and event.pressed:
#         count += 1
#         print(f"interrupted! ({count})")
#     time.sleep(1)

reed = digitalio.DigitalInOut(board.D17)
reed.direction = digitalio.Direction.INPUT

count = 0
state = reed.value
print(state)
while True:
    trigger = reed.value
    print(trigger)
    if (not state) and trigger:
        state = True
        count += 1
        print(f"interrupted! ({count})")
    elif state and (not trigger):
        state = False
        print("Drop")
    time.sleep(0.1)
