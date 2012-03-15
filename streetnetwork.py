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

# This class represents a street network
class StreetNetwork:
    ATTRIBUTE_KEY_LENGTH = 0
    ATTRIBUTE_KEY_MAX_SPEED = 1

    def __init__(self):
        # graph that holds the street network
        self._graph = graph()

    def exists_street(self, node1, node2):
        return self._graph.has_edge((node1, node2))

    def add_street(self, node1, node2, length, max_speed):
        if self.exists_street(node1, node2): raise AssertionError("Precondition failed: not exists_street(node1, node2)")

        # add nodes if they are not in the graph
        if not self._graph.has_node(node1):
            self._graph.add_node(node1)
        if not self._graph.has_node(node2):
            self._graph.add_node(node2)
        
        # add edge to the nodes
        edge = (node1, node2)
        self._graph.add_edge(edge)

        # set attributes for the edge
        self._graph.add_edge_attribute(edge, (self.ATTRIBUTE_KEY_LENGTH, length,))
        self._graph.add_edge_attribute(edge, (self.ATTRIBUTE_KEY_MAX_SPEED, max_speed,))
