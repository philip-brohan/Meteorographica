Meteorographica.wind
====================

This module is designed to make plots of 10-metre wind,  the functions can be used for any 2-element vector variable (with appropriate scaling factors).

It takes a :obj:`cartopy.mpl.geoaxes.GeoAxes` to draw into, and two iris :obj:`iris.cube.Cube` (each with 'latitude' and 'longitude' dimensions) as the zonal and meridional components to plot. Then it's just:

.. code-block:: python

    Meteorographica.wind.plot(geoaxes,zonal_cube,meridional_cube,**options)

See :doc:`examples of use <examples/examples>`.

|

.. automodule:: Meteorographica.wind
    :members:
    :imported-members:
