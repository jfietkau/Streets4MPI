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

        self.log("Reading OpenStreetMap data...")
        data = GraphBuilder(settings['osm_file'], settings['parser_concurrency'])

        self.log("Building street network...")
        street_network = data.build_street_network()

        if self.process_rank == 0 and settings['persist_traffic_load']:
            self.log("Saving street network to disk...")
            persist_write("street_network_1.s4mpi", street_network)

        self.log("Locating area types...")
        data.find_node_categories()

        self.log("Generating trips...")
        trip_generator = TripGenerator()
        # distribute residents over processes
        number_of_residents = settings['number_of_residents'] / number_of_processes
        if settings['use_residential_nodes_as_origins']:
            potential_origins = data.connected_residential_nodes
        else:
            potential_origins = street_network.get_nodes()
        potential_goals = data.connected_commercial_nodes | data.connected_industrial_nodes
        trips = trip_generator.generate_trips(number_of_residents, potential_origins, potential_goals)

        # run simulation
        simulation = Simulation(street_network, trips, self.log_indent)

        for step in range(settings['max_simulation_steps']):
            self.log("Running simulation step", step + 1, "of", str(settings['max_simulation_steps']) + "...")
            simulation.step()

            # send traffic load to process 0
            communicator.send(simulation.traffic_load, dest=0, tag=step)

            # sum up total traffic load on process 0 and broadcast it
            total_traffic_load = None
            if self.process_rank == 0:
                total_traffic_load = dict()
                for i in range(number_of_processes):
                    local_traffic_load = communicator.recv(source=i, tag=step)
                    for street, usage in local_traffic_load.iteritems():
                        total_usage = usage
                        if street in total_traffic_load.keys():
                            total_usage += total_traffic_load[street]
                        total_traffic_load[street] = total_usage

                if settings['persist_traffic_load']:
                    self.log_indent("Saving traffic load to disk...")
                    persist_write("traffic_load_" + str(step + 1) + ".s4mpi", total_traffic_load)

            # broadcast total traffic load
            total_traffic_load = communicator.bcast(total_traffic_load, root=0)
            simulation.traffic_load = total_traffic_load

        self.log("Done!")

    def log(self, *output):
        if(settings['logging'] == 'stdout'):
            print "[ %s ][ p%d ]" % (datetime.now(), self.process_rank),
            for o in output:
                print o,
            print ''

    def log_indent(self, *output):
        if(settings['logging'] == 'stdout'):
            print "[ %s ][ p%d ]  " % (datetime.now(), self.process_rank),
            for o in output:
                print o,
            print ''

if __name__ == "__main__":
    Streets4MPI()

