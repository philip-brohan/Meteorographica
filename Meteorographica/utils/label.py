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


def plot_label(ax,label,**kwargs):
    """Add a text label to the plot

    Args:
        ax (:obj:`cartopy.mpl.geoaxes.GeoAxes`): Axes on which to draw.
        label (:obj:`str`): Text of label

    Kwargs:
        color (see :mod:`matplotlib.colors`, optional): Text colour of the label. Defaults to 'black'.
        facecolor (see :mod:`matplotlib.colors`, optional): Background colour of the label. Defaults to 'white'.
        x_fraction (:obj:`float`, optional): X position of the label (fraction of axes). Defaults to 0.99.
        y_fraction (:obj:`float`, optional): Y position of the label (fraction of axes). Defaults to 0.02.
        horizontalalignment (:obj:`str`, optional): How is the label justified to the x position (right|left|center)?. Defaults to 'right'.
        verticalalignment (:obj:`str`, optional): How is the label justified to the y position (top|bottom|center)?. Defaults to 'bottom'.
        fontsize (:obj:`int`, optional): Size of the text to use. Defaults to 12.
        zorder (:obj:`float`, optional): Standard matplotlib parameter determining which things are plotted on top (high zorder), and which underneath (low zorder), Defaults to 55.

    Returns:
        Nothing - adds the label points to the plot.

    |
    """

    kwargs.setdefault('color','black')
    kwargs.setdefault('facecolor','white')
    kwargs.setdefault('x_fraction',0.99)
    kwargs.setdefault('y_fraction',0.02)
    kwargs.setdefault('horizontalalignment','right')
    kwargs.setdefault('verticalalignment','bottom')
    kwargs.setdefault('fontsize',12)
    kwargs.setdefault('zorder',55)

    extent=ax.get_extent()
    ax.text(extent[0]*(1-kwargs.get('x_fraction'))+
                 extent[1]*kwargs.get('x_fraction'),
            extent[2]*(1-kwargs.get('y_fraction'))+
                 extent[3]*kwargs.get('y_fraction'),
            label,
            horizontalalignment=kwargs.get('horizontalalignment'),
            verticalalignment=kwargs.get('verticalalignment'),
            color=kwargs.get('color'),
            bbox=dict(facecolor=kwargs.get('facecolor'),
                      edgecolor=kwargs.get('color'),
                      boxstyle='round',
                      pad=0.5),
            size=kwargs.get('fontsize'),
            clip_on=True,
            zorder=kwargs.get('zorder'))

