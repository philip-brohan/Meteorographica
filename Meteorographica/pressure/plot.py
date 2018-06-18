import numpy
import iris
import matplotlib
import matplotlib.colors
import scipy

# Plot a single field as a standard contour plot
def plot_pressure_contour(ax,pe,**kwargs):
    """Plots a variable as a contour plot.

    This is the same as :meth:`matplotlib.axes.Axes.contour`, except that it takes an :class:`iris.cube.Cube` instead of an array of values, and its defaults are chosen for plots of mean-sea-level pressure.

    Args:
        ax (:obj:`cartopy.mpl.geoaxes.GeoAxes`): Axes on which to draw.
        pe (:obj:`iris.cube.Cube`): Variable to plot - must have dimensions 'latitude' and 'longitude'.

    Kwargs:
        raw (:obj:`bool`): If True, plot the colourmap on the native data resolution. If False (default), regrid the data to the given resolution before plotting.
        label (:obj:`bool`, optional): Label contour lines? Defaults to False.
        resolution (:obj:`float`, optional): What lat:lon resolution (in degrees) to interpolate pe.data to before plotting. Defaults to 0.25.
        scale (:obj:`float`, optional): This function is tuned for data in hPa. For data in Pa, set this to 0.01. Defaults to 1.
        colors (see :mod:`matplotlib.colors`, optional) contour line colour. Defaults to 'black'.
        linewidths (:obj:`float`, optional): Line width for contour lines. Defaults to 0.5.
        alpha (:obj:`float`, optional): Colour alpha blend. Defaults to 1 (opaque).
        fontsize (:obj:`int`, optional): Font size for contour labels. Defaults to 12.
        zorder (:obj:`float`, optional): Standard matplotlib parameter determining which things are plotted on top (high zorder), and which underneath (low zorder), Defaults to 30.

    Returns:
        See :meth:`matplotlib.axes.Axes.contour` - also adds the lines to the plot.

    |
    """

    kwargs.setdefault('raw'        ,False)
    kwargs.setdefault('label'      ,True)
    kwargs.setdefault('resolution' ,0.25)
    kwargs.setdefault('scale'      ,1.0)
    kwargs.setdefault('colors'     ,'black')
    kwargs.setdefault('alpha'      ,1.0)
    kwargs.setdefault('linewidths' ,0.5)
    kwargs.setdefault('fontsize'   ,12)
    kwargs.setdefault('levels'     ,numpy.arange(870,1050,10))
    kwargs.setdefault('zorder'     ,30)

    if kwargs.get('raw'):
        contour_p=pe
    else:
        plot_cube=_make_dummy(ax,resolution)
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
    if kwargs.get('label'):
        cl=ax.clabel(CS, inline=1, fontsize=kwargs.get('fontsize'),
                     fmt='%d',zorder=kwargs.get('zorder'))

    return CS


# Plot a set of fields as a spaghetti plot
def plot_pressure_spaghetti_contour(ax,pe,**kwargs):
    """Plots a multi-contour (spaghetti) plot.

    Calls :meth:`plot_pressure_contour` multiple times with sensible defaults colurs and styles

    Args:
        ax (:obj:`cartopy.mpl.geoaxes.GeoAxes`): Axes on which to draw.
        pe (:obj:`iris.cube.Cube`): Variable to plot.- must have dimensions <ensemble_dimension>, 'latitude' and 'longitude'.

    Kwargs:
        ensemble_dimension (:obj:`float`, optional): name of the ensemble dimension. Defaults to 'member'.
        colors (see :mod:`matplotlib.colors`, optional) contour line colour. Defaults to 'blue'.
        linewidths (:obj:`float`, optional): Line width for contour lines. Defaults to 0.2.
        label (:obj:`bool`, optional): Label contour lines? Defaults to False.
        Other keyword arguments are passed to :meth:`plot_pressure_contour`

    Returns:
        See :meth:`matplotlib.axes.Axes.contour` - except it's an array, one for each member. Also adds the lines to the plot.
    |
    """  

    kwargs.setdefault('ensemble_dimension','member')
    kwargs.setdefault('colors'            ,'blue')
    kwargs.setdefault('linewidths'        ,0.2)
    kwargs.setdefault('label'             ,'False')

    CS=[]
    for m in prmsl.coord(kwargs.get('ensemble_dimension')).points:
        prmsl_e=prmsl.extract(iris.Constraint(member=m))
        CS.append(plot_pressure_contour(ax,prmsl_e,**kwargs))

    return CS

mean_contour_cmap= matplotlib.colors.LinearSegmentedColormap('mc_cmap',
                      {'red'   : ((0.0, 0.0, 0.0), 
                                  (1.0, 0.0, 0.0)), 
                       'green' : ((0.0, 0.8, 0.8), 
                                  (1.0, 0.8, 0.8)), 
                       'blue'  : ((0.0, 0.0, 0.0), 
                                  (1.0, 0.0, 0.0)), 
                       'alpha' : ((0.0, 0.0, 0.0),
                                  (1.0, 0.25, 0.25))}) 

# Plot ensemble mean contours, using transparency as an uncertainty indicator
def plot_pressure_mean_spread(ax,pe,**kwargs):
    """Plots a variable as a contour plot.

    Plots contours of the mean of an ensemble, mark uncertainty by fading out the contours where the ensemble spread is large.

    Args:
        ax (:obj:`cartopy.mpl.geoaxes.GeoAxes`): Axes on which to draw.
        pe (:obj:`iris.cube.Cube`): Variable to plot.- must have dimensions <ensemble_dimension>, 'latitude' and 'longitude'.

    Kwargs:
        ensemble_dimension (:obj:`float`, optional): name of the ensemble dimension. Defaults to 'member'.
        colors (see :mod:`matplotlib.colors`, optional) contour line colour. Defaults to 'black'.
        linewidths (:obj:`float`, optional): Line width for contour lines. Defaults to 0.2.
        label (:obj:`bool`, optional): Label contour lines? Defaults to False.
        cmap (:obj:`matplotlib.colors.LinearSegmentedColormap`): Mapping of pe.data to plot colour. Defaults to blackblack semi-transparent.
        threshold (:obj:`float`, optional): Ranges shown are regions where the probability that a contour line passes through the region is greater than this. Defaults to 0.05 (5%).
        vmax (:obj:`float`, optional): Show as 'most likely', regions where the prob of a contour is greater than this Defaults to 0.4 (40%).
        line_threshold (:obj:`float`, optional): Only draw contours where the local standard deviation is less than this. Defaults to None - draw contours everywhere.
        alpha (:obj:`float`, optional): Colour alpha blend. Defaults to 1 (opaque).
        fontsize (:obj:`int`, optional): Font size for contour labels. Defaults to 12.
        zorder (:obj:`float`, optional): Standard matplotlib parameter determining which things are plotted on top (high zorder), and which underneath (low zorder), Defaults to 4.
        label (:obj:`bool`, optional): Label contour lines? Defaults to True.

    Returns:
        See :meth:`matplotlib.axes.Axes.contour` - also adds the lines to the plot.

    |
    """

    kwargs.setdefault('raw'               ,False)
    kwargs.setdefault('label'             ,True)
    kwargs.setdefault('ensemble_dimension','member')
    kwargs.setdefault('resolution'        ,0.25)
    kwargs.setdefault('scale'             ,1.0)
    kwargs.setdefault('cmap'              ,mc_cmap)
    kwargs.setdefault('colors'            ,'black')
    kwargs.setdefault('alpha'             ,1.0)
    kwargs.setdefault('linewidths'        ,0.5)
    kwargs.setdefault('fontsize'          ,12)
    kwargs.setdefault('levels'            ,numpy.arange(870,1050,10))
    kwargs.setdefault('threshold'         ,0.05)
    kwargs.setdefault('vmax'              ,0.4)
    kwargs.setdefault('line_threshold'    ,None)

    pe_m=pe.collapsed(kwargs.get('ensemble_dimension'), iris.analysis.MEAN)
    pe_s=pe.collapsed(kwargs.get('ensemble_dimension'), iris.analysis.STD_DEV)

    if not kwargs.get('raw'):
        plot_cube=_make_dummy(ax,kwargs.get('resolution'))
        pe_m=pe_m.regrid(plot_cube,iris.analysis.Linear())
        pe_s=pe_s.regrid(plot_cube,iris.analysis.Linear())

    # Estimate, at each point, the probability that a contour goes through it.
    pe_u = pe_m.copy()
    pe_u.data=pe_m.data*0.0
    pe_t = pe_u.copy()
    for level in levels:
        pe_t.data=1-scipy.stats.norm.cdf(numpy.absolute(pe_m.data-level)/pe_s.data)
        pe_u.data=numpy.maximum(pe_u.data,pe_t.data)
    # Plot this probability as a colormap
    lats = prmsl_u.coord('latitude').points
    lons = prmsl_u.coord('longitude').points
    u_img=ax.pcolorfast(lons, lats, prmsl_u.data, 
                         cmap=kwargs.get('cmap'),
                         vmin=kwargs.get('threshold')/2.0-0.01,
                         vmax=kwargs.get('vmax'),
                         zorder=kwargs.get(zorder)-1)

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
    if label:
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
def plot_pressure(ax,pe,**kwargs):
    """Plot pressure.

    Generic function for plotting pressure. Use the 'type' argument to choose the plot style.

    Args:
        ax (:obj:`cartopy.mpl.geoaxes.GeoAxes`): Axes on which to draw.
        pe (:obj:`iris.cube.Cube`): Variable to plot - must have dimensions 'latitude' and 'longitude'.


    Kwargs:
        type (:obj:`str`, optional): Style to plot. Default is 'cmap', which delegates plotting to :meth:`plot_precip_cmesh` and at the moment this is the only choice. 
        Other keyword arguments are passed to the style-specific plotting function.

    Returns:
        See :meth:`matplotlib.axes.Axes.contour` - Also adds the lines to the plot.
    |
    """  

    kwargs.setdefault('type','cmesh')

    if kwargs.get('type')=='cmesh':
        return plot_precip_cmesh(ax,pe,**kwargs)

    raise StandardError('Unsupported precipitation plot type %s' %
                         kwargs.get('type'))




