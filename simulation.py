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
from operator import itemgetter

from osmdata import GraphBuilder
from streetnetwork import StreetNetwork
from utils import merge_dictionaries
from settings import settings

# This class does the actual simulation steps
class Simulation(object):

    def __init__(self, street_network, trips, jam_tolerance, log_callback):
        self.street_network = street_network
        self.trips = trips
        self.jam_tolerance = jam_tolerance
        self.log_callback = log_callback
        self.step_counter = 0
        self.traffic_load = dict()
        self.cumulative_traffic_load = dict()

    def step(self):
        self.step_counter += 1
        self.log_callback("Preparing edges...")

        # update driving time based on traffic load
        for street, length, max_speed in self.street_network:
            if street in self.traffic_load.keys():
                street_traffic_load = self.traffic_load[street]
            else:
                street_traffic_load = 0

            # ideal speed is when the street is empty
            ideal_speed = calculate_driving_speed(length, max_speed, 0)
            # actual speed may be less then that
            actual_speed = calculate_driving_speed(length, max_speed, street_traffic_load)
            # based on traffic jam tolerance the deceleration is weighted differently
            perceived_speed = actual_speed + (ideal_speed - actual_speed) * self.jam_tolerance

            driving_time = length / perceived_speed

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

    def road_construction(self):
        sorted_traffic_load = sorted(self.cumulative_traffic_load.iteritems(), key = itemgetter(1))
        max_decrease_index =  0.15 * len(sorted_traffic_load) # bottom 15%
        min_increase_index = 0.95 * len(sorted_traffic_load) # top 5%
        for i in range(len(sorted_traffic_load)):
            if i <= max_decrease_index:
                if not self.street_network.change_maxspeed(sorted_traffic_load[i][0], -20):
                    max_decrease_index += 1
            j = len(sorted_traffic_load) - i - 1
            if j >= min_increase_index:
                if not self.street_network.change_maxspeed(sorted_traffic_load[j][0], 20):
                    min_increase_index -= 1
            if max_decrease_index >= min_increase_index:
                break
        self.cumulative_traffic_load = dict()

def calculate_driving_speed_var(street_length, max_speed, number_of_trips):
    # individual formulae:
    # number of trips per time = (number of trips * street length) / (actual speed * traffic period duration)
    # available space for each car = street length / max(number of trips per time, 1)
    # available braking distance = max(available space for each car - car length, min breaking distance)
    # how fast can a car drive to ensure the calculated breaking distance?
    # potential speed = sqrt(braking deceleration * available braking distance * 2)
    # actual speed = min(max speed, potential speed)

    # all in one calculation:
    intermediate_quotient_result = settings["traffic_period_duration"] * 3600 * settings["braking_deceleration"] / max(number_of_trips, 1)
    potential_speed = sqrt(intermediate_quotient_result**2 + 2 * settings["car_length"] * settings["braking_deceleration"]) + intermediate_quotient_result # m/s
    actual_speed = min(max_speed, potential_speed * 3.6) # km/h

    return actual_speed

def calculate_driving_speed(street_length, max_speed, number_of_trips):
    # distribute trips over the street
    available_space_for_each_car = street_length / max(number_of_trips, 1) # m
    available_braking_distance = max(available_space_for_each_car - settings["car_length"], settings["min_breaking_distance"]) # m
    # how fast can a car drive to ensure the calculated breaking distance?
    potential_speed = sqrt(settings["braking_deceleration"] * available_braking_distance * 2) # m/s
    # cars respect speed limit
    actual_speed = min(max_speed, potential_speed * 3.6) # km/h

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

