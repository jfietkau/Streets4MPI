#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# streets4mpi.py
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

from datetime import datetime

from osmdata import GraphBuilder
from tripmanager import TripManager
from simulation import Simulation
from settings import settings

# This class runs the Streets4MPI program.
class Streets4MPI(object):

    def __init__(self):
        self.log("Welcome to Streets4MPI!")
        self.log("Reading OpenStreetMap data...")
        data = GraphBuilder(settings['osm_file'], settings['parser_concurrency'])
        self.log("Building street network...")
        data.init_graph()
        self.log("Locating area types...")
        data.find_node_categories()
        self.log("Generating trips...")
        tm = TripManager(settings['number_of_residents'],
                         data.connected_residential_nodes,
                         data.connected_commercial_nodes | data.connected_industrial_nodes)
        tm.create_trips()
        sim = Simulation(data.graph, tm.trips, self.log_indent)
        for step in range(settings['max_simulation_steps']):
            self.log("Running simulation step", step + 1, "of", settings['max_simulation_steps'], "...")
            sim.step()
        self.log("Done!")

    def log(self, *output):
        if(settings['logging'] == 'stdout'):
            print '[', datetime.now(), ']',
            for o in output:
                print o,
            print ''

    def log_indent(self, *output):
        if(settings['logging'] == 'stdout'):
            print '[', datetime.now(), ']  ',
            for o in output:
                print o,
            print ''

if __name__ == "__main__":
    Streets4MPI()

