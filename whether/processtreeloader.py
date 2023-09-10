# Process tree loader
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
import sys
from pathlib import Path
import yaml
from whether import ProcessTree


class ProcessTreeLoader(ProcessTree):
    '''Loaderf for process trees.

    This class parses a process tree description and then loads it,
    creating all the elements and their buffers.

    :param fn: file name or file structure for the process tree description
    '''

    DEFAULT_PACKAGE = __name__   #: Package against which to expland unqualified class names.


    def __init__(self, fn):
        super().__init__(fn)
        self._sensors = {}
        self._aggregators = {}
        self._reporters = {}


    # ---------- Run-time instanciation ----------

    def _fullClassName(self, cl):
        '''Return the module and class name for a class. If the class
        isn't fully-qualified, qualify it with our default package.

        :param cl: the class name
        :returns: a pair of module and class name'''
        lastdot = cl.rfind('.')
        if lastdot == -1:
            return (self.DEFAULT_PACKAGE, cl)
        else:
            return (cl[:lastdot], cl[lastdot + 1:])

    def instanciate(self, settings):
        '''Instanciate a class and pass it its settings.

        The settings should include:

        - 'class': the name of the class to be instanciated

        The class name can be a fully-qualified class with a package
        (for exmaple 'mysensors.DHT22') or an unqualified class name
        (for example 'DHT22'). In the latter case the class name is
        assumed to be built-in to whether and is qualified against
        the appropriate default package name.

        :param settings: the settings'''
        fqcn = settings.get('class')
        (pn, cn) = self._fullClassName(fqcn)

        module = __import__(pn)
        cl = getattr(module, cn)
        o = cl(settings)
        return o


    # ---------- Tree construction ----------

    def createSensor(self, s):
        '''Add a sensor.

        :param s: a dict describing the sensor'''
        sensor = self.instanciate(s)
        self.add(sensor)

    def createAggregator(self, s):
        '''Add an aggregator.

        :param a: a dict describing the aggregator'''
        raise NotImplementedError('addAggregator')

    def createReporter(self, r):
        '''Add a reporter.

        :param r: a dict describing the reporter'''
        raise NotImplementedError('addReporter')
