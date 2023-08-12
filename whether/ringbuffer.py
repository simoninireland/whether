# Ring buffers
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

from whether import logger


class RingBuffer:
    '''Ring buffers.

    A ring buffer is a queue with a maximum size. The ring behaves
    like a first-in/first-out queue. However, if its size grows to
    be larger than the given size, new elements overwrite older
    elements, oldest first.
    '''

    def __init__(self, n):
        '''Create an empty ring buffer of size n.

        :param n: the length of the ring buffer'''
        self._len = n + 1             # size + the marker
        self._write = 0
        self._read = 0

        # initialise the buffer with a reference, the assumption being
        # that this sets up initial menory that won't then be expanded
        self._buf = [ self ] * self._len

    def size(self):
        '''Return the maximum number of elements in the ring.

        :returns: the size'''
        return self._len - 1

    def __len__(self):
        '''Return the length of the ring, which is the number
         of elements it actually contains.

        :returns: the length'''
        return (self._write - self._read) % self._len

    def reset(self):
        '''Reset the buffer.'''
        self._write = 0
        self._read = 0

    def empty(self):
        '''Test if the buffer is empty. Popping from an
        empty buffer will return None.

        :returns: True if the buffer is empty'''
        return (self._read == self._write)

    def full(self):
        '''Test is the buffer is full. Pushing to a full buffer will
        overwrite the oldest element.

        :returns: True if the buffer is full'''
        return (((self._write + 1) % self._len) == self._read)

    def push(self, v):
        '''Push a value to the buffer.

        This operationm will result in data loss if the ring is full: the
        oldest element will be dropped. This is logged as an info-level
        event: *not* as an error, since this behaviour is part of the
        purpose of using ring buffers in the first place.

        :param v: the value to push'''
        self._buf[self._write] = v
        self._write = (self._write + 1) % self._len
        if self._read == self._write:
            # the buffer is full, so drop the oldest element
            # so that the next read will read the next oldest
            logger.info("Dropped item {v} from ring buffer".format(v=self._buf[self._write]))
            self._read = (self._read + 1) % self._len

    def pop(self):
        '''Pop a value from the buffer. The value returned will be
        the oldest value pushed. Return None if the buffer is empty.

        :returns: the next value'''
        if self.empty():
            return None
        v = self._buf[self._read]
        self._read = (self._read + 1) % self._len
        return v

    def peek(self, i = 0):
        '''Return the i'th element from the front of the buffer without popping it.
        Return None if the buffer is empty.

        :returns: the next value'''
        n = (self._read + i) % self._len
        if n == self._write:
            # buffer is empty
            return None
        else:
            v = self._buf[n]
            return v


    # ---------- Iterator interface ----------

    class Iterator:
        '''A non-destructive iterator over a ring buffer. Iterating
        will :meth:`peek` at elements until all have been seen.

        This is absolutely not safe against pops or pushes mid-iteration.

        :param ring: the ring buffer
        '''

        def __init__(self, ring):
            self._ring = ring
            self._i = 0

        def __next__(self):
            '''Return the next value.

            :returns: the next value'''
            while True:
                v = self._ring.peek(self._i)
                if v is None:
                    raise StopIteration
                else:
                    self._i += 1
                    return v

    def __iter__(self):
        '''Return a non-destructive iterator over this ring.

        :returns: an iterator'''
        return RingBuffer.Iterator(self)
