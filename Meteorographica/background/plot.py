import matplotlib
import numpy

# Add a lat lon grid to an axes
def add_grid(ax,**kwargs):
    """Add a lat-lon grid to the map.

    Actually plots two grids, a minor grid at a narrow spacing with thin lines, and a major grid at a wider spacing with thicker lines. Note that the grids only cover the latitude range -85 to 85, because the line spacings become too small very close to the poles on a rotated grid.

    Args:
        ax (:obj:`cartopy.mpl.geoaxes.GeoAxes`): Axes on which to draw.

    Kwargs:
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

    kwargs.setdefault('linestyle'      ,'-')
    kwargs.setdefault('linewidth_minor',0.2)
    kwargs.setdefault('linewidth_major',0.5)
    kwargs.setdefault('color'          ,(0,0.30,0,0.3))
    kwargs.setdefault('sep_minor'      ,0.5)
    kwargs.setdefault('sep_major'      ,2.0)
    kwargs.setdefault('zorder'         ,5)

    gl_minor=ax.gridlines(linestyle=kwargs.get('linestyle'),
                          linewidth=kwargs.get('linewidth_minor'),
                          color=kwargs.get('color'),
                          zorder=kwargs.get('zorder'))
    gl_minor.xlocator = matplotlib.ticker.FixedLocator(
                       numpy.arange(-180,180+kwargs.get('sep_minor'),
                                             kwargs.get('sep_minor')))
    gl_minor.ylocator = matplotlib.ticker.FixedLocator(
                         numpy.arange(-85,85+kwargs.get('sep_minor'),
                                             kwargs.get('sep_minor')))
    gl_major=ax.gridlines(linestyle=kwargs.get('linestyle'),
                          linewidth=kwargs.get('linewidth_major'),
                          color=kwargs.get('color'),
                          zorder=kwargs.get('zorder'))
    gl_major.xlocator = matplotlib.ticker.FixedLocator(
                       numpy.arange(-180,180+kwargs.get('sep_major'),
                                             kwargs.get('sep_major')))
    gl_major.ylocator = matplotlib.ticker.FixedLocator(
                         numpy.arange(-85,85+kwargs.get('sep_major'),
                                             kwargs.get('sep_major')))
