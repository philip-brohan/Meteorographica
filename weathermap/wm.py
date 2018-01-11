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
Weather map plotting functions.        .

"""

import os
import math

import virtualtime # fixes datetime to work pre-1900
import datetime

import numpy
import pandas

import matplotlib
import matplotlib.colors
from matplotlib.patches import Circle

import iris
from iris.analysis.cartography import rotate_winds

import cartopy
import cartopy.crs as ccrs

# Add a lat lon grid to an axes
def add_grid(ax,
             linestyle='-',
             linewidth_minor=0.2,linewidth_major=1,
             color=(0,0.50,0,0.3),zorder=0,
             sep_major=2,sep_minor=0.5):

    gl_minor=ax.gridlines(linestyle=linestyle,
                          linewidth=linewidth_minor,
                          color=color,
                          zorder=zorder)
    gl_minor.xlocator = matplotlib.ticker.FixedLocator(numpy.arange(-180,180,sep_minor))
    gl_minor.ylocator = matplotlib.ticker.FixedLocator(numpy.arange(-90,90,sep_minor))
    gl_ajor=ax.gridlines(linestyle=linestyle,
                          linewidth=linewidth_major,
                          color=color,
                          zorder=zorder)
    gl_major.xlocator = matplotlib.ticker.FixedLocator(numpy.arange(-180,180,sep_major))
    gl_major.ylocator = matplotlib.ticker.FixedLocator(numpy.arange(-90,90,sep_major))

# Make a dummy cube to use as a plot grid
def make_dummy(extent,resolution,pole_latitude=90,pole_longitude=180)

    cs=iris.coord_systems.RotatedGeogCS(pole_latitude,
                                        pole_longitude)
    lat_values=numpy.arange(extent[2]-2,extent[3]+2,resolution)
    latitude = iris.coords.DimCoord(lat_values,
                                    standard_name='latitude',
                                    units='degrees_north',
                                    coord_system=cs)
    lon_values=numpy.arange(extent[0]-2,extent[1]+2,resolution)
    longitude = iris.coords.DimCoord(lon_values,
                                     standard_name='longitude',
                                     units='degrees_east',
                                     coord_system=cs)
    dummy_data = numpy.zeros((len(lat_values), len(lon_values)))
    plot_cube = iris.cube.Cube(dummy_data,
                               dim_coords_and_dims=[(latitude, 0),
                                                    (longitude, 1)])
    return plot_cube


