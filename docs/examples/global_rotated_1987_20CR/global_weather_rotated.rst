`Meteographica examples main page <../examples.html>`_

Meteorographica examples: Global weathermap (20CR version)
==========================================================

.. raw:: html

    <center>
    <table><tr><td>
    <a href="https://github.com/philip-brohan/Meteorographica/raw/master/docs/examples/global_rotated_1987/global.rotated.1987-10-16:06.png"><img src="https://github.com/philip-brohan/Meteorographica/raw/master/docs/examples/global_rotated_1987/global.rotated.1987-10-16:06.png"></a></td></tr>
    <tr><td>Global weather map for 16 October 1987, at 6am UTC, as reconstructed by the 20CR2c reanalysis (ensemble member 1 is shown). Contours show mean-sea-level pressure, vectors 10m wind, green shading precipitation rate, and yellow dots observations assimilated.</td></tr>
    </table>
    </center>

Collect the data (observations, sea-level pressure, precipitation and 10m-wind ensembles from 20CR2c for October 1987):

.. code-block:: python

    import Meteorographica.data.twcr as twcr
    twcr.fetch_observations(1987,version='2c')
    for var in ('prmsl','prate','uwnd.10m','vwnd.10m'):
        twcr.fetch(var,1987,version='2c')

Make the figure:

.. literalinclude:: GS_1987.rotated.py

