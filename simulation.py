#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# simulation.py
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

from time import time
from math import sqrt

from osmdata import GraphBuilder
from streetnetwork import StreetNetwork

# This class does the actual simulation steps
class Simulation(object):

    def __init__(self, street_network, trips, log_callback):
        self.street_network = street_network
        self.trips = trips
        self.log_callback = log_callback
        self.step_counter = 0
        self.traffic_load = dict()

    def step(self):
        self.step_counter += 1
        self.log_callback("Preparing edges...")

        # update driving time based on traffic load
        for street, length, max_speed in self.street_network:
            if street in self.traffic_load.keys():
                street_traffic_load = self.traffic_load[street]
            else:
                street_traffic_load = 0
            actual_speed = calculate_actual_speed(length, max_speed, street_traffic_load)
            driving_time = length / actual_speed
            self.street_network.set_driving_time(street, driving_time)

        # reset traffic load
        self.traffic_load.clear()

        origin_nr = 0
        for origin in self.trips.keys():
            # calculate all shortest paths from resident to every other node
            origin_nr += 1
            self.log_callback("Origin nr", str(origin_nr) + "...")
            paths = self.street_network.calculate_shortest_paths(origin)

            # increase traffic load
            for goal in self.trips[origin]:
                # is the goal even reachable at all? if not, ignore for now
                if goal in paths:
                    # hop along the edges until we're there
                    current = goal
                    while current != origin:
                        street = (min(current, paths[current]), max(current, paths[current]))
                        current = paths[current]
                        usage = 1
                        if street in self.traffic_load.keys():
                            usage += self.traffic_load[street]
                        self.traffic_load[street] = usage

def calculate_actual_speed(street_length, max_speed, number_of_trips):
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

    return actual_speed

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

