#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# simulation.py
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

from pygraph.classes.graph import graph
from pygraph.algorithms.minmax import shortest_path

from time import time

from osmdata import GraphBuilder
from streetnetwork import StreetNetwork

# This class does the actual simulation steps
class Simulation(object):

    def __init__(self, street_network, trips, log_callback):
        # TODO do not access the graph directly
        self.graph = street_network._graph
        self.trips = trips
        self.edge_usage = dict()
        self.log_callback = log_callback

    def step(self):
        self.log_callback("Preparing edges...")
        for edge in self.graph.edges():
            self.edge_usage[edge] = 0
            attrs = self.graph.edge_attributes(edge)
            length = None
            maxspeed = None
            for attr in attrs:
                if attr[0] == StreetNetwork.ATTRIBUTE_KEY_LENGTH:
                    length = attr[1]
                if attr[0] == StreetNetwork.ATTRIBUTE_KEY_MAX_SPEED:
                    maxspeed = attr[1]
            if length != None and maxspeed != None:
                expected_time = length / maxspeed
                self.graph.set_edge_weight(edge, expected_time)
        origin_nr = 0
        for origin in self.trips.keys():
            # calculate all shortest paths from resident to every other node
            origin_nr += 1
            self.log_callback("Origin nr", origin_nr, "...")
            paths = shortest_path(self.graph, origin)[0]
            for goal in self.trips[origin]:
                # is the goal even reachable at all? if not, ignore for now
                if goal in paths:
                    # hop along the edges until we're there
                    current = goal
                    while current != origin:
                        self.edge_usage[(current, paths[current])] += 1
                        current = paths[current]

if __name__ == "__main__":

    def out(*output):
        for o in output:
            print o,
        print ''

    graph = graph()
    graph.add_nodes([1,2,3])
    graph.add_edge((1,2,))
    graph.add_edge((2,3,))
    graph.add_edge_attributes((1,2,), [(0, 10,), (1, 50,)])
    graph.add_edge_attributes((2,3,), [(0, 100,), (1, 140,)])

    trips = dict()
    trips[1] = [3]

    sim = Simulation(graph, trips, out)
    for step in range(10):
        print "Running simulation step", step+1, "of 10..."
        sim.step()
    # done

