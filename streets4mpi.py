#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# streets4mpi.py
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

from datetime import datetime
from random import random
from random import seed

from mpi4py import MPI

from osmdata import GraphBuilder
from tripgenerator import TripGenerator
from simulation import Simulation
from settings import settings
from persistence import persist_write

# This class runs the Streets4MPI program.
class Streets4MPI(object):

    def __init__(self):
        # get process info from mpi
        communicator = MPI.COMM_WORLD
        self.process_rank = communicator.Get_rank()
        number_of_processes = communicator.Get_size()

        self.log("Welcome to Streets4MPI!")
        # set random seed based on process rank
        random_seed = settings["random_seed"] + (37 * self.process_rank)
        seed(random_seed)

        self.log("Reading OpenStreetMap data...")
        data = GraphBuilder(settings["osm_file"], settings["parser_concurrency"])

        self.log("Building street network...")
        street_network = data.build_street_network()

        if self.process_rank == 0 and settings["persist_traffic_load"]:
            self.log_indent("Saving street network to disk...")
            persist_write("street_network_1.s4mpi", street_network)

        self.log("Locating area types...")
        data.find_node_categories()

        self.log("Generating trips...")
        trip_generator = TripGenerator()
        # distribute residents over processes
        number_of_residents = settings["number_of_residents"] / number_of_processes
        if settings["use_residential_origins"]:
            potential_origins = data.connected_residential_nodes
        else:
            potential_origins = street_network.get_nodes()
        potential_goals = data.connected_commercial_nodes | data.connected_industrial_nodes
        trips = trip_generator.generate_trips(number_of_residents, potential_origins, potential_goals)

        # set traffic jam tolerance for this process and its trips
        jam_tolerance = random()
        self.log("Setting traffic jam tolerance to", str(round(jam_tolerance, 2)) + "...")        

        # run simulation
        simulation = Simulation(street_network, trips, jam_tolerance, self.log_indent)

        for step in range(settings["max_simulation_steps"]):
            self.log("Running simulation step", step + 1, "of", str(settings["max_simulation_steps"]) + "...")
            simulation.step()

            # gather local traffic loads from all other processes
            local_traffic_loads = communicator.allgather(simulation.traffic_load)

            # sum up total traffic load
            total_traffic_load = self.merge_dictionaries(local_traffic_loads)
            simulation.traffic_load = total_traffic_load

            if self.process_rank == 0 and settings["persist_traffic_load"]:
                self.log_indent("Saving traffic load to disk...")
                persist_write("traffic_load_" + str(step + 1) + ".s4mpi", total_traffic_load)

        self.log("Done!")

    def merge_dictionaries(self, dictionaries):
        merged_dictionary = dict()

        for dictionary in dictionaries:
            for key, value in dictionary.iteritems():
                total_value = value
                if key in merged_dictionary.keys():
                    total_value += merged_dictionary[key]
                merged_dictionary[key] = total_value

        return merged_dictionary

    def log(self, *output):
        if(settings["logging"] == "stdout"):
            print "[ %s ][ p%d ]" % (datetime.now(), self.process_rank),
            for o in output:
                print o,
            print ""

    def log_indent(self, *output):
        if(settings["logging"] == "stdout"):
            print "[ %s ][ p%d ]  " % (datetime.now(), self.process_rank),
            for o in output:
                print o,
            print ""

if __name__ == "__main__":
    Streets4MPI()

