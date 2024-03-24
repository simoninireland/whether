# Process tree parsing
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

import io
from pathlib import Path
import yaml
from whether import onlyDictElement, onlyDictElements


class ProcessTree:
    '''The process tree for a sensor deployment.

    This is an abstract class defining the tree parser obtained from
    a YAML file. It calls specific methods to handle the elements once
    parsed: sub-classes can construct the process tree or generate
    code that compiles it.

    :param fn: file name or file structure for the process tree description
    '''

    def __init__(self, fn):
        super().__init__()
        self._metadata = {}
        self._elements = {}
        self._load(fn)


    #---------- File handling ----------

    def _load(self, fn):
        '''Load the process tree described in the file.

        :param fn: the filename'''
        t = None
        if isinstance(fn, str) or isinstance(fn, Path):
            # file name or path
            with open(fn, "r") as fh:
                t = yaml.safe_load(fh)
        elif isinstance(fn, io.TextIOBase):
            # file object
             t = yaml.safe_load(fn)
        else:
            raise Exception(f'Can\'t handle file object {fn}')

        self._parse(t)

    def _parse(self, t):
        '''Parse a process tree,

        :param t: the tree'''

        # parse the various top-level elements
        es = onlyDictElement(t, 'location')
        for k in es.keys():
            if k == 'sensors':
                for s in onlyDictElements(es[k], 'sensor'):
                    self.createSensor(s)
            elif k == 'aggregators':
                for a in onlyDictElements(es[k], 'aggregator'):
                    self.createAggregator(a)
            elif k == 'reporters':
                for r in onlyDictElements(es[k], 'reporter'):
                    self.createReporter(r)
            else:
                # anything else is assumed to be metadata
                self._metadata[k] = es[k]


    # ---------- Access ----------

    # IDs have to be unique, so we hold all sensors, aggregators, and
    # reporters in one dict.

    def add(self, e):
        '''Add a sensor, aggregator, or reporter to the process tree.
        The element is keyed by its ID, which must be unique.

        :param e: the element'''
        id = e.id()
        if id in self._elements.keys():
            raise Exception(f'Duplicate id {id}')
        self._elements[id] = e

    def get(self, id, default=None):
        '''Retrieve the sensor, aggregator, or reporter with the given ID.
        The default value is returned if there is no such element defined.

        :param id: the id
        :param default: the default value'''
        return self._elements.get(id, default)


    # ---------- Tree construction ----------

    def createSensor(self, s):
        '''Creates a sensor. This method should be overridden by sub-classes.

        :param s: a dict describing the sensor'''
        raise NotImplementedError('createSensor')

    def createAggregator(self, s):
        '''Creates an aggregator. This method should be overridden by sub-classes.

        :param a: a dict describing the aggregator'''
        raise NotImplementedError('createAggregator')

    def createReporter(self, r):
        '''Creates a reporter. This method should be overridden by sub-classes.

        :param r: a dict describing the reporter'''
        raise NotImplementedError('createReporter')
