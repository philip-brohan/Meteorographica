import numpy
import iris
import matplotlib
import matplotlib.colors

# Define a colour map appropriate for precip plots
# Dark green with varying transparency
precip_cmap = matplotlib.colors.LinearSegmentedColormap('p_cmap',
                             {'red'  : ((0.0, 0.0, 0.0), 
                                        (1.0, 0.0, 0.0)), 
                              'green': ((0.0, 0.3, 0.3), 
                                        (1.0, 0.3, 0.3)), 
                              'blue' : ((0.0, 0.0, 0.0), 
                                        (1.0, 0.0, 0.0)), 
                              'alpha': ((0.0, 0.0, 0.0),
                                        (0.2, 0.0, 0.0),
                                        (1.0, 0.95, 0.95)) })

# Plot precip as a colour map
def plot_precip_cmesh(ax,pe,**kwargs):
    """Plots a variable as a colour map.

    This is the same as :meth:`matplotlib.axes.Axes.pcolorfast`, except that it takes an :class:`iris.cube.Cube` instead of an array of colour values, and its colour defaults are chosen for plots of precipitation rate.

    Args:
        ax (:obj:`cartopy.mpl.geoaxes.GeoAxes`): Axes on which to draw.
        pe (:obj:`iris.cube.Cube`): Variable to plot - must be 2d, with dimensions latitude and longitude.

    Kwargs:
        raw (:obj:`bool`): If True, plot the colourmap on the native data resolution. If False (default), regrid the data to the given resolution before plotting.
        resolution (:obj:`float`, optional): What lat:lon resolution (in degrees) to interpolate pe.data to before plotting. Defaults to 0.25.
        scale (:obj:`float`, optional): This function is tuned for 20CR precip data - rates in Kg*m-2*s-1. For accumulated precip it will be necessary to scale it to an equivalent range. For CERA-20C, try 10. For ERA5, try 10 for enda and 3.6 for oper. Defaults to 1.
        sqrt (:obj:`bool`): Heavy precip (tropical) is so much bigger than light precip that it helps a lot to flatten the distribution before plotting. Apply a square-root filter to the data before plotting? Defaults to True.
        cmap (:obj:`matplotlib.colors.LinearSegmentedColormap`): Mapping of pe.data to plot colour. Defaults to green semi-transparent.
        vmin (:obj:`float): Data value that is shown as 'no precip' (after scaling and filtering). Increase this to show low-previp as zero instead. Defaults to 0.
        vmax (:obj:`float): Data value that is shown as 'heavy precip - darkest colour' (after scaling and filtering). Defaults to 0.025 Kg*m-2*s-1.
        zorder (:obj:`float`, optional): Standard matplotlib parameter determining which things are plotted on top (high zorder), and which underneath (low zorder), Defaults to 40.

    Returns:
        See :meth:`matplotlib.axes.Axes.pcolorfast` - also adds the image to the plot.

    |
    """  

    # Set keyword argument defaults
    kwargs.setdefault('raw'       ,False)
    kwargs.setdefault('resolution',0.25)
    kwargs.setdefault('scale'     ,1.0)
    kwargs.setdefault('sqrt'      ,True)
    kwargs.setdefault('cmap'      ,precip_cmap)
    kwargs.setdefault('vmin'      ,0.0)
    kwargs.setdefault('vmax'      ,0.025)
    kwargs.setdefault('zorder'    ,40)
 
    if kwargs.get('raw'):
        cmesh_p=pe
    else:
        plot_cube=_make_dummy(ax,resolution)
        cmesh_p = pe.regrid(plot_cube,iris.analysis.Linear())

    cmesh_p.data=cmesh_p.data*kwargs.get('scale')
    if kwargs.get('sqrt'):
        cmesh_p.data=numpy.sqrt(cmesh_p.data)

    lats = cmesh_p.coord('latitude').points
    lons = cmesh_p.coord('longitude').points
    prate_img=ax.pcolorfast(lons, lats, cmesh_p.data, 
                            cmap=kwargs.get('cmap'),
                            vmin=kwargs.get('vmin'),
                            vmax=kwargs.get('vmax'),
                            zorder=kwargs.get('zorder'))
    return prate_img




# Plot precip 
def plot_precip(ax,pe,**kwargs):
    """Plot precipitation.

    Generic function for plotting precipitation. Use the 'type' argument to choose the plot style.

    Args:
        ax (:obj:`cartopy.mpl.geoaxes.GeoAxes`): Axes on which to draw.
        pe (:obj:`iris.cube.Cube`): Variable to plot - must be 2d, with dimensions latitude and longitude.


    Kwargs:
        type (:obj:`str`, optional): Style to plot. Default is 'cmap', which delegates plotting to :meth:`plot_precip_cmesh` and at the moment this is the only choice. 
        Other keyword arguments are passed to the style-specific plotting function.

    |
    """  

    kwargs.setdefault('type','cmesh')

    if kwargs.get('type')=='cmesh':
        return plot_precip_cmesh(ax,pe,**kwargs)

    raise StandardError('Unsupported precipitation plot type %s' %
                         kwargs.get('type'))




