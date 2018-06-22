Meteorographica.observations
============================

This module is designed to make plots of observation positions, but they are basically just image maps, so the functions can be used for any scalar variable (with appropriate scaling).

It takes a :obj:`cartopy.mpl.geoaxes.GeoAxes` to draw into, and an :obj:`pandas.DataFrame` of observations. Then it's just:

.. code-block:: python

    Meteorographica.observations.plot(geoaxes,dataframe,**options)

Only the observation positions are plotted.

See :doc:`examples of use <examples/examples>`.

|

.. automodule:: Meteorographica.observations
    :members:
    :imported-members:
