Meteorographica: Data
=====================

Suppose you wanted global near-surface air temperatures for 3:30pm (UTC) on March 1st 1903. One possible source is the `Twentieth Century Reanalysis (20CR) <https://www.esrl.noaa.gov/psd/data/20thC_Rean/>`_ and it would be good to have a function something like:

.. code-block:: python

   at=get_data(source='20CR',variable='2m air temperature',year=1903,
                   month=3,day=1,hour=15,minute=30)

That would query the archive containing all the 20CR output and return an :class:`iris.cube.Cube` or with the selected temperatures. The Meteorographica.data modules aim to provide essentially this functionality.

Unfortunately it's not quite as easy as that. The first problem is that retrieving data from remote archives is pretty slow - the data is generally on tape, and quite possibly also on the far side of the world. So it's best to break the problem into two haves: first fetching a large block of data from the archive and storing it on local disc, then getting data from that local file.

.. code-block:: python

   # Fetch all the 2m temperatures for 1903 and store them locally
   #  This function may take a long time to run.
   fetch_data(source='20CR',variable='2m air temperature',year=1903)
   # Now we can get data for any time in 1903 - fast - from the local store
   at=get_data(source='20CR',variable='2m air temperature',year=1903,
                   month=3,day=1,hour=15,minute=30)

This means some local disc space is needed to store data - Meteorographica requires the environment variable 'SCRATCH' to be set with the name of a suitable directory.

A second problem is that we want data from many different sources, and they can be *very* different. So each source is supported by a separate, independent module. In each case there is a fetch function and a load function, and they are designed to be similar, but each has its own quirks. The advantage of this approach is that adding a new datasource can be done without any impact on the existing ones.

.. toctree::
   :maxdepth: 2

   datasources/twcr
   datasources/cera20c
   datasources/era5
   datasources/mogreps
