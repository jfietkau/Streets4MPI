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

def merge_dictionaries(dictionaries):
    merged_dictionary = dict()

    for dictionary in dictionaries:
        for key, value in dictionary.iteritems():
            total_value = value
            if key in merged_dictionary.keys():
                total_value += merged_dictionary[key]
            merged_dictionary[key] = total_value

    return merged_dictionary

