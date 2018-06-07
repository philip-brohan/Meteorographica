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
This package retrieves and loads data from the `ERA5 reanalysis <https://www.ecmwf.int/en/forecasts/datasets/reanalysis-datasets/era5>`_.

To retrieve the data, it uses the `ECMWF Public data API <https://software.ecmwf.int/wiki/display/WEBAPI/ECMWF+Web+API+Home>`_. You will need to install a key and the client libraries as described in `the API documentation <https://software.ecmwf.int/wiki/display/WEBAPI/Access+ECMWF+Public+Datasets>`_. Note that this is the same system used by `Meteographica.data.cera20c` - the same key and libraries will let you use that as well.

Only hourly data is supported (no daily or monthly averages) for 7 surface variables:

* Mean-sea-level pressure: 'mslp'
* 2m air temperature: 'air.2m'
* Precipitation rate: 'prate'
* 10m meridional wind: 'uwnd.10m'
* 10m zonal wind: 'vwnd.10m'
* Sea-surface temperature: 'sst'
* Sea-ice coverage: 'icec'

Data retrieved is stored in directory $SCRATCH/ERA5 - the 'SCRATCH' environment variable must be set. Data is retrieved in 1-month batches: ERA 5 comes in two streams: the 'oper' stream is a single member analysis at highest resolution, and the 'enda' stream is a 10-member ensemble at lower resolution - both are supported.

For example:

.. code-block:: python

    import Meteorographica.data.era5 as era5
    era5.fetch('prate',2015,3,stream='enda')

Will retrieve precipitation rate data for the whole of March 2015, and

.. code-block:: python

    pr=era5.load('prate',2015,3,12,15.25,stream='enda')

will then load the precipitation rates at quarter past 3pm on March 12 2015 from the retrieved dataset as a :class:`iris.cube.Cube`. Note that as ERA only provides data at hourly or 3-hourly intervals, the value for 15.25 will be interpolated between the outputs. Also, as ERA5 stream 'enda' is an ensemble dataset, the result will include all 10 ensemble members.

|
"""


from utils import *
from fetch import *
from load import *

