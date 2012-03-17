#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# osmdata.py
# Copyright 2012 Julian Fietkau <http://www.julian-fietkau.de/>,
# Joachim Nitschke
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

from math import sqrt, radians, sin, cos, asin
from time import time

from streetnetwork import StreetNetwork 

# This class reads an OSM file and builds a graph out of it
class GraphBuilder(object):

    LATITUDE = 0
    LONGITUDE = 1

    def __init__(self, osmfile, parser_concurrency):
        # parse the input file and save its contents in memory

        # initialize street network
        self.street_network = StreetNetwork()

        # coord pairs as returned from imposm
        self.coords = dict()

        # active copy of OSM data indexed by OSM id
        self.all_osm_relations = dict()
        self.all_osm_ways = dict()
        self.all_osm_nodes = dict()

        # nodes with specific landuse tags
        self.residential_nodes = set()
        self.industrial_nodes = set()
        self.commercial_nodes = set()

        # subset that is also connected to the street network
        self.connected_residential_nodes = set()
        self.connected_industrial_nodes = set()
        self.connected_commercial_nodes = set()

        # mapping from highway types to max speeds
        # we do this so there's always a speed limit for every edge, even if
        # none is in the OSM data
        self.max_speed_map = dict()
        self.max_speed_map['motorway'] = 140
        self.max_speed_map['trunk'] = 120
        self.max_speed_map['primary'] = 100
        self.max_speed_map['secondary'] = 80
        self.max_speed_map['tertiary'] = 70
        self.max_speed_map['road'] = 50
        self.max_speed_map['minor'] = 50
        self.max_speed_map['unclassified'] = 50
        self.max_speed_map['residential'] = 30
        self.max_speed_map['track'] = 30
        self.max_speed_map['service'] = 20
        self.max_speed_map['path'] = 10
        self.max_speed_map['cycleway'] = 1   # >0 to prevent infinite weights
        self.max_speed_map['bridleway'] = 1  # >0 to prevent infinite weights
        self.max_speed_map['pedestrian'] = 1 # >0 to prevent infinite weights
        self.max_speed_map['footway'] = 1    # >0 to prevent infinite weights

        p = OSMParser(concurrency = parser_concurrency,
                      coords_callback = self.coords_callback,
                      nodes_callback = self.nodes_callback,
                      ways_callback = self.ways_callback,
                      relations_callback = self.relations_callback)
        p.parse(osmfile)

    def build_street_network(self):
        # construct the actual graph structure from the input data
        for osmid in self.coords.keys():
            if not self.street_network.has_node(osmid):
                coord = self.coords[osmid]
                self.street_network.add_node(osmid, coord[self.LONGITUDE], coord[self.LATITUDE])

        for osmid, tags, refs in self.all_osm_ways.values():
            if 'highway' in tags:
                for i in range(0, len(refs)-1):
                    street = (refs[i], refs[i+1])

                    # calculate street length
                    length = self.length_haversine(refs[i], refs[i+1])

                    # determine max speed
                    max_speed = 50
                    if 'maxspeed' in tags:
                        if tags['maxspeed'].isdigit():
                            max_speed = int(tags['maxspeed'])
                        elif tags['maxspeed'] == 'none':
                            max_speed = 140
                    elif tags['highway'] in self.max_speed_map.keys():
                        max_speed = self.max_speed_map[tags['highway']]

                    # add street to street network
                    if not self.street_network.has_street(street):
                        self.street_network.add_street(street, length, max_speed)

        return self.street_network

    def find_node_categories(self):
        # collect relevant categories of nodes in their respective sets
        # TODO there has to be a better way to do this
        # TODO do this inside class StreetNetwork?
        for osmid, tags, members in self.all_osm_relations.values():
            if 'landuse' in tags:
                if tags['landuse'] == 'residential':
                    self.residential_nodes = self.residential_nodes | self.get_all_child_nodes(osmid)
                if tags['landuse'] == 'industrial':
                    self.industrial_nodes = self.industrial_nodes | self.get_all_child_nodes(osmid)
                if tags['landuse'] == 'commercial':
                    self.commercial_nodes = self.commercial_nodes | self.get_all_child_nodes(osmid)
        for osmid, tags, refs in self.all_osm_ways.values():
            if 'landuse' in tags:
                if tags['landuse'] == 'residential':
                    self.residential_nodes = self.residential_nodes | self.get_all_child_nodes(osmid)
                if tags['landuse'] == 'industrial':
                    self.industrial_nodes = self.industrial_nodes | self.get_all_child_nodes(osmid)
                if tags['landuse'] == 'commercial':
                    self.commercial_nodes = self.commercial_nodes | self.get_all_child_nodes(osmid)
        for osmid, tags, coords in self.all_osm_nodes.values():
            if 'landuse' in tags:
                if tags['landuse'] == 'residential':
                    self.residential_nodes = self.residential_nodes | self.get_all_child_nodes(osmid)
                if tags['landuse'] == 'industrial':
                    self.industrial_nodes = self.industrial_nodes | self.get_all_child_nodes(osmid)
                if tags['landuse'] == 'commercial':
                    self.commercial_nodes = self.commercial_nodes | self.get_all_child_nodes(osmid)
        street_network_nodes = set(self.street_network.get_nodes())
        self.connected_residential_nodes = self.residential_nodes & street_network_nodes
        self.connected_industrial_nodes = self.industrial_nodes & street_network_nodes
        self.connected_commercial_nodes = self.commercial_nodes & street_network_nodes

    def coords_callback(self, coords):
        for osmid, lon, lat in coords:
            self.coords[osmid] = dict([(self.LATITUDE, lat), (self.LONGITUDE, lon)])

    def nodes_callback(self, nodes):
        for node in nodes:
            self.all_osm_nodes[node[0]] = node

    def ways_callback(self, ways):
        for way in ways:
            self.all_osm_ways[way[0]] = way

    def relations_callback(self, relations):
        for relation in relations:
            self.all_osm_relations[relation[0]] = relation

    def get_all_child_nodes(self, osmid):
        # given any OSM id, construct a set of the ids of all descendant nodes
        if osmid in self.all_osm_nodes.keys():
            return set([osmid])
        if osmid in self.all_osm_relations.keys():
            children = set()
            for osmid, osmtype, role in self.all_osm_relations[osmid][2]:
                children = children | self.get_all_child_nodes(osmid)
            return children
        if osmid in self.all_osm_ways.keys():
            children = set()
            for ref in self.all_osm_ways[osmid][2]:
                children.add(ref)
            return children
        return set()

    def length_euclidean(self, id1, id2):
        # calculate distance on a 2D plane assuming latitude and longitude
        # form a planar uniform coordinate system (obviously not 100% accurate)
        p1 = self.coords[id1]
        p2 = self.coords[id2]
        # assuming distance between to degrees of latitude to be approx.
        # 66.4km as is the case for Hamburg, and distance between two
        # degrees of longitude is always 111.32km
        dist = sqrt( ((p2[self.LATITUDE]-p1[self.LATITUDE])*111.32)**2
                     + ((p2[self.LONGITUDE]-p1[self.LONGITUDE])*66.4)**2 )
        return dist*1000 # return distance in m

    def length_haversine(self, id1, id2):
        # calculate distance using the haversine formula, which incorporates
        # earth curvature
        # see http://en.wikipedia.org/wiki/Haversine_formula
        lat1 = self.coords[id1][self.LATITUDE]
        lon1 = self.coords[id1][self.LONGITUDE]
        lat2 = self.coords[id2][self.LATITUDE]
        lon2 = self.coords[id2][self.LONGITUDE]
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        return 6367000 * c # return distance in m

if __name__ == "__main__":
    # instantiate counter and parser and start parsing
    start = time()

    builder = GraphBuilder('osm/hamburg.osm', 4)

    parsed = time()

    builder.init_graph()

    initialized = time()

    builder.find_node_categories()

    categorized = time()

    paths, distances = shortest_path(builder.graph, 1287690225)

    pathed = time()

    # done
    print "Time parsing OSM data: ", parsed - start, " seconds"
    print "Time initializing data structures: ", initialized - parsed, " seconds"
    print "Time finding node categories: ", categorized - initialized, " seconds"
    print "Time calculating shortest paths: ", pathed - categorized, " seconds"
    print "Nodes: ", len(builder.graph.nodes())
    print "Edges: ", len(builder.graph.edges())
    print "Residential Nodes: ", len(builder.residential_nodes)
    print "Residential Nodes connected to street network: ", len(builder.connected_residential_nodes)
    print "Industrial Nodes: ", len(builder.industrial_nodes)
    print "Industrial Nodes connected to street network: ", len(builder.connected_industrial_nodes)
    print "Commercial Nodes: ", len(builder.commercial_nodes)
    print "Commercial Nodes connected to street network: ", len(builder.connected_commercial_nodes)

