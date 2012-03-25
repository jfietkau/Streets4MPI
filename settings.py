#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# settings.py
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

settings = {
    'osm_file' : 'osm/test.osm',
    'parser_concurrency' : 4,
    'number_of_residents' : 100,
    'max_simulation_steps' : 1,

    'logging' : 'stdout',
    'persist_traffic_load' : True,
    'use_residential_nodes_as_origins' : False
}

