#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# visualization.py
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

import re
from os import listdir
from PIL import Image, ImageChops, ImageDraw, ImageFont
from math import floor
from datetime import datetime

from pygraph.algorithms.accessibility import connected_components

from streetnetwork import StreetNetwork
from persistence import persist_read
from simulation import calculate_driving_speed

# This class turns persistent traffic load data into images
class Visualization(object):

    ATTRIBUTE_KEY_LATITUDE = 0
    ATTRIBUTE_KEY_LONGITUDE = 1
    ATTRIBUTE_KEY_COMPONENT = 2
    ATTRIBUTE_KEY_COORDS = 3

    # Modes:
    # COMPONENTS   - display connected components
    # TRAFFIC_LOAD - display absolute traffic load
    # MAX_SPEED    - display local speed limits
    # IDEAL_SPEED  - display calculated ideal speed based on safe breaking distance
    # ACTUAL_SPEED - display calculated actual speed based on traffic load

    # Colors:
    # HEATMAP      - vary hue on a temperature-inspired scale from dark blue to red
    # MONOCHROME   - vary brightness from black to white

    def __init__(self, street_network_filename_pattern, traffic_load_filename_pattern, mode = 'TRAFFIC_LOAD', color_mode = 'HEATMAP'):
        print "Welcome to Streets4MPI visualization!"
        print "Current display mode:", mode, "with color mode", color_mode

        self.max_resolution = (2000, 2000)
        self.zoom = 1
        self.coord2km = (111.32, 66.4) # distances between 2 deg of lat/lon
        self.bounds = None
        self.street_network = None
        self.node_coords = dict()
        self.mode = mode
        self.color_mode = color_mode
        self.street_network_filename_expression = re.compile(street_network_filename_pattern)
        self.traffic_load_filename_expression = re.compile(traffic_load_filename_pattern)

    def visualize(self):
        # find files
        all_files = listdir('.')
        street_network_files = filter(self.street_network_filename_expression.search, all_files)
        traffic_load_files = filter(self.traffic_load_filename_expression.search, all_files)

        # read street networks
        street_networks = dict()
        for street_network_file in street_network_files:
            street_network = persist_read(street_network_file)
            street_networks[street_network_file] = street_network

        # keep max traffic load to setup legend later
        max_load = 0

        # read traffic loads
        traffic_loads = dict()
        for traffic_load_file in traffic_load_files:
            traffic_load = persist_read(traffic_load_file)
            traffic_loads[traffic_load_file] = traffic_load

            # find max traffic load
            max_load = max(max_load, self.find_max_value(traffic_load))

        step = 0
        while len(traffic_loads.keys()) > 0:
            step += 1
            print "Step counter", step

            # check if there is a street network for the current step and load it
            street_network_filename = "street_network_" + str(step) + ".s4mpi"
            if street_network_filename in street_networks.keys():
                print "  Found street network data, reading..."
                self.street_network = street_networks[street_network_filename]
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

            # check if there is traffic load for the current step and draw it
            traffic_load_filename = "traffic_load_" + str(step) + ".s4mpi"
            if traffic_load_filename in traffic_loads.keys():
                print "  Found traffic load data, reading and drawing..."
                traffic_load = traffic_loads[traffic_load_filename]
                street_network_image = Image.new("RGBA", self.max_resolution, (0, 0, 0, 255))
                draw = ImageDraw.Draw(street_network_image)

                for street, length, max_speed in self.street_network:
                    color = (255, 255, 255, 0) # default: white
                    width = 1 # max_speed / 50 looks bad for motorways
                    value = 0
                    current_traffic_load = 0
                    if street in traffic_load.keys():
                        current_traffic_load = traffic_load[street]
                    if self.mode == 'TRAFFIC_LOAD':
                        value = 1.0 * current_traffic_load / max_load
                    if self.mode == 'MAX_SPEED':
                        value = min(140, 1.0 * max_speed / 140)
                    if self.mode == 'IDEAL_SPEED':
                        ideal_speed = calculate_driving_speed(length, max_speed, 0)
                        value = min(1.0, 1.0 * ideal_speed / 140)
                    if self.mode == 'ACTUAL_SPEED':
                        actual_speed = calculate_driving_speed(length, max_speed, current_traffic_load)
                        value = min(1.0, 1.0 * actual_speed / 140)
                    color = self.value_to_color(value)
                    if self.mode == 'COMPONENTS':
                        component = dict(self.street_network._graph.edge_attributes(street))[Visualization.ATTRIBUTE_KEY_COMPONENT]
                        color = "hsl(" + str(int(137.5*component) % 360) + ",100%,50%)"
                    draw.line([self.node_coords[street[0]], self.node_coords[street[1]]], fill=color, width=width)

                street_network_image = self.image_finalize(street_network_image, max_load)
                print "  Saving image to disk (traffic_load_" + str(step) + ".png) ..."
                street_network_image.save("traffic_load_" + str(step) + ".png")

                # remove current traffic load from dictionary
                del traffic_loads[traffic_load_filename]

        print "Done!"

    def calculate_components(self, graph):
        components = connected_components(graph)
        for edge in graph.edges():
            graph.add_edge_attribute(edge, (Visualization.ATTRIBUTE_KEY_COMPONENT, max(components[edge[0]], components[edge[1]])))

    def find_max_value(self, dictionary):
        max_value = 0
        for value in dictionary.values():
            max_value = max(max_value, 1.0 * value)
        return max_value

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

    def image_finalize(self, street_network_image, max_load):
        # take the current street network and make it pretty
        street_network_image = self.auto_crop(street_network_image)

        white = (255,255,255,0)
        black = (0,0,0,0)
        padding = self.max_resolution[0] / 40
        legend = Image.new("RGBA", street_network_image.size, (0,0,0,255))
        font = ImageFont.load_default()
        draw = ImageDraw.Draw(legend)
        bar_outer_width = self.max_resolution[0] / 50
        bar_inner_width = min(bar_outer_width - 4, int(bar_outer_width * 0.85))
        # make sure the difference is a multiple of 4
        bar_inner_width = bar_inner_width - (bar_outer_width - bar_inner_width) % 4
        bar_offset = max(2, int(bar_outer_width - bar_inner_width) / 2)

        if self.mode in ['TRAFFIC_LOAD', 'MAX_SPEED', 'IDEAL_SPEED', 'ACTUAL_SPEED']:
            draw.rectangle([(0, 0), (bar_outer_width, legend.size[1]-1)], fill = white)
            border_width = int(bar_offset / 2)
            draw.rectangle([(border_width, border_width), (bar_outer_width-border_width, legend.size[1]-1-border_width)], fill = black)
            for y in xrange(bar_offset, legend.size[1]-bar_offset):
                value = 1.0 * (y - bar_offset) / (legend.size[1] - 2 * bar_offset)
                color = self.value_to_color(1.0 - value) # highest value at the top
                draw.line([(bar_offset, y), (bar_offset + bar_inner_width, y)], fill=color)
            if self.mode == 'TRAFFIC_LOAD':
                top_text = str(round(max_load, 1)) + " cars gone through"
                bottom_text = "0 cars gone through"
            if self.mode == 'MAX_SPEED':
                top_text = "speed limit: 140 km/h or higher"
                bottom_text = "speed limit: 0 km/h"
            if self.mode == 'IDEAL_SPEED':
                top_text = "ideal driving speed: 140 km/h or higher"
                bottom_text = "ideal driving speed: 0 km/h"
            if self.mode == 'ACTUAL_SPEED':
                top_text = "actual driving speed: 140 km/h or higher"
                bottom_text = "actual driving speed: 0 km/h"
            draw.text((int(bar_outer_width * 1.3), 0), top_text, font = font, fill = white)
            box = draw.textsize(bottom_text, font = font)
            draw.text((int(bar_outer_width * 1.3), legend.size[1] - box[1]), bottom_text, font = font, fill = white)

        legend = self.auto_crop(legend)

        copyright = "Generated by Streets4MPI version 0.1 using data from the OpenStreetMap project. Licensed under CC-BY-SA 2.0 (https://creativecommons.org/licenses/by-sa/2.0/)."
        copyright_size = draw.textsize(copyright, font = font)

        final_width = street_network_image.size[0] + legend.size[0] + 3 * padding
        final_height = legend.size[1] + 2 * padding + copyright_size[1] + 1
        final = Image.new("RGB", (final_width, final_height), black)
        final.paste(street_network_image, (padding, padding))
        final.paste(legend, (street_network_image.size[0] + 2 * padding, padding))
        ImageDraw.Draw(final).text((2, legend.size[1] + 2 * padding), copyright, font = font, fill = white)

        return final

    def auto_crop(self, image):
        # remove black edges from image
        empty = Image.new("RGBA", image.size, (0,0,0))
        difference = ImageChops.difference(image, empty)
        bbox = difference.getbbox()
        return image.crop(bbox)        

if __name__ == "__main__":
    visualization = Visualization("^street_network_[0-9]+.s4mpi$", "^traffic_load_[0-9]+.s4mpi$", mode='MAX_SPEED')
    visualization.visualize()

