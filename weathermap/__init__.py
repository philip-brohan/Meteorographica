# (C) British Crown Copyright 2017, Met Office
#
# This code is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This code is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
"""
This package contains utility functions to simplify making weather-maps. The idea is to get data cubes loaded by :mod:`Meteorographica.data` and plot them as contour plots, colour maps and the like. So there is one function to take a data cube and add it to a :mod:`Cartopy` map as a contour plot; another for a colour map, and so on.

It is probably best illustrated `by example <examples/examples.html>`_.

|
"""

from utils import *
from wind_vectors import *
from wm import *
