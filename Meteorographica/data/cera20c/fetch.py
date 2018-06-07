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

# Functions to fetch CERA data through the ECMWF Public data API

import os
import subprocess
import calendar
import ecmwfapi

from utils import _hourly_get_file_name
from utils import _translate_for_file_names
from utils import monolevel_analysis
from utils import monolevel_forecast

def fetch(variable,year,month):
    """Get all data for one variable, for one month, from ECMWF's archive.

    Data wil be stored locally in directory $SCRATCH/CERA-20C, to be retrieved by :func:`load`. If the local file that would be produced already exists, this function does nothing.

    Args:
        variable (:obj:`str`): Variable to fetch (e.g. 'prmsl')
        year (:obj:`int`): Year to get data for.
        month (:obj:`int`): Month to get data for (1-12).

    Raises:
        StandardError: If Variable is not a supported value.

    |
    """
    if variable in monolevel_analysis:
        return _fetch_analysis_data_for_month(variable,year,
                                             month)
    if variable in monolevel_forecast:
        return _fetch_forecast_data_for_month(variable,year,
                                             month)
    raise StandardError("Unsupported variable %s" % variable)

def _fetch_analysis_data_for_month(variable,year,month):
        
    local_file=_hourly_get_file_name(variable,year,month)
    if os.path.isfile(local_file):
        # Got this data already
        return

    if not os.path.exists(os.path.dirname(local_file)):
        os.makedirs(os.path.dirname(local_file))

    server = ecmwfapi.ECMWFDataServer()
    server.retrieve({
        'dataset'   : 'cera20c',
        'stream'    : 'enda',
        'type'      : 'an',
        'class'     : 'ep',
        'expver'    : '1',
        'levtype'   : 'sfc',
        'param'     : _translate_for_file_names(variable),
        'time'      : '00/03/06/09/12/15/18/21',
        'grid'      : '1.25/1.25',
        'number'    : '0/1/2/3/4/5/6/7/8/9',
        'date'      : "%04d-%02d-%02d/to/%04d-%02d-%02d" %
                       (year,month,1,
                        year,month,
                        calendar.monthrange(year,month)[1]),
        'format'    : 'netcdf',
        'target'    : local_file
    })

def _fetch_forecast_data_for_month(variable,year,month):
        
    # Want 27 hours of forecast for each day
    #         (so we can interpolate over the seam),
    #  but the 27-hr forcast from one day has the same
    #      validity time as the 3-hr forecast from the
    #       next day - so need to download them separately
    #       and store in different files.

    # First 24-hours of forecast in main file
    local_file=_hourly_get_file_name(variable,year,month,
                                    fc_init=None)
    if os.path.isfile(local_file):
        # Got this data already
        return

    if not os.path.exists(os.path.dirname(local_file)):
        os.makedirs(os.path.dirname(local_file))

    server = ecmwfapi.ECMWFDataServer()
    server.retrieve({
        'dataset'   : 'cera20c',
        'stream'    : 'enda',
        'type'      : 'fc',
        'class'     : 'ep',
        'expver'    : '1',
        'levtype'   : 'sfc',
        'param'     : _translate_for_file_names(variable),
        'time'      : '18',
        'step'      : '3/6/9/12/15/18/21/24',
        'grid'      : '1.25/1.25',
        'number'    : '0/1/2/3/4/5/6/7/8/9',
        'date'      : "%04d-%02d-%02d/to/%04d-%02d-%02d" %
                       (year,month,1,
                        year,month,
                        calendar.monthrange(year,month)[1]),
        'format'    : 'netcdf',
        'target'    : local_file
    })


    # 27-hour forecast in additional file
    local_file=_hourly_get_file_name(variable,year,month,
                                     fc_init='last')
    if os.path.isfile(local_file):
        # Got this data already
        return

    if not os.path.exists(os.path.dirname(local_file)):
        os.makedirs(os.path.dirname(local_file))

    server = ECMWFDataServer()
    server.retrieve({
        'dataset'   : 'cera20c',
        'stream'    : 'enda',
        'type'      : 'fc',
        'class'     : 'ep',
        'expver'    : '1',
        'levtype'   : 'sfc',
        'param'     : _translate_for_file_names(variable),
        'time'      : '18',
        'step'      : '27',
        'grid'      : '1.25/1.25',
        'number'    : '0/1/2/3/4/5/6/7/8/9',
        'date'      : "%04d-%02d-%02d/to/%04d-%02d-%02d" %
                       (year,month,1,
                        year,month,
                        calendar.monthrange(year,month)[1]),
        'format'    : 'netcdf',
        'target'    : local_file
    })
