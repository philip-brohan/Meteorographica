Meteorographica.precipitation
=============================

This module is designed to make plots of precipitation rate, but they are basically just image maps, so the functions can be used for any scalar variable (with appropriate scaling).

It takes a :obj:`cartopy.mpl.geoaxes.GeoAxes` to draw into, and an :obj:`iris.cube.Cube` (with 'latitude' and 'longitude' dimensions) of data to plot. Then it's just:

.. code-block:: python

    Meteorographica.precipitation.plot(geoaxes,cube,**options)

Three different types of plot are supported:

See :doc:`examples of use <examples/examples>`.

|

.. automodule:: Meteorographica.precipitation
    :members:
    :imported-members:
