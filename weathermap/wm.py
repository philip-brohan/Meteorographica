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

from . import allocate_vector_points

# Convert an rgb tuple colour string to its hex representation
#  some functions expecting a sequence of colours misinterpret
#  the tuple version.
def rgb_to_hex(rgb):
    rgb = [255*x for x in rgb]
    return '#' + ''.join(['{:02X}'.format(int(round(x))) for x in rgb])

# Add a lat lon grid to an axes
def add_grid(ax,
             linestyle='-',
             linewidth_minor=0.2,linewidth_major=0.5,
             color=(0,0.30,0,0.3),zorder=0,
             sep_major=2,sep_minor=0.5):

    gl_minor=ax.gridlines(linestyle=linestyle,
                          linewidth=linewidth_minor,
                          color=color,
                          zorder=zorder)
    gl_minor.xlocator = matplotlib.ticker.FixedLocator(
                       numpy.arange(-180,180+sep_minor,sep_minor))
    gl_minor.ylocator = matplotlib.ticker.FixedLocator(
                         numpy.arange(-85,58+sep_minor,sep_minor))
    gl_major=ax.gridlines(linestyle=linestyle,
                          linewidth=linewidth_major,
                          color=color,
                          zorder=zorder)
    gl_major.xlocator = matplotlib.ticker.FixedLocator(
                       numpy.arange(-180,180+sep_major,sep_major))
    gl_major.ylocator = matplotlib.ticker.FixedLocator(
                         numpy.arange(-85,85+sep_major,sep_major))

# Make a dummy cube to use as a plot grid
def make_dummy(ax,resolution):

    extent=ax.get_extent()
    pole_latitude=ax.projection.proj4_params['o_lat_p']
    pole_longitude=ax.projection.proj4_params['lon_0']-180
    npg_longitude=ax.projection.proj4_params['o_lon_p']

    cs=iris.coord_systems.RotatedGeogCS(pole_latitude,
                                        pole_longitude,
                                        npg_longitude)
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


# Plot a field as a partially-transparent colour mesh
#  Defaults are for precip
precip_default_colour_dict = {'red'  : ((0.0, 0.0, 0.0), 
                                        (1.0, 0.0, 0.0)), 
                              'green': ((0.0, 0.3, 0.3), 
                                        (1.0, 0.3, 0.3)), 
                              'blue' : ((0.0, 0.0, 0.0), 
                                        (1.0, 0.0, 0.0)), 
                              'alpha': ((0.0, 0.0, 0.0),
                                        (0.2, 0.0, 0.0),
                                        (1.0, 0.95, 0.95)) 
} 
precip_default_cmap= matplotlib.colors.LinearSegmentedColormap('p_cmap',
                                                 precip_default_colour_dict)
temperature_default_colour_dict = {'red'  : ((0.0, 0.0, 0.0), 
                                             (1.0, 1.0, 1.0)), 
                                   'green': ((0.0, 0.0, 0.0), 
                                             (1.0, 0.0, 0.0)), 
                                   'blue' : ((0.0, 1.0, 1.0), 
                                             (1.0, 0.0, 0.0)), 
                                   'alpha': ((0.0, 0.4, 0.4),
                                             (1.0, 0.4, 0.4)) 
} 
temperature_default_cmap= matplotlib.colors.LinearSegmentedColormap('p_cmap',
                                                 temperature_default_colour_dict)
def plot_cmesh(ax,pe,resolution=0.25,
               cmap=precip_default_cmap,
               zorder=4):

    plot_cube=make_dummy(ax,resolution)
    cmesh_p = pe.regrid(plot_cube,iris.analysis.Linear())
    cmesh_p.data=numpy.sqrt(cmesh_p.data)
    lats = cmesh_p.coord('latitude').points
    lons = cmesh_p.coord('longitude').points
    prate_img=ax.pcolorfast(lons, lats, cmesh_p.data, cmap=cmap,
                            vmin=0,vmax=0.025,zorder=zorder)
    return prate_img

# Plot a field as contours
def plot_contour(ax,pe,
                 resolution=0.25,
                 levels=None,
                 colors='black',linewidths=0.5,
                 fontsize=12,
                 zorder=4,label=False):
    plot_cube=make_dummy(ax,resolution)
    contour_p = pe.regrid(plot_cube,iris.analysis.Linear())
    lats = contour_p.coord('latitude').points
    lons = contour_p.coord('longitude').points
    lons,lats = numpy.meshgrid(lons,lats)
    CS=ax.contour(lons, lats, contour_p.data,
                               colors=colors,
                               linewidths=linewidths,
                               levels=levels,
                               zorder=zorder)

    # Label the contours
    if label:
        cl=ax.clabel(CS, inline=1, fontsize=fontsize, fmt='%d',zorder=zorder+0.1)

    return CS

# Plot a (wind) field as vectors
def plot_quiver(ax,ue,ve,points=None,
                scale=None,resolution=1,
                color=(0,0,0,0.25),headwidth=1,
                random_state=None,max_points=10000,
                zorder=5):

    pole_latitude=ax.projection.proj4_params['o_lat_p']
    pole_longitude=ax.projection.proj4_params['lon_0']-180
    projection_iris=iris.coord_systems.RotatedGeogCS(pole_latitude,
                                                     pole_longitude)
    rw=rotate_winds(ue,ve,projection_iris)
    plot_cube=make_dummy(ax,resolution)
    u_p = rw[0].regrid(plot_cube,iris.analysis.Linear())
    v_p = rw[1].regrid(plot_cube,iris.analysis.Linear())
    if points is None:
        if scale is None: scale=resolution
        points=allocate_vector_points(initial_points=None,
                                      lat_range=(min(u_p.coord('latitude').points),
                                                 max(u_p.coord('latitude').points)),
                                      lon_range=(min(u_p.coord('longitude').points),
                                                 max(u_p.coord('longitude').points)),
                                      scale=scale,
                                      random_state=random_state,
                                      max_points=max_points)
    lats = points['Latitude']
    lons = points['Longitude']
    u_interpolator = iris.analysis.Linear().interpolator(u_p, 
                                    ['latitude', 'longitude'])
    v_interpolator = iris.analysis.Linear().interpolator(v_p, 
                                    ['latitude', 'longitude'])
    u_i=numpy.zeros(lons.size)
    v_i=numpy.zeros(lons.size)
    for i in range(lons.size):
        u_i[i]=u_interpolator([lats[i],lons[i]]).data*-1
        v_i[i]=v_interpolator([lats[i],lons[i]]).data*-1
    qv=ax.quiver(lons,lats,u_i,v_i,
                            headwidth=headwidth,
                            color=color,
                            scale=2000,
                            zorder=5)
    return qv

# Plot a wind field as vectors coloured by temperature
def plot_wind_and_temperature(ax,ue,ve,t2,points=None,
                              scale=None,resolution=1,
                              color=(0,0,0,0.25),headwidth=1,
                              random_state=None,max_points=10000,
                              zorder=5):
    pole_latitude=ax.projection.proj4_params['o_lat_p']
    pole_longitude=ax.projection.proj4_params['lon_0']-180
    projection_iris=iris.coord_systems.RotatedGeogCS(pole_latitude,
                                                     pole_longitude)
    plot_cube=make_dummy(ax,resolution)
    t_p = t2.regrid(plot_cube,iris.analysis.Linear())
    if points is None:
        if scale is None: scale=resolution
        points=allocate_vector_points(initial_points=None,
                                      lat_range=(min(t_p.coord('latitude').points),
                                                 max(t_p.coord('latitude').points)),
                                      lon_range=(min(t_p.coord('longitude').points),
                                                 max(t_p.coord('longitude').points)),
                                      scale=scale,
                                      random_state=random_state,
                                      max_points=max_points)
    lats_a = points['Latitude']
    lons_a = points['Longitude']
    t_p.data=(t_p.data-253)/50
    t_p.data=numpy.where(t_p.data >= 1, 1, t_p.data)
    t_p.data=numpy.where(t_p.data < 0,  0, t_p.data)
    t_interpolator = iris.analysis.Linear().interpolator(t_p, 
                                    ['latitude', 'longitude'])
    t_i=numpy.zeros(lons_a.size)
    for i in range(lons_a.size):
        t_i[i]=t_interpolator([lats_a[i],lons_a[i]]).data
    for t in range(0,10,1):
        colour=(t/10.0+0.05,0,0.95-t/10.0,0.75)
        pts_i=numpy.where((t_i>=t/10.0) & (t_i<=t/10.0+0.1))
        if len(pts_i[0])==0: continue
        pts={'Latitude':lats_a[pts_i],
             'Longitude':lons_a[pts_i]}
        plot_quiver(ax,ue,ve,points=pts,scale=scale,resolution=resolution,
                    color=colour,headwidth=headwidth,
                    random_state=random_state,
                    max_points=max_points,
                    zorder=zorder)

# Plot observations as points
def plot_obs(ax,obs,
             obs_projection=ccrs.PlateCarree(),
             lat_label='Latitude',lon_label='Longitude',
             radius=0.1,
             facecolor='yellow',
             edgecolor='black',
             alpha=0.85,
             zorder=2.5):

    rp=ax.projection.transform_points(obs_projection,
                                   obs[lon_label].values,
                                   obs[lat_label].values)
    new_longitude=rp[:,0]
    new_latitude=rp[:,1]

    # Plot each ob as a circle
    for i in range(0,len(new_longitude)):
        ax.add_patch(Circle((new_longitude[i],
                             new_latitude[i]),
                            radius=radius,
                            facecolor=facecolor,
                            edgecolor=edgecolor,
                            alpha=alpha,
                            zorder=zorder))

# Add a label
def plot_label(ax,label,
               color='black',
               facecolor='white',
               x_fraction=0.98,y_fraction=0.02,
               horizontalalignment='right',
               verticalalignment='bottom',
               fontsize=12,
               zorder=5.5):

    extent=ax.get_extent()
    ax.text(extent[0]*(1-x_fraction)+extent[1]*x_fraction,
            extent[2]*(1-y_fraction)+extent[3]*y_fraction,
            label,
            horizontalalignment=horizontalalignment,
            verticalalignment=verticalalignment,
            color=color,
            bbox=dict(facecolor=facecolor,
                      edgecolor=color,
                      boxstyle='round',
                      pad=0.5),
            size=fontsize,
            clip_on=True,
            zorder=zorder)
