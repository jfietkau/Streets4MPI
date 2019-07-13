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
    # technical settings
    "osm_file": "osm/test.osm",
    "logging": "stdout",
    "persist_traffic_load": True,
    "random_seed": 3756917,  # set to None to use system time

    # simulation settings
    "max_simulation_steps": 10,
    "number_of_residents": 100,
    "use_residential_origins": False,
    # period over which the traffic is distributed (24h = the hole day)
    "traffic_period_duration": 8,  # h
    "car_length": 4,  # m
    "min_breaking_distance": 0.001,  # m
    # take breaking deceleration for asphalt
    # see http://www.bense-jessen.de/Infos/Page10430/page10430.html
    "braking_deceleration": 7.5,  # m/s²
    "steps_between_street_construction": 10,
    "trip_volume": 1
}
