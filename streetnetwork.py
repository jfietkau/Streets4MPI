#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# tripmanager.py
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

    def exists_street(self, street):
        return self._graph.has_edge(street)

    def add_street(self, street, length, max_speed):
        if self.exists_street(street): raise AssertionError("Precondition failed: not exists_street(street)")

        # add street nodes if they are not in the graph
        node1 = street[0]
        node2 = street[1]
        if not self._graph.has_node(node1):
            self._graph.add_node(node1)
        if not self._graph.has_node(node2):
            self._graph.add_node(node2)
        
        attributes = [(self.ATTRIBUTE_KEY_LENGTH, length,), (self.ATTRIBUTE_KEY_MAX_SPEED, max_speed,)]
        # set initial weight to optimal driving time
        weight = length / max_speed

        self._graph.add_edge(street, wt=weight, attrs=attributes)

    def set_driving_time(self, street, driving_time):
        if not self.exists_street(street): raise AssertionError("Precondition failed: exists_street(street)")

        self._graph.set_edge_weight(street, driving_time)

    def add_node(self, osmid, lon, lat):
        if not self._graph.has_node(osmid):
            self._graph.add_node(osmid, [(self.ATTRIBUTE_KEY_LONGITUDE, lon), (self.ATTRIBUTE_KEY_LATITUDE, lat)])
        

    def get_nodes(self):
        return self._graph.nodes()

    def exists_node(self, node):
        return self._graph.has_node(node)

    def calculate_shortest_paths(self, origin_node):
        if not self.exists_node(origin_node): raise AssertionError("Precondition failed: exists_node(origin_node)")

        return shortest_path(self._graph, origin_node)[0]

    # iterator to iterate over the streets and their attributes
    def __iter__(self):
        for street in self._graph.edges():
            # get street attributes
            attrs = self._graph.edge_attributes(street)
            length = None
            max_speed = None
            for attr in attrs:
                if attr[0] == StreetNetwork.ATTRIBUTE_KEY_LENGTH:
                    length = attr[1]
                elif attr[0] == StreetNetwork.ATTRIBUTE_KEY_MAX_SPEED:
                    max_speed = attr[1]

            yield (street, length, max_speed)
        
