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

from array import array
from datetime import datetime
from itertools import repeat
from random import random
from random import seed, randint
from timeit import timeit

from osmdata import GraphBuilder
from persistence import persist_write
from settings import settings
from simulation import Simulation
from tripgenerator import TripGenerator
from utils import merge_arrays

import pytracemalloc
# This class runs the Streets4MPI program.
class Streets4Serial(object):

    def __init__(self):
        self.log("Welcome to Streets4MPI!")
        # set random seed based on process rank
        random_seed = settings["random_seed"] + (37 * randint(1, 20))
        seed(random_seed)

        self.log("Reading OpenStreetMap data...")
        data = GraphBuilder(settings["osm_file"])

        self.log("Building street network...")
        street_network = data.build_street_network()

        if settings["persist_traffic_load"]:
            self.log_indent("Saving street network to disk...")
            persist_write("street_network_1.s4mpi", street_network)

        self.log("Locating area types...")
        data.find_node_categories()

        self.log("Generating trips...")
        trip_generator = TripGenerator()
        # distribute residents over processes
        number_of_residents = settings["number_of_residents"]
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
            if step > 0 and step % settings["steps_between_street_construction"] == 0:
                self.log_indent("Road construction taking place...")
                simulation.road_construction()
                if settings["persist_traffic_load"]:
                    persist_write("street_network_" + str(step + 1) + ".s4mpi", simulation.street_network)

            self.log("Running simulation step", step + 1, "of", str(settings["max_simulation_steps"]) + "...")
            simulation.step()

            # gather local traffic loads from all other processes
            self.log("Exchanging traffic load data between nodes...")
            total_traffic_load = array("I", repeat(0, len(simulation.traffic_load)))
            simulation.traffic_load = total_traffic_load
            simulation.cumulative_traffic_load = merge_arrays((total_traffic_load, simulation.cumulative_traffic_load))

            if settings["persist_traffic_load"]:
                self.log_indent("Saving traffic load to disk...")
                persist_write("traffic_load_" + str(step + 1) + ".s4mpi", total_traffic_load, is_array=True)

            del total_traffic_load

        self.log("Done!")

    def log(self, *output):
        if (settings["logging"] == "stdout"):
            print "[ %s ]  " % (datetime.now()),
            for o in output:
                print o,
            print ""

    def log_indent(self, *output):
        if (settings["logging"] == "stdout"):
            print "[ %s ]  " % (datetime.now()),
            for o in output:
                print o,
            print ""


def display_top(snapshot, key_type='lineno', limit=10):
    snapshot = snapshot.filter_traces((
        tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
        tracemalloc.Filter(False, "<unknown>"),
    ))
    top_stats = snapshot.statistics(key_type)

    print("Top %s lines" % limit)
    for index, stat in enumerate(top_stats[:limit], 1):
        frame = stat.traceback[0]
        # replace "/path/to/module/file.py" with "module/file.py"
        filename = os.sep.join(frame.filename.split(os.sep)[-2:])
        print("#%s: %s:%s: %.1f KiB"
              % (index, filename, frame.lineno, stat.size / 1024))
        line = linecache.getline(frame.filename, frame.lineno).strip()
        if line:
            print('    %s' % line)

    other = top_stats[limit:]
    if other:
        size = sum(stat.size for stat in other)
        print("%s other: %.1f KiB" % (len(other), size / 1024))
    total = sum(stat.size for stat in top_stats)
    print("Total allocated size: %.1f KiB" % (total / 1024))

if __name__ == "__main__":
    tracemalloc.start()
    #print timeit(stmt=Streets4Serial,
    #             number=10)
    Streets4Serial()
    snapshot = tracemalloc.take_snapshot()
    display_top(snapshot)
