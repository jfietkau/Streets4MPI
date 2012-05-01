#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# streetnetwork.py
# Copyright 2012 Joachim Nitschke, 
#                Julian Fietkau <http://www.julian-fietkau.de/>
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

# This class represents a street network
class StreetNetwork(object):
    ATTRIBUTE_INDEX_LENGTH = 0
    ATTRIBUTE_INDEX_MAX_SPEED = 1
    ATTRIBUTE_INDEX_LONGITUDE = 0
    ATTRIBUTE_INDEX_LATITUDE = 1

    def __init__(self):
        # graph that holds the street network
        self._graph = graph()
        self.bounds = None

    def has_street(self, street):
        return self._graph.has_edge(street)

    def add_street(self, street, length, max_speed):
        # attribute order is given through constants ATTRIBUTE_INDEX_...
        street_attributes = [length, max_speed]
        # set initial weight to ideal driving time
        driving_time = length / max_speed

        self._graph.add_edge(street, wt=driving_time, attrs=street_attributes)

    def set_driving_time(self, street, driving_time):
        self._graph.set_edge_weight(street, driving_time)

    def get_driving_time(self, street):
        return self._graph.edge_weight(street)

    def change_maxspeed(self, street, max_speed_delta):
        street_attributes = self._graph.edge_attributes(street)
        street_attributes[ATTRIBUTE_INDEX_MAX_SPEED] = street_attributes[ATTRIBUTE_INDEX_MAX_SPEED] + max_speed_delta

    def set_bounds(self, min_latitude, max_latitude, min_longitude, max_longitude):
        self.bounds = ((min_latitude, max_latitude), (min_longitude, max_longitude))

    def add_node(self, node, longitude, latitude):
        # attribute order is given through constants ATTRIBUTE_INDEX_... 
        self._graph.add_node(node, [longitude, latitude])
        
    def get_nodes(self):
        return self._graph.nodes()

    def node_coordinates(self, node):
        node_attributes = self._graph.node_attributes(node)

        return (node_attributes[ATTRIBUTE_INDEX_LONGITUDE], node_attributes[ATTRIBUTE_INDEX_LATITUDE])

    def has_node(self, node):
        return self._graph.has_node(node)

    def calculate_shortest_paths(self, origin_node):
        return shortest_path(self._graph, origin_node)[0]

    # iterator to iterate over the streets and their attributes
    def __iter__(self):
        for street in self._graph.edges():
            if street[0] > street[1]:
                # using the "graph" class from pygraph, we will get every edge
                # twice in this loop: one time for each direction. We discard
                # one of the directions to not return the same edge twice when
                # iterating over the street network.
                continue

            # get street attributes
            street_attributes = self._graph.edge_attributes(street)

            yield (street, street_attributes[StreetNetwork.ATTRIBUTE_INDEX_LENGTH], street_attributes[StreetNetwork.ATTRIBUTE_INDEX_MAX_SPEED])
