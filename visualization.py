#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# visualization.py
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

import glob
from PIL import Image, ImageDraw
from math import floor

from streetnetwork import StreetNetwork
from persistence import persist_read

from pygraph.algorithms.accessibility import connected_components

# This class turns persistent street usage data into images
class Visualization(object):

    ATTRIBUTE_KEY_LATITUDE = 0
    ATTRIBUTE_KEY_LONGITUDE = 1
    ATTRIBUTE_KEY_COMPONENT = 2

    MODE_COMPONENTS = 'MODE_COMPONENTS'
    MODE_USAGE      = 'MODE_USAGE'

    def __init__(self, street_network_filename, street_usage_filename, mode):
        print "Welcome to Streets4MPI visualization!"
        print "Initializing data structures..."
        self.step_counter = 0
        self.street_network_files = glob.glob(street_network_filename)
        self.street_usage_files = glob.glob(street_usage_filename)
        self.max_resolution = (600, 600)
        self.zoom = 1
        self.coord2km = (111.32, 66.4) # distances between 2 deg of lat/lon
        self.bounds = None
        self.background = Image.new("RGB", self.max_resolution)
        self.street_network = None
        self.street_usage = None
        self.node_coords = dict()
        self.mode = mode

    def step(self):

        print "Step counter", self.step_counter
        if "street_network_"+str(self.step_counter)+".s4mpi" in self.street_network_files:
            print "  Found street network data, reading..."
            self.street_network = persist_read("street_network_"+str(self.step_counter)+".s4mpi")
            self.bounds = self.street_network.bounds
            self.street_network_im = Image.new("RGBA", self.max_resolution, (0, 0, 0, 255))
            self.zoom = 600 / max((self.bounds[0][1] - self.bounds[0][0]) * self.coord2km[0],
                                  (self.bounds[1][1] - self.bounds[1][0]) * self.coord2km[1])
            for node in self.street_network.get_nodes():
                attrs = dict(self.street_network.get_node_attributes(node))
                point = dict()
                for i in range(2):
                    point[i] = (attrs[i] - self.bounds[i][0]) * self.coord2km[i] * self.zoom
                self.node_coords[node] = (point[0], point[1])
            if self.mode == Visualization.MODE_COMPONENTS:
                  self.calculate_components(self.street_network._graph)

        if "street_usage_"+str(self.step_counter)+".s4mpi" in self.street_usage_files:
            print "  Found street usage data, reading and drawing..."
            self.street_usage = persist_read("street_usage_"+str(self.step_counter)+".s4mpi")
            draw = ImageDraw.Draw(self.street_network_im)
            usage = 0
            for street, length, max_speed in self.street_network:
                if self.mode == Visualization.MODE_USAGE:
                    brightness = min(255, 55+1*self.street_usage[street])
                    color = (brightness, 0, 0, 0)
                if self.mode == Visualization.MODE_COMPONENTS:
                    component = dict(self.street_network._graph.edge_attributes(street))[2]
                    color = "hsl(" + str(int(137.5*component) % 360) + ",100%,50%)"
                draw.line([self.node_coords[street[0]], self.node_coords[street[1]]], fill=color)
            self.street_network_im.show()

        self.step_counter += 1

    def calculate_components(self, graph):
        components = connected_components(graph)
        for edge in graph.edges():
            graph.add_edge_attribute(edge, (Visualization.ATTRIBUTE_KEY_COMPONENT, max(components[edge[0]], components[edge[1]])))

if __name__ == "__main__":

    vis = Visualization("street_network_*.s4mpi", "street_usage_*.s4mpi", Visualization.MODE_COMPONENTS)
    vis.step()
    vis.step()

