#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# utils.py
# Copyright 2012 Joachim Nitschke
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

from array import array
from itertools import repeat
from math import floor


def merge_arrays(arrays):
    merged_array = array("I", repeat(0, len(arrays[0])))

    for arr in arrays:
        if arr != None:
            for index in range(0, len(arr)):
                merged_array[index] += arr[index]

    return merged_array


def print_header(text):
    print '#' * 40
    print '#'
    # This would be so much easier with fstrings, god bless 3.6
    print '#' + " " * (20 - floor(len(text) / 2)) + text + '*' * (40 - len(text) - 1) + "#"
    print '#'
    print '#' * 40
