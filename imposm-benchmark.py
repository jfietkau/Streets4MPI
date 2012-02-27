#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# imposm-benchmark.py       
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

from imposm.parser import OSMParser

from pygraph.classes.graph import graph
from pygraph.algorithms.minmax import shortest_path

import time

# This class reads an OSM file and builds a graph out of it
class GraphBuilder(object):

    def __init__(self, osmfile):
        self.graph = graph()
        self.edges = []
        # Callbacks are done in parallel, but we can't add the edges before we
        # add the respective nodes. So, we save a list of all edges and insert
        # them into the graph after we're done parsing.
        p = OSMParser(concurrency = 4,
                      coords_callback = self.coords,
                      ways_callback = self.ways)
        p.parse(osmfile)
        for x in self.edges:
            # The same edge might belong to several OSM ways.
            if not self.graph.has_edge(x):
                self.graph.add_edge(x)
        edges = []

    def coords(self, coords):
        # callback method for coords
        for osmid, lon, lat in coords:
            # TODO only add coords if they belong to an OSM highway, not any
            # other kind of way
            self.graph.add_nodes([osmid])

    def ways(self, ways):
        # callback method for ways
        for osmid, tags, refs in ways:
            if 'highway' in tags:
                for i in range(0, len(refs)-1):
                    self.edges.append((refs[i], refs[i+1]))

if __name__ == "__main__":
    # instantiate counter and parser and start parsing
    start = time.time()

    builder = GraphBuilder('osm/hamburg.osm')

    parsed = time.time()

    paths, distances = shortest_path(builder.graph, 1619962885)

    pathed = time.time()

    # done
    print "Time parsing OSM data: ", parsed - start, " seconds"
    print "Time calculating shortest paths: ", pathed - parsed, " seconds"
    print "Nodes: ", len(builder.graph.nodes())
    print "Edges: ", len(builder.graph.edges())

