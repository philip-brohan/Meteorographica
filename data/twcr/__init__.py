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
"""
This package retrieves and loads data from the `Twentieth Century Reanalysis (20CR) <https://www.esrl.noaa.gov/psd/data/20thC_Rean/>`_.

It retrieves the data from the `20CR portal <http://portal.nersc.gov/project/20C_Reanalysis/>`_ at `NERSC <http://www.nersc.gov>`_.

At the moment, only version '2c' of 20CR is supported for public use.

Only hourly data is supported (no daily or monthly averages) for 5 surface variables:

* Mean-sea-level pressure: 'mslp'
* 2m air temperature: 'air.2m'
* Precipitation rate: 'prate'
* 10m meridional wind: 'uwnd.10m'
* 10m zonal wind: 'vwnd.10m'

Data retrieved is stored in directory $SCRATCH/20CR - the 'SCRATCH' environment variable must be set. Data is retrieved in 1-year batches

For example:

.. code-block:: python

    import Meteorographica.data.twcr as twcr
    twcr.fetch('prate',1987,version='2c')

Will retrieve precipitation rate data for the whole of 1987, and

.. code-block:: python

    pr=twcr.load('prate',1987,3,12,15.25,version='2c')

will then load the precipitation rates at quarter past 3pm on March 12 1987 from the retrieved dataset as an :obj:`iris.cube.Cube`. Note that as 20CR only provides data at 6-hourly or 3-hourly intervals, the value for 15.25 will be interpolated between the outputs. Also, as 20CR is an ensemble dataset, the result will include all 56 ensemble members.

Observations files are also available. They can be fetched with:

.. code-block:: python

    twcr.fetch_observations(1987,version='2c')

There is one observations file for each 6-hourly assimilation run. Load all the observations available to the assimilation run for 12 noon on March 12 1987 (as a :obj:`pandas.DataFrame`) with:

.. code-block:: python

    o=twcr.load_observations_1file(1987,3,12,12,version='2c')

or just load all the observations valid between 6am and 6pm that day with:

.. code-block:: python

    import datetime
    o=twcr.load_observations(datetime.datetime(1987,3,12,6),
                             datetime.datetime(1987,3,12,18),
                             version='2c')


|
"""

from utils import *
from load import *
from fetch import *
from observations import *
