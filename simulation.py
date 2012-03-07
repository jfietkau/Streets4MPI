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

# This class does the actual simulation steps
class Simulation(object):

    def __init__(self, graph, trips):
        self.graph = graph
        self.trips = trips
        self.edge_usage = dict()

    def step(self):
        for edge in self.graph.edges():
            self.edge_usage[edge] = 0
        for resident in self.trips.keys():
            # calculate all shortest paths from resident to every other node
            paths = shortest_path(self.graph, resident)[0]
            for goal in self.trips[resident]:
                # is the goal even reachable at all? if not, ignore for now
                if goal in paths:
                    # hop along the edges until we're there
                    current = goal
                    while current != resident:
                        self.edge_usage[(current, paths[current])] += 1
                        current = paths[current]

if __name__ == "__main__":

    graph = graph()
    graph.add_nodes([1,2,3])
    graph.add_edge((1,2,))
    graph.add_edge((2,3,))

    trips = dict()
    trips[1] = [3]

    sim = Simulation(graph, trips)
    for step in range(10):
        print "Running simulation step", step+1, "of 10..."
        sim.step()
    # done

