# Uploader for Home Assistant
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

#import socketpool
#import adafruit_requests as requests
import json
import asyncio
import requests
import paho.mqtt.client as mqtt
from whether import angleForDirection, modalTagValue, meanTagValue, maxTagValue, logger


class HomeAssistant:
    '''Reporter for uploading data to a Home Assistant server over MQTT.

    :param server: the MQTT server
    :param username: user name
    :param password: password
    :param topic: topic to publish data to
    :param sensors: dict mapping keys to sensors
    :param period: (optional) reporting period in seconds (defaults to 60s)
    '''

    # Sensor type keys
    TEMPERATURE = "t"        #: Temperature sensor.
    HUMIDITY = "h"           #: Humidity sensor
    WINDSPEED = "ws"         #: Windspeed sensor.
    WINDDIRECTION = "wd"     #: Wind direction sensor.
    RAININTENSITY = "r"      #: Rain gauge.
    BATTERY = "b"            #: Battery.
    CPU = 'c'                #: CPU.


    def __init__(self, server, username, password, topic,
                 sensors, period = 60):
        super().__init__()
        self._server = server
        self._username = username
        self._password = password
        self._topic = topic
        self._sensors = sensors
        self._period = period
        self._payload = []

        # connect to MQTT
        self._mqttClient()

        # build the component callback list
        self._makePayloadConstructor()

    def _makePayloadConstructor(self):
        '''Create the sensor components.

        This installs the event handlers for the sensors we have
        installed, and issues MQTT discovery messages for them.'''
        if self.TEMPERATURE in self._sensors:
            self._payload.append((self._sensors[self.TEMPERATURE], self.temperature))
            self._client.publish("homeassistant/sensor/temperature/config",
                                 json.dumps(dict(name="Temperature",
                                                 unique_id="whether-temperature",
                                                 device_class="temperature",
                                                 unit_of_measurement="°C",
                                                 value_template="{{ value_json.temperature }}",
                                                 state_topic=self._topic)))

        if self.HUMIDITY in self._sensors:
            self._payload.append((self._sensors[self.HUMIDITY], self.humidity))
            self._client.publish("homeassistant/sensor/humidity/config",
                                 json.dumps(dict(name="Humidity",
                                                 unique_id="whether-humidity",
                                                 device_class="humidity",
                                                 unit_of_measurement="%",
                                                 value_template="{{ value_json.humidity }}",
                                                 state_topic=self._topic)))

        if self.WINDSPEED in self._sensors:
            self._payload.append((self._sensors[self.WINDSPEED], self.windspeed))
            self._client.publish("homeassistant/sensor/windspeed/config",
                                 json.dumps(dict(name="Wind speed",
                                                 unique_id="whether-windspeed",
                                                 device_class="wind_speed",
                                                 unit_of_measurement="m/s",
                                                 value_template="{{ value_json.wind_speed }}",
                                                 state_topic=self._topic)))
            self._client.publish("homeassistant/sensor/windgust/config",
                                 json.dumps(dict(name="Wind speed gust",
                                                 unique_id="whether-windgust",
                                                 device_class="wind_speed",
                                                 unit_of_measurement="m/s",
                                                 value_template="{{ value_json.wind_speed_gust }}",
                                                 state_topic=self._topic)))

        if self.WINDDIRECTION in self._sensors:
            self._payload.append((self._sensors[self.WINDDIRECTION], self.windDirection))

            # no device_class entries to capture generic information
            self._client.publish("homeassistant/sensor/winddir/config",
                                 json.dumps(dict(name="Wind direction (cardinal)",
                                                 unique_id="whether-winddir",
                                                 value_template="{{ value_json.wind_dir }}",
                                                 state_topic=self._topic)))
            self._client.publish("homeassistant/sensor/winddeg/config",
                                 json.dumps(dict(name="Wind direction (degrees)",
                                                 unique_id="whether-winddeg",
                                                 unit_of_measurement="°",
                                                 value_template="{{ value_json.wind_dir_deg }}",
                                                 state_topic=self._topic)))

        if self.RAININTENSITY in self._sensors:
            self._payload.append((self._sensors[self.RAININTENSITY], self.rainfall))
            self._client.publish("homeassistant/sensor/rainfall/config",
                                 json.dumps(dict(name="Rainfall",
                                                 unique_id="whether-rainfall",
                                                 device_class="precipitation_intensity",
                                                 unit_of_measurement="mm/h",
                                                 value_template="{{ value_json.rainfall }}",
                                                 state_topic=self._topic)))
        if self.BATTERY in self._sensors:
            self._payload.append((self._sensors[self.BATTERY], self.battery))
            self._client.publish("homeassistant/sensor/battery/config",
                                 json.dumps(dict(name="Battery",
                                                 unique_id="whether-battery",
                                                 device_class="battery",
                                                 unit_of_measurement="%",
                                                 value_template="{{ value_json.battery_charge }}",
                                                 state_topic=self._topic)))
            self._client.publish("homeassistant/sensor/batterytemp/config",
                                 json.dumps(dict(name="Battery temperature",
                                                 unique_id="whether-batterytemp",
                                                 device_class="temperature",
                                                 unit_of_measurement="C",
                                                 value_template="{{ value_json.battery_temp }}",
                                                 state_topic=self._topic)))

        if self.CPU in self._sensors:
            self._payload.append((self._sensors[self.CPU], self.cpu))
            self._client.publish("homeassistant/sensor/cputemp/config",
                                 json.dumps(dict(name="CPU temperature",
                                                 unique_id="whether-cputemp",
                                                 device_class="temperature",
                                                 unit_of_measurement="C",
                                                 value_template="{{ value_json.cpu_temp }}",
                                                 state_topic=self._topic)))

    def _mqttClient(self):
        '''Connect to the MQTT server.'''
        self._client = mqtt.Client()
        self._client.username_pw_set(username=self._username,
                                     password=self._password)
        logger.debug(f"MQTT {self._server}, username {self._username}, password {self._password}")
        self._client.connect(self._server, port=1883)

    def period(self):
        return self._period

    def temperature(self, t, payload):
        d = meanTagValue(t.events(), t.TEMPERATURE)
        payload['temperature'] = d

    def humidity(self, h, payload):
        d = meanTagValue(h.events(), h.HUMIDITY)
        payload['humidity'] = d

    def windspeed(self, ws, payload):
        d = meanTagValue(ws.events(), ws.WINDSPEED)
        g = maxTagValue(ws.events(), ws.WINDSPEED)
        payload['wind_speed'] = d
        payload['wind_speed_gust'] = g

    def windDirection(self, wd, payload):
        d = modalTagValue(wd.events(), wd.DIRECTION)
        payload['wind_dir'] = d
        payload['wind_dir_deg'] = angleForDirection(d)

    def rainfall(self, rg, payload):
        d = meanTagValue(rg.events(), rg.RAININTENSITY)
        payload['rainfall'] = d

    def battery(self, rg, payload):
        c = meanTagValue(rg.events(), rg.BATTERY_CHARGE_PERCENTAGE)
        t = meanTagValue(rg.events(), rg.BATTERY_TEMPERATURE)
        payload['battery_charge'] = c
        payload['battery_temp'] = t

    def cpu(self, rg, payload):
        t = meanTagValue(rg.events(), rg.CPU_TEMPERATURE)
        payload['cpu_temp'] = t

    def payload(self):
        '''Create the payload for the upload.

        :returns: a dict'''
        payload = dict()
        for (s, f) in self._payload:
            f(s, payload)
        return payload

    def reset(self):
        '''Discard events on component event queues.'''
        for (s, _) in self._payload:
            s.events().reset()

    def submit(self, payload):
        '''Submit the readings to the MQTT server.

        :param payload: the payload
        '''
        logger.debug(f"MQTT submitting {payload}")
        self._client.publish(self._topic, json.dumps(payload))

    async def run(self):
        while True:
            # wait for the next sample submission
            await asyncio.sleep(self.period())

            # send the data
            payload = self.payload()
            self.submit(payload)

            # reset the event queues
            self.reset()
