# Tests of ring buffers
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
from whether import *


class RingBufferTest(unittest.TestCase):

    def testInitiallyEmpty(self):
        '''Test that a new buffer is empty.'''
        ring = RingBuffer(10)
        self.assertTrue(ring.empty())
        self.assertEqual(ring.size(), 10)
        self.assertEqual(len(ring), 0)

    def testPopEmpty(self):
        '''Test we can't pop from an empty ring.'''
        ring = RingBuffer(10)
        self.assertIsNone(ring.pop())

    def testPushPop(self):
        '''Test we pop what we push.'''
        ring = RingBuffer(10)
        ring.push(10)
        self.assertEqual(len(ring), 1)
        self.assertEqual(ring.pop(), 10)
        self.assertEqual(len(ring), 0)

    def testPeekEmpty(self):
        '''Test we can't peek into an empty buffer.'''
        ring = RingBuffer(10)
        self.assertIsNone(ring.peek())

    def testPushPeek(self):
        '''Test we can peek what we push.'''
        ring = RingBuffer(10)
        ring.push(10)
        self.assertEqual(len(ring), 1)
        self.assertEqual(ring.peek(), 10)
        self.assertEqual(len(ring), 1)

    def testPushNotEmpty(self):
        '''Test a ring with an element isn't empty.'''
        ring = RingBuffer(10)
        ring.push(10)
        self.assertFalse(ring.empty())

    def testPushSeqLen(self):
        '''Test pushing and popping changes the length correctly.'''
        ring = RingBuffer(3)
        self.assertEqual(len(ring), 0)
        ring.push(1)
        self.assertEqual(len(ring), 1)
        ring.push(2)
        self.assertEqual(len(ring), 2)
        ring.pop()
        self.assertEqual(len(ring), 1)
        ring.pop()
        self.assertEqual(len(ring), 0)
        self.assertTrue(ring.empty())

    def testPushSeq(self):
        '''Test we can push and pop a sequence of values.'''
        ring = RingBuffer(10)
        seq = [1, 2, 3]
        for s in seq:
            ring.push(s)
        self.assertEqual(len(ring), len(seq))
        for s in seq:
            self.assertEqual(s, ring.pop())
        self.assertTrue(ring.empty())

    def testNotFull(self):
        '''Test we can detect a full ring (undercount).'''
        ring = RingBuffer(3)
        seq = [1, 2]
        for s in seq:
            ring.push(s)
        self.assertFalse(ring.full())

    def testFull(self):
        '''Test we can detect a full ring.'''
        ring = RingBuffer(3)
        seq = [1, 2, 3]
        for s in seq:
            ring.push(s)
        self.assertTrue(ring.full())
        self.assertEqual(len(ring), 3)

    def testPushOverwrite(self):
        '''Test we overwrite old values when the ring fills.'''
        ring = RingBuffer(3)
        seq = [1, 2, 3, 4]
        for s in seq:
            ring.push(s)
        for s in seq[1:]:
            self.assertEqual(s, ring.pop())
        self.assertTrue(ring.empty())

    def testPushOverwriteSeq(self):
        '''Test opverwriting maintains the last values pushed.'''
        ring = RingBuffer(3)
        seq = [1, 2, 3, 4, 5, 6, 7, 8]
        for s in seq:
            ring.push(s)
        for s in seq[-3:]:
            self.assertEqual(ring.pop(), s)

    def testMaxLen(self):
        '''Test the length maxes out correctly.'''
        ring = RingBuffer(3)
        seq = [1, 2, 3, 4, 5, 6, 7, 8]
        for s in seq:
            ring.push(s)
            self.assertTrue(len(ring) <= 3)


    # ---------- Iterator interface ----------

    def testIterEmpty(self):
        '''Test iterating an empty ring.'''
        ring = RingBuffer(10)
        self.assertCountEqual([x for x in ring], [])

    def testIterNotEmpty(self):
        '''Test iterating a ring.'''
        ring = RingBuffer(10)
        seq = [1, 2, 3, 4, 5, 6]
        for s in seq:
            ring.push(s)
        self.assertCountEqual([x for x in ring], seq)
