#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# tripgenerator.py
# Copyright 2012 Julian Fietkau <http://www.julian-fietkau.de/>,
#                Joachim Nitschke
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
class TripGenerator(object):

    def generate_trips(self, number_of_residents, potential_origins, potential_goals):
        trips = dict()
        
        for i in range(0, number_of_residents):
            origin = sample(potential_origins, 1)[0]
            goal = sample(potential_goals, 1)[0]

            if origin in trips.keys():
                goals = trips[origin]
            else:
                goals = list()
            goals.append(goal)
            trips[origin] = goals

        return trips

if __name__ == "__main__":
    manager = TripManager(30, set([1, 2, 3, 4, 5]), set([6, 7, 8, 9, 10]))

    start = time()

    manager.create_trips()

    generated = time()

    # done
    print "Trips: ", manager.trips
    print "Time generating trips: ", generated - start, " seconds"

