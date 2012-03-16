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

from streetnetwork import StreetNetwork
from persistence import persist_read

# This class turns persistent street usage data into images
class Visualization(object):

    ATTRIBUTE_KEY_LATITUDE = 0
    ATTRIBUTE_KEY_LONGITUDE = 1

    def __init__(self, street_network_filename, street_usage_filename):
        self.step_counter = 0
        self.street_network_files = glob.glob(street_network_filename)
        self.street_usage_files = glob.glob(street_usage_filename)
        self.resolution = (800, 600)
        self.bounds = ((53.58, 53.62), (9.91, 9.93))
        self.background = Image.new("RGB", self.resolution)
        self.street_network = None
        self.street_usage = None

    def step(self):
        if "street_network_"+str(self.step_counter)+".s4mpi" in self.street_network_files:
            self.street_network = persist_read("street_network_"+str(self.step_counter)+".s4mpi")
            self.street_network_im = Image.new("RGBA", self.resolution, (0, 0, 0, 255))
            draw = ImageDraw.Draw(self.street_network_im)
            for node in self.street_network.get_nodes():
                attrs = dict(self.street_network.get_node_attributes(node))
                point = dict()
                for i in range(2):
                    point[i] = (attrs[i] - self.bounds[i][0]) * self.resolution[i] / (self.bounds[i][1] - self.bounds[i][0])
                print point
                draw.point([point[0], point[1]], fill=(255,0,0,0))
            self.street_network_im.show()

if __name__ == "__main__":

    vis = Visualization("street_network_*.s4mpi", "street_usage_*.s4mpi")
    vis.step()
