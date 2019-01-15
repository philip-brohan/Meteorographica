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

#Functions for assigning, updating, and plotting wind vectors.

import numpy
import math
import sklearn.utils

# Generate a set of random points at distance between 1 and 2
#  from (0,0) - we'll sample from these many times.
# Uses a fixed seed, so should get same set of points every time
random_state = sklearn.utils.check_random_state(12) # Arbitrary argument
sample_cache_x=numpy.array(random_state.uniform(-3,3,10000))
sample_cache_y=numpy.array(random_state.uniform(-3,3,10000))
sample_mag=sample_cache_x**2+sample_cache_y**2
sample_selected=numpy.logical_and(sample_mag>1,sample_mag<6)
sample_cache_x=sample_cache_x[sample_selected]
sample_cache_y=sample_cache_y[sample_selected]

# Allocate wind vector seed points evenly over a given lat,lon
#  region. Uses Bridson's algorithm, modified to allow a set
#  of initial points be supplied.
def allocate_vector_points(initial_points=None,
                           lat_range=(-90,90),
                           lon_range=(-180,180),
                           scale=5.0,
                           random_state=None,
                           max_points=10000):
    """Allocate even coverage of points over a 2d space - for wind vectors.

    *WARNING* This function is broken/unfinished - do not use.

    To plot wind vectors in a video, we need an even coverage that moves with the wind. So we need a function that will take a set of wind-vector locations and keep their coverage fairly even, by removing any that have got too close together, and seeding new ones to fill any holes in the coverage.


    Args:
        initial points (:obj:`dict`, optional): None (default) or the output from a previous run of this function (see return value).
        lat_range (:obj:`list`, optional): The latitude range to cover with points. Defaults to (-90,90).
        lon_range (:obj:`list`, optional): The longitude range to cover with points. Defaults to (-180,180).
        scale (:obj:`float`): Characteristic separation between points (in degrees).
        random_state (None|:obj:`int`|:obj:`numpy.random.RandomState`): Random number generation seed, see :func:`sklearn.utils.check_random_state`.
        max_points (:obj:`int`, optional): Maximum number of points to allocate, defaults to 10,000.


    Returns:
        :obj:`dict`: Dictionary with components 'Longitude', 'Latitude', (both arrays of float) and 'Age' (array of int). The first two give the positions of each point, and ther last counts how many times each point has been updated by this function.

    Raises:
        StandardError: if max_points is too small - more points than this are needed to cover the region.

    |
    """
    

    random_state=sklearn.utils.check_random_state(random_state)
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
        # 5x5 block around the centre cell
        close_idx=numpy.meshgrid(numpy.arange(centre_cell[0]-2,
                                              centre_cell[0]+3),
                                 numpy.arange(centre_cell[1]-2,
                                              centre_cell[1]+3))
        # remove the corners
        corners=numpy.array((0,4,20,24))
        close_idx[0]=numpy.delete(close_idx[0],corners)
        close_idx[1]=numpy.delete(close_idx[1],corners)
        # remove any points outside the grid range
        in_p=numpy.logical_and(close_idx[0]>=0,
                               close_idx[0]<x_n_cells)
        close_idx[0]=close_idx[0][in_p]
        close_idx[1]=close_idx[1][in_p]
        in_p=numpy.logical_and(close_idx[1]>=0,
                               close_idx[1]<y_n_cells)
        close_idx[0]=close_idx[0][in_p]
        close_idx[1]=close_idx[1][in_p]
        return(close_idx)

    # Try and find a new point close to a seed point
    def find_new(x,y):
        sub_s=random_state.randint(len(sample_cache_x),size=100)
        for samp in sub_s:
            if (x+sample_cache_x[samp]*scale<lon_range[0] or
                x+sample_cache_x[samp]*scale>lon_range[1] or
                y+sample_cache_y[samp]*scale<lat_range[0] or
                y+sample_cache_y[samp]*scale>lat_range[1]): continue
            gc=grid_coords(x+sample_cache_x[samp]*scale,
                           y+sample_cache_y[samp]*scale)
            if(occupied[gc[0],gc[1]]==0): return (x+sample_cache_x[samp]*scale,
                                                  y+sample_cache_y[samp]*scale)
        return None
        
    # Store the allocated points in a dictionary
    allocated={'Latitude': numpy.zeros([max_points],float),
               'Longitude':numpy.zeros([max_points],float),
               'Age':      numpy.zeros([max_points],int)}
    n_allocated=0 # Nothing in it yet
    # Store the culled points similarly
    culled={'Latitude': numpy.zeros([max_points],float),
            'Longitude':numpy.zeros([max_points],float),
            'Age':      numpy.zeros([max_points],int)}
    n_culled=0 # Nothing in it yet
    active=numpy.zeros([max_points])

    # Grid marking occupied cells
    occupied=numpy.zeros([x_n_cells,y_n_cells]) # 0=free cell

    # Insert the initial points, rejecting any that overlap
    if initial_points is not None:
        for init_i in range(0,len(initial_points['Age'])):
            if initial_points['Latitude'][init_i] < lat_range[0] or\
               initial_points['Latitude'][init_i] > lat_range[1]: continue
            if initial_points['Longitude'][init_i] < lon_range[0] or\
               initial_points['Longitude'][init_i] > lon_range[1]: continue
            cdrs=grid_coords(initial_points['Longitude'][init_i],
                             initial_points['Latitude'][init_i])
            if occupied[cdrs[0],cdrs[1]]!=0: continue  # reject
            # Add it to the newly allocated list
            allocated['Latitude'][n_allocated]=initial_points['Latitude'][init_i]
            allocated['Longitude'][n_allocated]=initial_points['Longitude'][init_i]
            allocated['Age'][n_allocated]=initial_points['Age'][init_i]+1
            # Mark the region around it as occupied
            tc=too_close(initial_points['Longitude'][init_i],
                         initial_points['Latitude'][init_i])
            occupied[tc[0],tc[1]]=1
            active[n_allocated]=1 # Seed new points from this one
            n_allocated +=1
            if n_allocated>max_points:
                raise Exception("Insufficient wind points")

    # Add a seed point if there were no initial points
    if n_allocated==0:
        seed_x=lon_range[0]*.9+lon_range[1]*.1
        seed_y=lat_range[0]*.9+lat_range[1]*.1
        allocated['Longitude'][n_allocated]=seed_x
        allocated['Latitude'][n_allocated]=seed_y
        allocated['Age'][n_allocated]=0
        tc=too_close(seed_x,seed_y)
        occupied[tc[0],tc[1]]=1
        active[n_allocated]=1 # Seed new points from this one
        n_allocated +=1

    # Fill in remaining space with Bridson's method
    while len(numpy.where(active==1)[0])>0:
        current=min(numpy.where(active==1)[0])
        new_point=find_new(allocated['Longitude'][current],
                           allocated['Latitude'][current])
        if new_point is None:
            active[current]=0
            continue
        allocated['Longitude'][n_allocated]=new_point[0]
        allocated['Latitude'][n_allocated]=new_point[1]
        allocated['Age'][n_allocated]=0
        tc=too_close(new_point[0],new_point[1])
        occupied[tc[0],tc[1]]=1
        active[n_allocated]=1
        n_allocated +=1
        if n_allocated>max_points:
            raise Exception("Insufficient wind points")

    return {'Longitude': allocated['Longitude'][0:n_allocated],
            'Latitude':  allocated['Latitude'][0:n_allocated],
            'Age':       allocated['Age'][0:n_allocated]}
