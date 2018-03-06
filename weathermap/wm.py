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

# Weather map plotting functions.        

import os
import math

import virtualtime # fixes datetime to work pre-1900
import datetime

import numpy
import pandas

import matplotlib
import matplotlib.colors
import matplotlib.patches

import iris
import iris.analysis.cartography

import cartopy
import cartopy.crs as ccrs

from wind_vectors import allocate_vector_points

# Convert an rgb tuple colour string to its hex representation
#  some functions expecting a sequence of colours misinterpret
#  the tuple version.
def _rgb_to_hex(rgb):
    rgb = [255*x for x in rgb]
    return '#' + ''.join(['{:02X}'.format(int(round(x))) for x in rgb])

# Add a lat lon grid to an axes
def add_grid(ax,
             linestyle='-',
             linewidth_minor=0.2,linewidth_major=0.5,
             color=(0,0.30,0,0.3),zorder=0,
             sep_major=2,sep_minor=0.5):
    """Add a lat-lon grid to the map.

    Actually plots two grids, a minor grid at a narrow spacing with thin lines, and a major grid at a wider spacing with thicker lines. Note that the grids only cover the latitude range -85 to 85, because the line spacings become too small very close to the poles on a rotated grid.

    Args:
        ax (:obj:`cartopy.mpl.geoaxes.GeoAxes`): Axes on which to draw.
        linestyle (:obj:`str`, optional): See :meth:`matplotlib.lines.Line2D.set_linestyle`. Defaults to '-'.
        linewidth_minor (:obj:`float`, optional): Line width for minor grid. Defaults to 0.2.
        linewidth_major (:obj:`float`, optional): Line width for major grid. Defaults to 0.5.
        color (see :mod:`matplotlib.colors`, optional): Grid colour. Defaults to (0,0.30,0,0.3).
        sep_minor (:obj:`float`, optional): Separation, in degrees, of the minor grid lines. Defaults to 0.5.
        sep_major (:obj:`float`, optional): Separation, in degrees, of the major grid lines. Defaults to 2.0.
        zorder (:obj:`float`, optional): Standard matplotlib parameter determining which things are plotted on top (high zorder), and which underneath (low zorder), Defaults to 0 - at the bottom.

    Returns:
        Nothing - adds the grid to the plot as a side effect.

    |
    """

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
def _make_dummy(ax,resolution):

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
    """Plots a variable as a colour map.

    This is the same as :meth:`matplotlib.axes.Axes.pcolorfast`, except that it takes an :class:`iris.cube.Cube` instead of an array of colour values, and its colour defaults are chosen for plots of precipitation rate.

    Args:
        ax (:obj:`cartopy.mpl.geoaxes.GeoAxes`): Axes on which to draw.
        pe (:obj:`iris.cube.Cube`): Variable to plot.
        resolution (:obj:`float`, optional): What lat:lon resolution (in degrees) to interpolate pe.data to before plotting. Defaults to 0.25.
        cmap (:obj:`matplotlib.colors.LinearSegmentedColormap`): Mapping of pe.data to plot colour. Defaults to green semi-transparent.
        zorder (:obj:`float`, optional): Standard matplotlib parameter determining which things are plotted on top (high zorder), and which underneath (low zorder), Defaults to 4.

    Returns:
        See :meth:`matplotlib.axes.Axes.pcolorfast` - also adds the image to the plot.

    |
    """   
    plot_cube=_make_dummy(ax,resolution)
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
    """Plots a variable as a contour plot.

    This is the same as :meth:`matplotlib.axes.Axes.contour`, except that it takes an :class:`iris.cube.Cube` instead of an array of values, and its defaults are chosen for plots of mean-sea-level pressure.

    Args:
        ax (:obj:`cartopy.mpl.geoaxes.GeoAxes`): Axes on which to draw.
        pe (:obj:`iris.cube.Cube`): Variable to plot.
        resolution (`float`, optional): What lat:lon resolution (in degrees) to interpolate pe.data to before plotting. Defaults to 0.25.
        colors (see :mod:`matplotlib.colors`, optional) contour line colour. Defaults to 'black'.
        linewidths (:obj:`float`, optional): Line width for contour lines. Defaults to 0.5.
        fontsize (:obj:`int`, optional): Font size for contour labels. Defaults to 12.
        zorder (:obj:`float`, optional): Standard matplotlib parameter determining which things are plotted on top (high zorder), and which underneath (low zorder), Defaults to 4.
        label (:obj:`bool`, optional): Label contour lines? Defaults to False.

    Returns:
        See :meth:`matplotlib.axes.Axes.contour` - also adds the lines to the plot.

    |
    """
    plot_cube=_make_dummy(ax,resolution)
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
    """Plots a pair of variables as a 2d field of arrows.

    This is the same as :meth:`matplotlib.axes.Axes.quiver`, except that it takes :class:`iris.cube.Cube` as arguments instead of a set of vectors, and its defaults are chosen for plots of 10m wind.

    *WARNING* This function is under development - in particular the argument names are badly chosen and will need to be changed.

    Args:
        ax (:obj:`cartopy.mpl.geoaxes.GeoAxes`): Axes on which to draw.
        ue (:obj:`iris.cube.Cube`): meridional value of variable to plot.
        ve (:obj:`iris.cube.Cube`): zonal value of  variable to plot.
        resolution (:obj:`float`, optional): What lat:lon resolution (in degrees) to interpolate [uv]e.data to before plotting. Defaults to 1.
        colors (see :mod:`matplotlib.colors`, optional) vector colour. Defaults to (0,0,0,0.25).
        headwidth (:obj:`float`, optional): Controls arraw shape. Defaults to 1.
        random_state (None|:obj:`int`|:obj:`numpy.random.RandomState`): Random number generation seed, see :func:`sklearn.utils.check_random_state`.
        max_points (:obj:`int`, optional): Maximum number of vectors to allocate, defaults to 10,000.
        zorder (:obj:`float`, optional): Standard matplotlib parameter determining which things are plotted on top (high zorder), and which underneath (low zorder), Defaults to 5.

    Returns:
        See :meth:`matplotlib.axes.Axes.quiver` - also adds the vectors to the plot.

    |
    """

    pole_latitude=ax.projection.proj4_params['o_lat_p']
    pole_longitude=ax.projection.proj4_params['lon_0']-180
    projection_iris=iris.coord_systems.RotatedGeogCS(pole_latitude,
                                                     pole_longitude)
    rw=iris.analysis.cartography.rotate_winds(ue,ve,projection_iris)
    plot_cube=_make_dummy(ax,resolution)
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
    """Plots a pair of variables as a 2d field of arrows, coloured according to a third variable.

    This is the same as :meth:`matplotlib.axes.Axes.quiver`, except that it takes :class:`iris.cube.Cube` as arguments instead of a set of vectors, and its defaults are chosen for plots of 10m wind.

    *WARNING* This function does not yet work - don't use it..

    Args:
        ax (:obj:`cartopy.mpl.geoaxes.GeoAxes`): Axes on which to draw.
        ue (:obj:`iris.cube.Cube`): meridional value of variable to plot.
        ve (:obj:`iris.cube.Cube`): zonal value of  variable to plot.
        t2 (:obj:`iris.cube.Cube`): variable to use to select arrow colour.
        resolution (:obj:`float`, optional): What lat:lon resolution (in degrees) to interpolate [uv]e.data to before plotting. Defaults to 1.
        colors (see :mod:`matplotlib.colors`, optional) vector colour. Defaults to (0,0,0,0.25).
        headwidth (:obj:`float`, optional): Controls arrow shape. Defaults to 1.
        random_state (None|:obj:`int`|:obj:`numpy.random.RandomState`): Random number generation seed, see :func:`sklearn.utils.check_random_state`.
        max_points (:obj:`int`, optional): Maximum number of vectors to allocate, defaults to 10,000.
        zorder (:obj:`float`, optional): Standard matplotlib parameter determining which things are plotted on top (high zorder), and which underneath (low zorder), Defaults to 5.

    Returns:
        See :meth:`matplotlib.axes.Axes.quiver` - also adds the vectors to the plot.

    |
    """
    pole_latitude=ax.projection.proj4_params['o_lat_p']
    pole_longitude=ax.projection.proj4_params['lon_0']-180
    projection_iris=iris.coord_systems.RotatedGeogCS(pole_latitude,
                                                     pole_longitude)
    plot_cube=_make_dummy(ax,resolution)
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

def plot_obs(ax,obs,
             obs_projection=ccrs.PlateCarree(),
             lat_label='Latitude',lon_label='Longitude',
             radius=0.1,
             facecolor='yellow',
             edgecolor='black',
             alpha=0.85,
             zorder=2.5):
    """Plot observations as points.

    Args:
        ax (:obj:`cartopy.mpl.geoaxes.GeoAxes`): Axes on which to draw.
        obs (:obj:`dict`): Dictionary containing obs positions.
        obs_projection (:obj:`cartopy.crs.CRS`, optional): Projection in which observations latitudes and longitudes are defined. Default is :class:`cartopy.crs.PlateCarree`.
        lat_label (:obj:`str`, optional): Key, in the obs dictionary, of the latitude data. Defaults to 'Latitude'.
        lon_label (:obj:`str`, optional): Key, in the obs dictionary, of the longitude data. Defaults to 'Longitude'.
        radius (:obj:`float`, optional): Radius of circle marking each ob. (degrees). Defaults to 1.
        facecolor (see :mod:`matplotlib.colors`, optional): Main colour of the circle to be plotted for each ob. Defaults to 'yellow'.
        edgecolor (see :mod:`matplotlib.colors`, optional): Border colour of the circle to be plotted for each ob. Defaults to 'black'.
        alpha (:obj:`float`, optional): Alpha value for facecolor and edgecolor. Defaults to 0.85.
        zorder (:obj:`float`, optional): Standard matplotlib parameter determining which things are plotted on top (high zorder), and which underneath (low zorder), Defaults to 2.5.

    Returns:
        Nothing - adds the obs. points to the plot.

    |
    """

    rp=ax.projection.transform_points(obs_projection,
                                   obs[lon_label].values,
                                   obs[lat_label].values)
    new_longitude=rp[:,0]
    new_latitude=rp[:,1]

    # Plot each ob as a circle
    for i in range(0,len(new_longitude)):
        ax.add_patch(matplotlib.patches.Circle((new_longitude[i],
                                                new_latitude[i]),
                                                radius=radius,
                                                facecolor=facecolor,
                                                edgecolor=edgecolor,
                                                alpha=alpha,
                                                zorder=zorder))

def plot_label(ax,label,
               color='black',
               facecolor='white',
               x_fraction=0.98,y_fraction=0.02,
               horizontalalignment='right',
               verticalalignment='bottom',
               fontsize=12,
               zorder=5.5):
    """Add a text label to the plot

    Args:
        ax (:obj:`cartopy.mpl.geoaxes.GeoAxes`): Axes on which to draw.
        color (see :mod:`matplotlib.colors`, optional): Text colour of the label. Defaults to 'black'.
        facecolor (see :mod:`matplotlib.colors`, optional): Background colour of the label. Defaults to 'white'.
        x_fraction (:obj:`float`, optional): X position of the label (fraction of axes). Defaults to 0.98.
        y_fraction (:obj:`float`, optional): Y position of the label (fraction of axes). Defaults to 0.02.
        horizontalalignment (:obj:`str`, optional): How is the label justified to the x position (right|left|center)?. Defaults to 'right'.
        verticalalignment (:obj:`str`, optional): How is the label justified to the y position (top|bottom|center)?. Defaults to 'bottom'.
        fontsize (:obj:`int`, optional): Size of the text to use. Defaults to 12.
        zorder (:obj:`float`, optional): Standard matplotlib parameter determining which things are plotted on top (high zorder), and which underneath (low zorder), Defaults to 5.5.

    Returns:
        Nothing - adds the label points to the plot.

    |
    """

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

