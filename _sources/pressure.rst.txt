Meteorographica.pressure
========================

This module is designed to make plots of mean-sea-level-pressure (mslp), but they are basically just contour plots, so the functions can be used for any (continuous) scalar variable (with appropriate specification of levels).

It takes a :obj:`cartopy.mpl.geoaxes.GeoAxes` to draw into, and an :obj:`iris.cube.Cube` (with 'latitude' and 'longitude' dimensions) of data to plot. Then it's just:

.. code-block:: python

    Meteorographica.pressure.plot(geoaxes,cube,**options)

Three different types of plot are supported:

* 'contour' - straight contour plot of a single pressure field.
* 'spaghetti' - spaghetti-contour plot of multiple pressure fields.
* 'spread' - mean-contour plot with error bars derived from an ensemble of pressure fields.

See :doc:`examples of use <examples/examples>`.

|

.. automodule:: Meteorographica.pressure
    :members:
    :imported-members:
