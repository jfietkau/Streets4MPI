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

import re
from os import listdir
from PIL import Image, ImageChops, ImageDraw, ImageFont
from math import floor
from datetime import datetime

from streetnetwork import StreetNetwork
from persistence import persist_read

from pygraph.algorithms.accessibility import connected_components

# This class turns persistent traffic load data into images
class Visualization(object):

    ATTRIBUTE_KEY_LATITUDE = 0
    ATTRIBUTE_KEY_LONGITUDE = 1
    ATTRIBUTE_KEY_COMPONENT = 2
    ATTRIBUTE_KEY_COORDS = 3

    # Modes:
    # COMPONENTS - display connected components
    # USAGE      - display relative traffic load
    # AMOUNT     - display absolute traffic load
    # MAXSPEED   - display local speed limits

    # Colors:
    # HEATMAP    - vary hue on a temperature-inspired scale from dark blue to red
    # MONOCHROME - vary brightness from black to white

    def __init__(self, street_network_filename, traffic_load_filename, mode = 'USAGE', color_mode = 'HEATMAP'):
        print "Welcome to Streets4MPI visualization!"
        print "Current display mode:", mode, "with color mode", color_mode
        print "Initializing data structures..."
        self.step_counter = 0
        self.max_resolution = (2000, 2000)
        self.zoom = 1
        self.coord2km = (111.32, 66.4) # distances between 2 deg of lat/lon
        self.bounds = None
        self.street_network = None
        self.traffic_load = None
        self.node_coords = dict()
        self.mode = mode
        self.color_mode = color_mode

        all_files = listdir('.')
        
        regex_network = re.compile(street_network_filename)
        regex_usage = re.compile(traffic_load_filename)
        self.street_network_files = filter(regex_network.search, all_files)
        self.traffic_load_files = filter(regex_usage.search, all_files)

    def finalize(self):
        print "Done!"

    def step(self):

        self.step_counter += 1
        print "Step counter", self.step_counter

        if "street_network_"+str(self.step_counter)+".s4mpi" in self.street_network_files:

            print "  Found street network data, reading..."
            self.street_network = persist_read("street_network_"+str(self.step_counter)+".s4mpi")
            self.bounds = self.street_network.bounds
            self.zoom = self.max_resolution[0] / max((self.bounds[0][1] - self.bounds[0][0]) * self.coord2km[0],
                                  (self.bounds[1][1] - self.bounds[1][0]) * self.coord2km[1])

            for node in self.street_network.get_nodes():
                attrs = dict(self.street_network.get_node_attributes(node))
                point = dict()
                for i in range(2):
                    point[i] = (attrs[i] - self.bounds[i][0]) * self.coord2km[i] * self.zoom
                self.node_coords[node] = (point[1], self.max_resolution[1] - point[0]) # x = longitude, y = latitude

            if self.mode == 'COMPONENTS':
                  self.calculate_components(self.street_network._graph)

            self.street_network_files.remove("street_network_"+str(self.step_counter)+".s4mpi")

        if "traffic_load_"+str(self.step_counter)+".s4mpi" in self.traffic_load_files:

            print "  Found traffic load data, reading and drawing..."
            self.traffic_load = persist_read("traffic_load_"+str(self.step_counter)+".s4mpi")
            self.street_network_im = Image.new("RGBA", self.max_resolution, (0, 0, 0, 255))
            draw = ImageDraw.Draw(self.street_network_im)

            if self.mode == 'AMOUNT':
                max_amount = self.find_max_amount()
            if self.mode == 'USAGE':
                max_usage = self.find_max_usage()

            for street, length, max_speed in self.street_network:
                color = (255, 255, 255, 0) # default: white
                width = max_speed / 50
                value = 0
                if self.mode == 'AMOUNT':
                    value = 1.0 * self.traffic_load[street] / max_amount
                if self.mode == 'USAGE':
                    value = min(1.0, 5 * (1.0 * self.traffic_load[street]) / (max_speed * max_usage))
                if self.mode == 'MAXSPEED':
                    value = min(1.0, 1.0 * max_speed / 140)
                color = self.value_to_color(value)
                if self.mode == 'COMPONENTS':
                    component = dict(self.street_network._graph.edge_attributes(street))[Visualization.ATTRIBUTE_KEY_COMPONENT]
                    color = "hsl(" + str(int(137.5*component) % 360) + ",100%,50%)"
                draw.line([self.node_coords[street[0]], self.node_coords[street[1]]], fill=color, width=width)

            self.image_finalize()
            print "  Saving image to disk (traffic_load_"+str(self.step_counter)+".png) ..."
            self.street_network_im.save("traffic_load_"+str(self.step_counter)+".png")

            self.traffic_load_files.remove("traffic_load_"+str(self.step_counter)+".s4mpi")

    def calculate_components(self, graph):
        components = connected_components(graph)
        for edge in graph.edges():
            graph.add_edge_attribute(edge, (Visualization.ATTRIBUTE_KEY_COMPONENT, max(components[edge[0]], components[edge[1]])))

    def find_max_amount(self):
        amount = 0
        for street, length, max_speed in self.street_network:
            amount = max(amount, 1.0 * self.traffic_load[street])
        return amount

    def find_max_usage(self):
        usage = 0
        for street, length, max_speed in self.street_network:
            usage = max(usage, 1.0 * self.traffic_load[street] / max_speed)
        return usage

    def value_to_color(self, value):
        value = min(1.0, max(0.0, value))
        if self.color_mode == 'MONOCHROME':
            brightness = min(255, int(15 + 240 * value))
            return (brightness, brightness, brightness, 0)
        if self.color_mode == 'HEATMAP':
            if value <= 0.2: # almost black to blue
                return "hsl(260,100%," + str(5+int(45*5*value)) + "%)"
            else: # blue to red
                return "hsl(" + str(int(260*(1-(value-0.2)/0.8))) + ",100%,50%)"

    def image_finalize(self):
        # take the current street network and make it pretty
        self.street_network_im = self.auto_crop(self.street_network_im)

        white = (255,255,255,0)
        black = (0,0,0,0)
        padding = self.max_resolution[0] / 40
        legend = Image.new("RGBA", self.street_network_im.size, (0,0,0,255))
        font = ImageFont.load_default()
        draw = ImageDraw.Draw(legend)
        bar_outer_width = self.max_resolution[0] / 50
        bar_inner_width = min(bar_outer_width - 4, int(bar_outer_width * 0.85))
        # make sure the difference is a multiple of 4
        bar_inner_width = bar_inner_width - (bar_outer_width - bar_inner_width) % 4
        bar_offset = max(2, int(bar_outer_width - bar_inner_width) / 2)

        if self.mode in ['USAGE', 'AMOUNT', 'MAXSPEED']:
            draw.rectangle([(0, 0), (bar_outer_width, legend.size[1]-1)], fill = white)
            border_width = int(bar_offset / 2)
            draw.rectangle([(border_width, border_width), (bar_outer_width-border_width, legend.size[1]-1-border_width)], fill = black)
            for y in xrange(bar_offset, legend.size[1]-bar_offset):
                value = 1.0 * (y - bar_offset) / (legend.size[1] - 2 * bar_offset)
                color = self.value_to_color(1.0 - value) # highest value at the top
                draw.line([(bar_offset, y), (bar_offset + bar_inner_width, y)], fill=color)
            if self.mode == 'AMOUNT':
                top_text = str(round(self.find_max_amount(), 1))+ " cars gone through"
                bottom_text = "0 cars gone through"
            if self.mode == 'USAGE':
                top_text = str(round(self.find_max_usage(), 1))+ " car density (cars per allowed km/h)"
                bottom_text = "0 car density (cars per allowed km/h)"
            if self.mode == 'MAXSPEED':
                top_text = "speed limit: 140 km/h or higher"
                bottom_text = "speed limit: 0 km/h"
            draw.text((int(bar_outer_width * 1.3), 0), top_text, font = font, fill = white)
            box = draw.textsize(bottom_text, font = font)
            draw.text((int(bar_outer_width * 1.3), legend.size[1] - box[1]), bottom_text, font = font, fill = white)

        legend = self.auto_crop(legend)

        copyright = "Generated by Streets4MPI version 0.1 using data from the OpenStreetMap project. Licensed under CC-BY-SA 2.0 (https://creativecommons.org/licenses/by-sa/2.0/)."
        copyright_size = draw.textsize(copyright, font = font)

        final_width = self.street_network_im.size[0] + legend.size[0] + 3 * padding
        final_height = legend.size[1] + 2 * padding + copyright_size[1] + 1
        final = Image.new("RGB", (final_width, final_height), black)
        final.paste(self.street_network_im, (padding, padding))
        final.paste(legend, (self.street_network_im.size[0] + 2 * padding, padding))
        ImageDraw.Draw(final).text((2, legend.size[1] + 2 * padding), copyright, font = font, fill = white)

        self.street_network_im = final

    def auto_crop(self, image):
        # remove black edges from image
        empty = Image.new("RGBA", image.size, (0,0,0))
        difference = ImageChops.difference(image, empty)
        bbox = difference.getbbox()
        return image.crop(bbox)        

if __name__ == "__main__":

    vis = Visualization("^street_network_[0-9]+.s4mpi$", "^traffic_load_[0-9]+.s4mpi$")

    while len(vis.street_network_files + vis.traffic_load_files) > 0:
        vis.step()

    vis.finalize()

