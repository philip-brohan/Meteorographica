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
Functions for assigning, updating, and plotting wind vectors.

"""

import numpy
import pandas
import math

# Allocate wind vector seed points evenly over a given lat,lon
#  region. Uses Bridson's algorithm, modified to allow a set
#  of initial points be supplied.
sub allocate_vector_points(initial_points=None,
                           lat_range=(-90,90),
                           lon_range=(-180,180),
                           scale=1.0):

    cellsize=scale/math.sqrt(2)
    x_n_cells=int(math.ceil((lon_range[1]-lon_range[0])/cellsize))
    y_n_cells=int(math.ceil((lat_range[1]-lat_range[0])/cellsize))

    # Point lon & lat to grid indices
    def grid_coords(x,y):
        return (int(math.floor((x-lon_range[0])/cellsize)), 
                int(math.floor((y-lat_range[0])/cellsize)))

    # Block of cells too close to a point
    def too_close(x,y):
        centre_cell=grid_coords(x,y)
        xmin=max(0,centre_cell[0]-2)
        xmax=min(centre_cell[0]+2,x_n_cells-1)
        ymin=max(0,centre_cell[1]-2)
        ymax=min(centre_cell[1]+2,y_n_cells-1)
        close_idx=numpy.meshgrid(numpy.arange(xmin,xmax),
                                 numpy.arange(ymin,ymax))
        if centre_cell[1]+2<y_n_cells-1:
            
        return(close_idx)


    
