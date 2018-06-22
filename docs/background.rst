Meteorographica.background
==========================

A weather-map should show the weather with as little distraction as possible. We need a map background to show where we are in the world, and also to indicate the local orography, which can be important, but it should be as unobtrusive as posible.

This package two features to add background to plots. A function to draw a lat:lon grid, and a custom background image derived from `Natural Earth data <https://www.naturalearthdata.com/>`_.

The grid takes a :obj:`cartopy.mpl.geoaxes.GeoAxes` to draw into

.. code-block:: python

    Meteorographica.background.add_grid(geoaxes,**options)


The image is applied using an existing GeoAxes function:

.. code-block:: python

    ax.background_img(name='GreyT', resolution='low')

But we do have to make it - this should be done during :doc:`installation <install>`.

See :doc:`examples of use <examples/examples>`.

|

.. automodule:: Meteorographica.background
    :members:
    :imported-members:

.. automodule:: Meteorographica.scripts.fetch_backgrounds
    :members:
    :imported-members:
