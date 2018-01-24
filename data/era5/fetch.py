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
The functions in this module fetch ERA5 data from ECMWF and
store it on $SCRATCH.

Uses the ECMWF Public data API:
  https://software.ecmwf.int/wiki/display/WEBAPI/ECMWF+Web+API+Home
"""

import os
import subprocess
from calendar import monthrange
from ecmwfapi import ECMWFDataServer

from . import hourly_get_file_name
from . import translate_for_file_names
from . import monolevel_analysis
from . import monolevel_forecast

def fetch_data_for_month(variable,year,month,stream='enda'):
    if variable in monolevel_analysis:
        return fetch_analysis_data_for_month(variable,year,
                                             month)
    if variable in monolevel_forecast:
        return fetch_forecast_data_for_month(variable,year,
                                             month)
    raise StandardError("Unsupported variable %s" % variable)

def fetch_analysis_data_for_month(variable,year,month,
                                  stream='enda'):
        
    local_file=hourly_get_file_name(variable,year,month,
                                    stream=stream)
    if os.path.isfile(local_file):
        # Got this data already
        return

    if not os.path.exists(os.path.dirname(local_file)):
        os.makedirs(os.path.dirname(local_file))

    grid='0.5/0.5'
    if stream=='oper':
        grid='0.25/0.25'
    server = ECMWFDataServer()
    server.retrieve({
        'dataset'   : 'era5',
        'stream'    : stream,
        'type'      : 'an',
        'levtype'   : 'sfc',
        'param'     : translate_for_file_names(variable),
        'grid'      : grid,
        'time'      : '0/to/23/by/1',
        'date'      : "%04d-%02d-%02d/to/%04d-%02d-%02d" %
                       (year,month,1,
                        year,month,
                        monthrange(year,month)[1]),
        'format'    : 'netcdf',
        'target'    : local_file
    })

def fetch_forecast_data_for_month(variable,year,month,
                                  stream='enda'):
        
    # Need two sets of forecast data - from the runs at 6 and 18
    for start_hour in (6,18):

        local_file=hourly_get_file_name(variable,year,month,
                                    fc_init=start_hour,stream=stream)
        if os.path.isfile(local_file):
            # Got this data already
            return

        if not os.path.exists(os.path.dirname(local_file)):
            os.makedirs(os.path.dirname(local_file))

        grid='0.5/0.5'
        if stream=='oper':
            grid='0.25/0.25'
        server = ECMWFDataServer()
        server.retrieve({
            'dataset'   : 'era5',
            'stream'    :  stream,
            'type'      : 'fc',
            'levtype'   : 'sfc',
            'param'     : translate_for_file_names(variable),
            'grid'      : grid,
            'time'      : "%02d" % start_hour,
            'step'      : '0/to/18/by/1',
            'grid'      : '1.25/1.25',
            'number'    : '0/1/2/3/4/5/6/7/8/9',
            'date'      : "%04d-%02d-%02d/to/%04d-%02d-%02d" %
                           (year,month,1,
                            year,month,
                            monthrange(year,month)[1]),
            'format'    : 'netcdf',
            'target'    : local_file
        })


