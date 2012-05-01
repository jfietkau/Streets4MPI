#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# persistence.py
# Copyright 2012 Julian Fietkau <http://www.julian-fietkau.de/>
#
# This file is part of Streets4MPI.
#
# Streets4MPI is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Streets4MPI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Streets4MPI.  If not, see <http://www.gnu.org/licenses/>.
#

import cPickle
import zlib

# This function serializes and compresses an object
def persist_serialize(data, compress = True):
    if compress:
        return zlib.compress(cPickle.dumps(data))
    else:
        return cPickle.dumps(data)

# This function deserializes and decompresses an object
def persist_deserialize(data, compressed = True):
    if compressed:
        return cPickle.loads(zlib.decompress(data))
    else:
        return cPickle.loads(data)

# This function saves a data structure to a file
def persist_write(filename, data, compress = True):
    file = open(filename, "w")
    file.write(persist_serialize(data, compress))

# This function reads a data structure from a file
def persist_read(filename, compressed = True):
    file = open(filename, "r")
    return persist_deserialize(file.read(), compressed)

