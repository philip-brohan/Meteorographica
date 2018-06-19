import cartopy
import cartopy.crs as ccrs
import matplotlib

def plot_patches(ax,obs,**kwargs):
    """Plot observations as points.

    Args:
        ax (:obj:`cartopy.mpl.geoaxes.GeoAxes`): Axes on which to draw.
        obs (:obj:`dict`): Dictionary containing obs positions.

    Kwargs:
        obs_projection (:obj:`cartopy.crs.CRS`, optional): Projection in which observations latitudes and longitudes are defined. Default is :class:`cartopy.crs.PlateCarree`.
        lat_label (:obj:`str`, optional): Key, in the obs dictionary, of the latitude data. Defaults to 'Latitude'.
        lon_label (:obj:`str`, optional): Key, in the obs dictionary, of the longitude data. Defaults to 'Longitude'.
        radius (:obj:`float`, optional): Radius of circle marking each ob. (degrees). Defaults to 1.
        facecolor (see :mod:`matplotlib.colors`, optional): Main colour of the circle to be plotted for each ob. Defaults to 'yellow'.
        edgecolor (see :mod:`matplotlib.colors`, optional): Border colour of the circle to be plotted for each ob. Defaults to 'black'.
        alpha (:obj:`float`, optional): Alpha value for facecolor and edgecolor. Defaults to 0.85. Will be multiplied by the observation weight if present.
        zorder (:obj:`float`, optional): Standard matplotlib parameter determining which things are plotted on top (high zorder), and which underneath (low zorder), Defaults to 25.

    Returns:
        Nothing - adds the obs. points to the plot.

    |
    """

    kwargs.setdefault('obs_projection',ccrs.PlateCarree())
    kwargs.setdefault('lat_label'     ,        'Latitude')
    kwargs.setdefault('lon_label'     ,       'Longitude')
    kwargs.setdefault('radius'        ,                 1)
    kwargs.setdefault('facecolor'     ,          'yellow')
    kwargs.setdefault('edgecolor'     ,           'black')
    kwargs.setdefault('alpha'         ,              0.85)
    kwargs.setdefault('zorder'        ,                25)

    rp=ax.projection.transform_points(kwargs.get('obs_projection'),
                                   obs[kwargs.get('lon_label')].values,
                                   obs[kwargs.get('lat_label')].values)
    new_longitude=rp[:,0]
    new_latitude=rp[:,1]

    # Plot each ob as a circle
    for i in range(0,len(new_longitude)):
        weight=1.0
        if 'weight' in obs.columns: weight=obs['weight'].values[i]
        ax.add_patch(matplotlib.patches.Circle((new_longitude[i],
                                                new_latitude[i]),
                                                radius=kwargs.get('radius'),
                                                facecolor=kwargs.get('facecolor'),
                                                edgecolor=kwargs.get('edgecolor'),
                                                alpha=kwargs.get('alpha')*weight,
                                                zorder=kwargs.get('zorder')))

    
# Plot observations
def plot(ax,obs,**kwargs):
    """Plot observations.

    Generic function for plotting observations. Use the 'type' argument to choose the plot style.

    Args:
        ax (:obj:`cartopy.mpl.geoaxes.GeoAxes`): Axes on which to draw.
        obs (:obj:`dict`): Dictionary containing obs positions.


    Kwargs:
        type (:obj:`str`, optional): Style to plot. Options are: 
            * 'patches', (default) which delegates plotting to :meth:`plot_patches`,
        Other keyword arguments are passed to the style-specific plotting function.

    Returns:
        Nothing - adds the obs. points to the plot.
    |
    """  

    kwargs.setdefault('type','patches')

    if kwargs.get('type')=='patches':
        return plot_patches(ax,obs,**kwargs)

    raise StandardError('Unsupported observations plot type %s' %
                         kwargs.get('type'))
