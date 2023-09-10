# Tests of process tree parsing
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

import unittest
from pathlib import Path
from io import StringIO
from whether import *


# ---------- Testing dummy harness ----------

# A null process tree that does does the parsing
class NullProcessTree(ProcessTree):
    def createSensor(self, s):
        pass

    def createAggregator(self, a):
        pass

    def createReporter(self, r):
        pass


# ---------- Tests----------

# The sample YAML file
# This is intended to be the up-to-date test case for anything we add
# to the process tree file format
source_path = Path(__file__).resolve()
sample_process_tree_file = Path(source_path.parent, 'sample_process_tree.yaml')

class ProcessTreeTest(unittest.TestCase):

    # ---------- Parsing ----------

    def testSimpleCase(self):
        '''Test a simple passing case.'''
        tree = NullProcessTree(StringIO('''
        location:
          sensors:
          - sensor:
        '''))

    def testLocation(self):
        '''Test we fail with no location, or anything else at toplevel..'''

        # no location: at top-level
        with self.assertRaises(ProcessTreeFileParserException):
            tree = NullProcessTree(StringIO('''
            sensors:
            - sensor:
            '''))

        # other top-level
        with self.assertRaises(ProcessTreeFileParserException):
            tree = NullProcessTree(StringIO('''
            location:
              sensors:
              - sensor:
            aggregators:
            - aggregator:
            '''))

    def testMainElements(self):
        '''Test we recognise the main elements.'''
        tree = NullProcessTree(StringIO('''
        location:
          sensors:
          - sensor:
              name: one
          - sensor:
              name: two
          aggregators:
          - aggregator:
              name: one
          - aggregator:
              name: two
          reporters:
          - reporter:
              name: one
          - reporter:
              name: two
        '''))

    def testMetadata(self):
        '''Test we can store metadata.'''
        tree = NullProcessTree(StringIO('''
        location:
          name: Here
          longitude: 55.5
          latitude: 1.3
          altitude: 11
          sensors:
          - sensor:
              name: one
          - sensor:
              name: two
          aggregators:
          - aggregator:
              name: one
          - aggregator:
              name: two
          reporters:
          - reporter:
              name: one
          - reporter:
              name: two
        '''))

        meta = tree._metadata
        self.assertEqual(meta['name'], "Here")
        self.assertEqual(meta['longitude'], 55.5)
        self.assertEqual(meta['longitude'], 55.5)
        self.assertEqual(meta['latitude'], 1.3)
        self.assertEqual(meta['altitude'], 11)

    def testSample(self):
        '''Test we can parse the sample file.'''
        tree = NullProcessTree(sample_process_tree_file)


    # ---------- Loading ----------

    def testSensor(self):
        '''Test we can create a sensor.'''
        tree = ProcessTreeLoader(StringIO('''
        location:
          sensors:
          - sensor:
              id: 123
              class: DHT22
              gpio: D14
        '''))

        self.assertIsNotNone(tree.get(123))
        self.assertTrue(isinstance(tree.get(123), DHT22))

    def testSensors(self):
        '''Test we can create several sensors.'''
        tree = ProcessTreeLoader(StringIO('''
        location:
          sensors:
          - sensor:
              id: 123
              class: DHT22
              gpio: D14
          - sensor:
              id: 456
              class: Anemometer
              gpio: D14
        '''))

        self.assertIsNotNone(tree.get(123))
        self.assertTrue(isinstance(tree.get(123), DHT22))
        self.assertIsNotNone(tree.get(456))
        self.assertTrue(isinstance(tree.get(456), Anemometer))
