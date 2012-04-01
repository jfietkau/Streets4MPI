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
    ATTRIBUTE_KEY_LENGTH = 0
    ATTRIBUTE_KEY_MAX_SPEED = 1
    ATTRIBUTE_KEY_LATITUDE = 0
    ATTRIBUTE_KEY_LONGITUDE = 1

    def __init__(self):
        # graph that holds the street network
        self._graph = graph()
        self.bounds = None

    def has_street(self, street):
        return self._graph.has_edge(street)

    def add_street(self, street, length, max_speed):
        if not self.has_node(street[0]): raise AssertionError("Precondition failed: has_node(street[0])")
        if not self.has_node(street[1]): raise AssertionError("Precondition failed: has_node(street[1])")
        if self.has_street(street): raise AssertionError("Precondition failed: not has_street(street)")

        attributes = [(self.ATTRIBUTE_KEY_LENGTH, length), (self.ATTRIBUTE_KEY_MAX_SPEED, max_speed)]
        # set initial weight to optimal driving time
        weight = length / max_speed

        self._graph.add_edge(street, wt=weight, attrs=attributes)

    def set_driving_time(self, street, driving_time):
        if not self.has_street(street): raise AssertionError("Precondition failed: has_street(street)")

        self._graph.set_edge_weight(street, driving_time)

    def get_driving_time(self, street):
        if not self.has_street(street): raise AssertionError("Precondition failed: has_street(street)")

        return self._graph.edge_weight(street)

    def change_maxspeed(self, street, maxspeed_delta):
        if not self.has_street(street): raise AssertionError("Precondition failed: has_street(street)")

        # pygraph can not delete or update a single attribute :(
        # thus, we save them all and the weight and rebuild them
        weight = self._graph.edge_weight(street)
        attrs = self._graph.edge_attributes(street)
        self._graph.del_edge_labeling(street)
        self._graph.set_edge_weight(street, weight)
        new_attrs = []
        for attr in attrs:
            if attr[0] == self.ATTRIBUTE_KEY_MAX_SPEED:
                value = attr[1] + maxspeed_delta
                value = max(1, min(140, value))
            else:
                value = attr[1]
            new_attrs.append((attr[0], value))
        self._graph.add_edge_attributes(street, new_attrs)

    def set_bounds(self, min_lat, max_lat, min_lon, max_lon):
        self.bounds = ((min_lat, max_lat), (min_lon, max_lon))

    def add_node(self, node, lon, lat):
        if self.has_node(node): raise AssertionError("Precondition failed: not has_node(node)")

        self._graph.add_node(node, [(self.ATTRIBUTE_KEY_LONGITUDE, lon), (self.ATTRIBUTE_KEY_LATITUDE, lat)])
        
    def get_nodes(self):
        return self._graph.nodes()

    def get_node_attributes(self, node):
        return self._graph.node_attributes(node)

    def has_node(self, node):
        return self._graph.has_node(node)

    def calculate_shortest_paths(self, origin_node):
        if not self.has_node(origin_node): raise AssertionError("Precondition failed: has_node(origin_node)")

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
            attrs = dict(self._graph.edge_attributes(street))

            yield (street, attrs[StreetNetwork.ATTRIBUTE_KEY_LENGTH], attrs[StreetNetwork.ATTRIBUTE_KEY_MAX_SPEED])
        
