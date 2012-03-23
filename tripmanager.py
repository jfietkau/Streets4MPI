#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# tripmanager.py
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

from random import sample
from time import time

# This class creates the appropriate number of residents and manages the trips
class TripManager(object):

    def __init__(self, number_of_residents, sources, targets):
        self.number = number_of_residents
        self.sources = sources
        self.targets = targets
        self.trips = dict()

    def create_trips(self):
        self.trips = dict()
        for i in range(0, self.number):
            source = sample(self.sources, 1)[0]
            target = sample(self.targets, 1)[0]
            if source in self.trips.keys():
                goals = self.trips[source]
            else:
                goals = list()
            goals.append(target)
            self.trips[source] = goals

if __name__ == "__main__":
    manager = TripManager(30, set([1, 2, 3, 4, 5]), set([6, 7, 8, 9, 10]))

    start = time()

    manager.create_trips()

    generated = time()

    # done
    print "Trips: ", manager.trips
    print "Time generating trips: ", generated - start, " seconds"

