#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# simulation.py
# Copyright 2012 Julian Fietkau <http://www.julian-fietkau.de/>, 
# Joachim Nitschke
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

from time import time

from math import sqrt

from osmdata import GraphBuilder
from streetnetwork import StreetNetwork
from persistence import persist_write

# This class does the actual simulation steps
class Simulation(object):

    def __init__(self, street_network, trips, log_callback, persist = False):
        self.street_network = street_network
        self.trips = trips
        self.log_callback = log_callback
        self.step_counter = 0
        self.persist = persist

        # initialize street usage with 0
        self.street_usage = dict()
        for street, length, max_speed in street_network:
            self.street_usage[street] = 0

        if self.persist:
            self.log_callback("Saving street network to disk...")
            persist_write("street_network_" + str(self.step_counter) + ".s4mpi", self.street_network)

    def step(self):
        self.step_counter += 1
        self.log_callback("Preparing edges...")

        for street, length, max_speed in self.street_network:
            # update driving time
            driving_time = self.calculate_actual_driving_time(length, max_speed, self.street_usage[street])
            self.street_network.set_driving_time(street, driving_time)

            # reset street usage
            self.street_usage[street] = 0

        origin_nr = 0
        for origin in self.trips.keys():
            # calculate all shortest paths from resident to every other node
            origin_nr += 1
            self.log_callback("Origin nr", origin_nr, "...")
            paths = self.street_network.calculate_shortest_paths(origin)
            for goal in self.trips[origin]:
                # is the goal even reachable at all? if not, ignore for now
                if goal in paths:
                    # hop along the edges until we're there
                    current = goal
                    while current != origin:
                        self.street_usage[(current, paths[current])] += 1
                        current = paths[current]

        if self.persist:
            self.log_callback("Saving street usage to disk...")
            persist_write("street_usage_" + str(self.step_counter) + ".s4mpi", self.street_usage)

    def calculate_actual_driving_time(self, street_length, max_speed, number_of_trips):
        # TODO store these constants in settings.py?
        CAR_LENGTH = 4
        MIN_BREAKING_DISTANCE = 0.01
        BRAKING_DECELERATION = 7.5         

        # TODO distribute trips over the day since they are not all driving at the same time
        # distribute trips over the street
        available_space_for_each_car = street_length / max(number_of_trips, 1)
        available_braking_distance = max(available_space_for_each_car - CAR_LENGTH, MIN_BREAKING_DISTANCE)
        # how fast can a car drive to ensure the calculated breaking distance?
        potential_speed = sqrt(BRAKING_DECELERATION * available_braking_distance * 2)
        # cars respect speed limit
        actual_speed = min(max_speed, potential_speed)
        actual_driving_time = street_length / actual_speed

        return actual_driving_time

if __name__ == "__main__":
    def out(*output):
        for o in output:
            print o,
        print ''

    street_network = StreetNetwork()
    street_network.add_node(1, 0, 0)
    street_network.add_node(2, 0, 0)
    street_network.add_node(3, 0, 0)
    street_network.add_street((1, 2,), 10, 50)
    street_network.add_street((2, 3,), 100, 140)

    trips = dict()
    trips[1] = [3]

    sim = Simulation(street_network, trips, out)
    for step in range(10):
        print "Running simulation step", step + 1, "of 10..."
        sim.step()
    # done

