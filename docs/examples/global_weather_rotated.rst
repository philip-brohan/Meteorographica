`Meteographica examples main page <examples.html>`_

Meteorographica examples: Global weathermap
===========================================

.. raw:: html

    <center>
    <table><tr><td>
    <a href="https://github.com/oldweather/DWR/raw/master/analyses/spaghetti_contour/Spaghetti_prmsl_1903102218_cera.png"><img src="https://github.com/oldweather/DWR/raw/master/analyses/spaghetti_contour/Spaghetti_prmsl_1903102218_cera.png""></a></td></tr>
    <tr><td>Global weather map for 16 October 1987, at 6am UTC, as reconstructed by the CERA-20C reanalysis (ensemble member 1 is shown). Contours show mean-sea-level pressure, vectors 10m wind, and green shading precipitation rate.</td></tr>
    </table>
    </center>

Collect the data (sea-level pressure, precipitation and 10m-wind ensembles from CERA20C for October 1987):

.. code-block:: python

    import Meteorographica.data.cera20c as cera20c
    for var in ('prmsl','prate','uwnd.10m','vwnd.10m'):
        cera20c.fetch(var,1987,10)

Make the figure:

.. literalinclude:: ../../../analyses/spaghetti_contour/prmsl_CERA.py

