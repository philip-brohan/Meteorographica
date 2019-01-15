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

import numpy
import iris
import matplotlib
import matplotlib.colors
import scipy

import Meteorographica.utils as utils

# Plot a single field as a standard contour plot
def plot_contour(ax,pe,**kwargs):
    """Plots a variable as a contour plot.

    This is the same as :meth:`matplotlib.axes.Axes.contour`, except that it takes an :class:`iris.cube.Cube` instead of an array of values, and its defaults are chosen for plots of mean-sea-level pressure.

    Args:
        ax (:obj:`cartopy.mpl.geoaxes.GeoAxes`): Axes on which to draw.
        pe (:obj:`iris.cube.Cube`): Variable to plot - must have dimensions 'latitude' and 'longitude'.

    Keyword Args:
        label (:obj:`bool`): Label contour lines? Defaults to False. If it's 'video' use stablised label locations.
        resolution (:obj:`float`): What lat:lon resolution (in degrees) to interpolate pe.data to before plotting. Defaults to None - use original resolution.
        scale (:obj:`float`): This function is tuned for data in hPa. For data in Pa, set this to 0.01. Defaults to 1.
        colors (see :mod:`matplotlib.colors`) contour line colour. Defaults to 'black'.
        linewidths (:obj:`float`): Line width for contour lines. Defaults to 0.5.
        alpha (:obj:`float`): Colour alpha blend. Defaults to 1 (opaque).
        fontsize (:obj:`int`): Font size for contour labels. Defaults to 12.
        zorder (:obj:`float`): Standard matplotlib parameter determining which things are plotted on top (high zorder), and which underneath (low zorder), Defaults to 30.

    Returns:
        See :meth:`matplotlib.axes.Axes.contour` - also adds the lines to the plot.

    |
    """

    kwargs.setdefault('raw'        ,False)
    kwargs.setdefault('label'      ,True)
    kwargs.setdefault('resolution' ,None)
    kwargs.setdefault('scale'      ,1.0)
    kwargs.setdefault('colors'     ,'black')
    kwargs.setdefault('alpha'      ,1.0)
    kwargs.setdefault('linewidths' ,0.5)
    kwargs.setdefault('fontsize'   ,12)
    kwargs.setdefault('levels'     ,numpy.arange(870,1050,10))
    kwargs.setdefault('zorder'     ,30)

    if kwargs.get('resolution') is None:
        contour_p=pe
    else:
        plot_cube=utils.dummy_cube(ax,kwargs.get('resolution'))
        contour_p = pe.regrid(plot_cube,iris.analysis.Linear())

    contour_p.data=contour_p.data*kwargs.get('scale')
    lats = contour_p.coord('latitude').points
    lons = contour_p.coord('longitude').points
    lons,lats = numpy.meshgrid(lons,lats)
    CS=ax.contour(lons, lats, contour_p.data,
                               colors=kwargs.get('colors'),
                               linewidths=kwargs.get('linewidths'),
                               alpha=kwargs.get('alpha'),
                               levels=kwargs.get('levels'),
                               zorder=kwargs.get('zorder'))

    # Label the contours
    if kwargs.get('label')=='video':
        cl=ax.clabel(CS, inline=1, fontsize=kwargs.get('fontsize'),
                     manual=make_label_hints(ax,CS),
                     fmt='%d',zorder=kwargs.get('zorder'))
    elif kwargs.get('label'):
        cl=ax.clabel(CS, inline=1, fontsize=kwargs.get('fontsize'),
                     fmt='%d',zorder=kwargs.get('zorder'))

    return CS


# Plot a set of fields as a spaghetti plot
def plot_spaghetti_contour(ax,pe,**kwargs):
    """Plots a multi-contour (spaghetti) plot.

    Calls :meth:`plot_pressure_contour` multiple times with sensible defaults colurs and styles

    Args:
        ax (:obj:`cartopy.mpl.geoaxes.GeoAxes`): Axes on which to draw.
        pe (:obj:`iris.cube.Cube`): Variable to plot.- must have dimensions <ensemble_dimension>, 'latitude' and 'longitude'.

    Keyword Args:
        ensemble_dimension (:obj:`float`): name of the ensemble dimension. Defaults to 'member'.
        colors (see :mod:`matplotlib.colors`) contour line colour. Defaults to 'blue'.
        linewidths (:obj:`float`): Line width for contour lines. Defaults to 0.2.
        label (:obj:`bool`): Label contour lines? Defaults to False.
        Other keyword arguments are passed to :meth:`plot_pressure_contour`

    Returns:
        See :meth:`matplotlib.axes.Axes.contour` - except it's an array, one for each member. Also adds the lines to the plot.

    |
    """  

    kwargs.setdefault('ensemble_dimension','member')
    kwargs.setdefault('colors'            ,'blue')
    kwargs.setdefault('linewidths'        ,0.1)
    kwargs.setdefault('label'             ,False)

    CS=[]
    for m in pe.coord(kwargs.get('ensemble_dimension')).points:
        pe_e=pe.extract(iris.Constraint(member=m))
        CS.append(plot_contour(ax,pe_e,**kwargs))

    return CS

mean_contour_cmap= matplotlib.colors.LinearSegmentedColormap('mc_cmap',
                      {'red'   : ((0.0, 0.0, 0.0), 
                                  (1.0, 0.0, 0.0)), 
                       'green' : ((0.0, 0.3, 0.3), 
                                  (1.0, 0.3, 0.3)), 
                       'blue'  : ((0.0, 0.0, 0.0), 
                                  (1.0, 0.0, 0.0)), 
                       'alpha' : ((0.0, 0.0, 0.0),
                                  (1.0, 0.75, 0.75))}) 

# Plot ensemble mean contours, using transparency as an uncertainty indicator
def plot_mean_spread(ax,pe,**kwargs):
    """Plots a variable as a contour plot.

    Plots contours of the mean of an ensemble, mark uncertainty by fading out the contours where the ensemble spread is large.

    Args:
        ax (:obj:`cartopy.mpl.geoaxes.GeoAxes`): Axes on which to draw.
        pe (:obj:`iris.cube.Cube`): Variable to plot.- must have dimensions <ensemble_dimension>, 'latitude' and 'longitude'.

    Keyword Args:
        ensemble_dimension (:obj:`float`): name of the ensemble dimension. Defaults to 'member'.
        resolution (:obj:`float`): What lat:lon resolution (in degrees) to interpolate pe.data to before plotting. Defaults to None - use original resolution.
        colors (see :mod:`matplotlib.colors`) contour line colour. Defaults to 'black'.
        linewidths (:obj:`float`): Line width for contour lines. Defaults to 0.2.
        label (:obj:`bool`): Label contour lines? Defaults to False.
        cmap (:obj:`matplotlib.colors.LinearSegmentedColormap`): Mapping of pe.data to plot colour. Defaults to blackblack semi-transparent.
        threshold (:obj:`float`): Ranges shown are regions where the probability that a contour line passes through the region is greater than this. Defaults to 0.05 (5%).
        vmax (:obj:`float`): Show as 'most likely', regions where the prob of a contour is greater than this Defaults to 0.4 (40%).
        line_threshold (:obj:`float`): Only draw contours where the local standard deviation is less than this. Defaults to None - draw contours everywhere.
        alpha (:obj:`float`): Colour alpha blend. Defaults to 1 (opaque).
        fontsize (:obj:`int`): Font size for contour labels. Defaults to 12.
        zorder (:obj:`float`): Standard matplotlib parameter determining which things are plotted on top (high zorder), and which underneath (low zorder), Defaults to 40.
        label (:obj:`bool`): Label contour lines? Defaults to True.

    Returns:
        See :meth:`matplotlib.axes.Axes.contour` - also adds the lines to the plot.

    |
    """

    kwargs.setdefault('label'             ,True)
    kwargs.setdefault('ensemble_dimension','member')
    kwargs.setdefault('resolution'        ,None)
    kwargs.setdefault('scale'             ,1.0)
    kwargs.setdefault('cmap'              ,mean_contour_cmap)
    kwargs.setdefault('colors'            ,'black')
    kwargs.setdefault('alpha'             ,1.0)
    kwargs.setdefault('linewidths'        ,0.5)
    kwargs.setdefault('fontsize'          ,12)
    kwargs.setdefault('levels'            ,numpy.arange(870,1050,10))
    kwargs.setdefault('threshold'         ,0.05)
    kwargs.setdefault('vmax'              ,0.4)
    kwargs.setdefault('line_threshold'    ,None)
    kwargs.setdefault('zorder'            ,40)

    pe.data=pe.data*kwargs.get('scale')
    pe_m=pe.collapsed(kwargs.get('ensemble_dimension'), iris.analysis.MEAN)
    pe_s=pe.collapsed(kwargs.get('ensemble_dimension'), iris.analysis.STD_DEV)

    if kwargs.get('resolution') is not None:
        plot_cube=utils.dummy_cube(ax,kwargs.get('resolution'))
        pe_m=pe_m.regrid(plot_cube,iris.analysis.Linear())
        pe_s=pe_s.regrid(plot_cube,iris.analysis.Linear())

    # Estimate, at each point, the probability that a contour goes through it.
    pe_u = pe_m.copy()
    pe_u.data=pe_m.data*0.0
    pe_t = pe_u.copy()
    for level in kwargs.get('levels'):
        pe_t.data=1-scipy.stats.norm.cdf(numpy.absolute(pe_m.data-level)/pe_s.data)
        pe_u.data=numpy.maximum(pe_u.data,pe_t.data)
    # Plot this probability as a colormap
    lats = pe_u.coord('latitude').points
    lons = pe_u.coord('longitude').points
    u_img=ax.pcolorfast(lons, lats, pe_u.data, 
                         cmap=kwargs.get('cmap'),
                         vmin=kwargs.get('threshold')/2.0-0.01,
                         vmax=kwargs.get('vmax'),
                         zorder=kwargs.get('zorder')-1)

    # Generate the mean contour lines, but don't draw them (linewidth=0)
    CS=ax.contour(lons, lats, pe_m.data,
                               colors=kwargs.get('colors'),
                               linewidths=0,
                               alpha=kwargs.get('alpha'),
                               levels=kwargs.get('levels'),
                               zorder=kwargs.get('zorder'))

    # Label the mean contours - transparency dependent on spread
    interpolator = iris.analysis.Linear().interpolator(pe_s, 
                                   ['latitude', 'longitude'])
    if kwargs.get('label'):
        cl=ax.clabel(CS, inline=1, 
                     fontsize=kwargs.get('fontsize'),
                     fmt='%d',
                     zorder=kwargs.get('zorder')+1)
        if kwargs.get('line_threshold') is not None:
            for label in cl:
                pos=label.get_position()
                local_spread=interpolator([pos[1],pos[0]]).data
                alpha_s=numpy.sqrt(max(0.04,1-local_spread/
                                              kwargs.get('line_threshold')))
                label.set_alpha(kwargs.get('alpha')*alpha_s)

    # Draw the mean contours, with transparency dependent on spread
    base_col=matplotlib.colors.colorConverter.to_rgb(kwargs.get('colors'))
    for collection in CS.collections: 
        segments=collection.get_segments()
        for segment in segments:  
            for idx in range(segment.shape[0]-1):
                alpha_s=1
                if kwargs.get('line_threshold') is not None:
                    local_spread=interpolator(
                          [(segment[idx,1]+segment[idx+1,1])/2.0,
                           (segment[idx,0]+segment[idx+1,0])/2.0]).data
                    alpha_s=numpy.sqrt(max(0.04,1-local_spread/
                                                  kwargs.get('line_threshold')))
                clr=(base_col[0],
                     base_col[1],
                     base_col[2],kwargs.get('alpha')*alpha_s)
                ax.add_line(matplotlib.lines.Line2D(
                                xdata=segment[idx:(idx+2),0],
                                ydata=segment[idx:(idx+2),1],
                                linestyle='solid',
                                linewidth=kwargs.get('linewidths'),
                                color=clr,
                                zorder=kwargs.get('zorder')))      

    return CS
    
# Plot pressure
def plot(ax,pe,**kwargs):
    """Plot pressure.

    Generic function for plotting pressure. Use the 'type' argument to choose the plot style.

    Args:
        ax (:obj:`cartopy.mpl.geoaxes.GeoAxes`): Axes on which to draw.
        pe (:obj:`iris.cube.Cube`): Variable to plot - must have dimensions 'latitude' and 'longitude'.


    Keyword Args:
        type (:obj:`str`): Style to plot. Options are:'contour' (default), which delegates plotting to :meth:`plot_contour`, 'spaghetti',  which delegates plotting to :meth:`plot_spaghetti_contour`, 'spread', which delegates plotting to :meth:`plot_mean_spread`.

    Other keyword arguments are passed to the style-specific plotting function.

    Returns:
        See :meth:`matplotlib.axes.Axes.contour` - Also adds the lines to the plot.

    |
    """  

    kwargs.setdefault('type','contour')

    if kwargs.get('type')=='contour':
        return plot_contour(ax,pe,**kwargs)
    if kwargs.get('type')=='spaghetti':
        return plot_spaghetti_contour(ax,pe,**kwargs)
    if kwargs.get('type')=='spread':
        return plot_mean_spread(ax,pe,**kwargs)

    raise Exception('Unsupported pressure plot type %s' %
                         kwargs.get('type'))


def make_label_hints(ax,CS):
    """Make hints for the contour label placement algorithm - these stabilise the positions of the contour labels between frames in videos. They don't eliminate the problem of jittery and flickering contour labels, but they do help.

    Args:
        ax (:obj:`cartopy.mpl.geoaxes.GeoAxes`): Axes on which to draw.
        CS (:obj:`matplotlib.contour.ContourSet`): Contours to be labeled.

    Returns:
        iterable of (x,y) tuples - each a position hint for a label.

    |
    """

    label_locations=[]
    buffer=(ax.get_extent()[1]-ax.get_extent()[0])/20.0
    for collection in CS.collections: 
        segments=collection.get_segments()
        for segment in segments:
            left_edge=None
            right_edge=None
            bottom_edge=None
            top_edge=None
            bottom_point=None
          # Find a suitable spot to label the segment
            for si in range(len(segment)):
                if (left_edge is None) and (si>0):
                    if ((segment[si][0]>=(ax.get_extent()[0]+buffer)) and
                        (segment[si-1][0]<(ax.get_extent()[0]+buffer))):
                        weight=((segment[si][0]-(ax.get_extent()[0]+buffer))/
                                            (segment[si][0]-segment[si-1][0]))
                        left_edge=(ax.get_extent()[0]+buffer,
                                   segment[si][1]+
                                  (segment[si][1]-segment[si-1][1])*weight)
                if (left_edge is None) and (si<(len(segment)-1)):
                    if ((segment[si][0]>=(ax.get_extent()[0]+buffer)) and
                        (segment[si+1][0]<(ax.get_extent()[0]+buffer))):
                        weight=((segment[si][0]-(ax.get_extent()[0]+buffer))/
                                            (segment[si][0]-segment[si+1][0]))
                        left_edge=(ax.get_extent()[0]+buffer,
                                   segment[si][1]+
                                  (segment[si][1]-segment[si+1][1])*weight)
                if (right_edge is None) and (si>0):
                    if ((segment[si][0]>=(ax.get_extent()[1]-buffer)) and
                        (segment[si-1][0]<(ax.get_extent()[1]-buffer))):
                        weight=((segment[si][0]-(ax.get_extent()[1]-buffer))/
                                            (segment[si][0]-segment[si-1][0]))
                        right_edge=(ax.get_extent()[1]-buffer,
                                   segment[si][1]+
                                  (segment[si][1]-segment[si-1][1])*weight)
                if (right_edge is None) and (si<(len(segment)-1)):
                    if ((segment[si][0]>=(ax.get_extent()[1]-buffer)) and
                        (segment[si+1][0]<(ax.get_extent()[1]-buffer))):
                        weight=((segment[si][0]-(ax.get_extent()[1]-buffer))/
                                            (segment[si][0]-segment[si+1][0]))
                        right_edge=(ax.get_extent()[1]-buffer,
                                   segment[si][1]+
                                  (segment[si][1]-segment[si+1][1])*weight)
                if (bottom_edge is None) and (si>0):
                    if ((segment[si][1]>=(ax.get_extent()[2]+buffer)) and
                        (segment[si-1][1]<(ax.get_extent()[2]+buffer))):
                        weight=((segment[si][1]-(ax.get_extent()[2]+buffer))/
                                            (segment[si][1]-segment[si-1][1]))
                        bottom_edge=(segment[si][0]+
                                     (segment[si][0]-segment[si-1][0])*weight,
                                     ax.get_extent()[2]+buffer)
                if (bottom_edge is None) and (si<(len(segment)-1)):
                    if ((segment[si][1]>=(ax.get_extent()[2]+buffer)) and
                        (segment[si+1][1]<(ax.get_extent()[2]+buffer))):
                        weight=((segment[si][1]-(ax.get_extent()[2]+buffer))/
                                            (segment[si][1]-segment[si+1][1]))
                        bottom_edge=(segment[si][0]+
                                     (segment[si][0]-segment[si+1][0])*weight,
                                     ax.get_extent()[2]+buffer)
                if (top_edge is None) and (si>0):
                    if ((segment[si][1]>=(ax.get_extent()[3]-buffer)) and
                        (segment[si-1][1]<(ax.get_extent()[3]-buffer))):
                        weight=((segment[si][1]-(ax.get_extent()[3]-buffer))/
                                            (segment[si][1]-segment[si-1][1]))
                        top_edge=(segment[si][0]+
                                     (segment[si][0]-segment[si-1][0])*weight,
                                     ax.get_extent()[3]-buffer)
                if (top_edge is None) and (si<(len(segment)-1)):
                    if ((segment[si][1]>=(ax.get_extent()[3]-buffer)) and
                        (segment[si+1][1]<(ax.get_extent()[3]-buffer))):
                        weight=((segment[si][1]-(ax.get_extent()[3]-buffer))/
                                            (segment[si][1]-segment[si+1][1]))
                        top_edge=(segment[si][0]+
                                     (segment[si][0]-segment[si+1][0])*weight,
                                     ax.get_extent()[3]-buffer)
                if bottom_point is None or segment[si][1]<bottom_point[1]:
                        bottom_point=(segment[si][0],segment[si][1])
            if left_edge is not None:
                label_locations.append(left_edge)
            if right_edge is not None:
                label_locations.append(right_edge)
            if left_edge is None and right_edge is None:
                if bottom_edge is not None:
                    label_locations.append(bottom_edge)
                if top_edge is not None:
                    label_locations.append(top_edge)
                if bottom_edge is None and top_edge is None:
                    label_locations.append(bottom_point)

    return label_locations
