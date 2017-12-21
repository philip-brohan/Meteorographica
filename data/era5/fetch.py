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

from . import get_data_file_name
from . import translate_for_file_names
from . import monolevel_analysis
from . import monolevel_forecast

def fetch_data_for_month(variable,year,month,
                                  stream='oper'):
    if variable in monolevel_analysis:
        return fetch_analysis_data_for_month(variable,year,
                                             month,stream)
    if variable in monolevel_forecast:
        return fetch_forecast_data_for_month(variable,year,
                                             month,stream)
    raise StandardError("Unsupported variable %s" % variable)

def fetch_analysis_data_for_month(variable,year,month,
                                  stream='oper'):
        
    local_file=get_data_file_name(variable,year,month,stream)
    if os.path.isfile(local_file):
        # Got this data already
        return

    if not os.path.exists(os.path.dirname(local_file)):
        os.makedirs(os.path.dirname(local_file))

    server = ECMWFDataServer()
    grid='0.25/0.25'
    if stream=='enda':
        grid='0.5/0.5'
    server.retrieve({
        'dataset'   : 'era5',
        'stream'    : stream,
        'type'      : 'an',
        'levtype'   : 'sfc',
        'param'     : translate_for_file_names(variable),
        'time'      : '0/to/23/by/1',
        'grid'      : grid,
        'date'      : "%04d-%02d-%02d/to/%04d-%02d-%02d" %
                       (year,month,1,
                        year,month,
                        monthrange(year,month))
        'format'    : 'netcdf',
        'target'    : local_file
    })

def fetch_forecast_data_for_month(variable,year,month,
                                  stream='oper'):
        
    # Need two sets of forecast data - from the runs at 6 and 18
    for start_hour in [6,18]:

        local_file=get_data_file_name(variable,year,month,stream,
                                      start_hour=start_hour)
        if os.path.isfile(local_file):
            # Got this data already
            return
            
        if not os.path.exists(os.path.dirname(local_file)):
            os.makedirs(os.path.dirname(local_file))

        server = ECMWFDataServer()
        grid='0.25/0.25'
        if stream=='enda':
            grid='0.5/0.5'
        server.retrieve({
            'dataset'   : 'era5',
            'stream'    : stream,
            'type'      : 'fc',
            'step'      : '0/to/18/by/1',
            'levtype'   : 'sfc',
            'param'     : translate_for_file_names(variable),
            'time'      : start_hour,
            'grid'      : grid,
            'date'      : "%04d-%02d-%02d/to/%04d-%02d-%02d" %
                           (year,month,1,
                            year,month,
                            calendar.monthrange(year,month))
            'format'    : 'netcdf',
            'target'    : local_file
        })


def fetch_data_for_month(variable,year,month,
                         version,type='ensemble',source=None):
    """Version 3 specific - for version 2 use fetch_data_for_year."""
    
    if(version[0]!='4' and month is not None):
        raise StandardError("Use 'fetch_data_for_year' for version 2")
    if(month is None):
        month=1   # Arbitrary, v2 data is by year, so any month would do
    # Day and hour also set arbtrarily to 1 and 6
    local_file=get_data_file_name(variable,year,month,1,6,version,type)

    if ((variable != 'observations') and os.path.isfile(local_file)): 
        # Got this data already
        return

    if not os.path.exists(os.path.dirname(local_file)):
        os.makedirs(os.path.dirname(local_file))

    remote_file=get_remote_file_name(variable,year,month,version,type,source)

    if(variable=='observations'):
        # Multiple files - use rsync
        local_file=os.path.dirname(local_file)
        cmd="rsync -Lr %s/ %s" % (remote_file,local_file)
        #print(cmd)
        scp_retvalue=subprocess.call(cmd,shell=True) # Why need shell=True?
        if scp_retvalue==3:
            raise StandardError("Remote data not available")
        if scp_retvalue!=0:
            raise StandardError("Failed to retrieve data")
        
    else:
        # Single file - use scp
        cmd="scp %s %s" % (remote_file,local_file)
        #print(cmd)
        scp_retvalue=subprocess.call(cmd,shell=True)
        if scp_retvalue==6:
            raise StandardError("Remote data not available")
        if scp_retvalue!=0:
            raise StandardError("Failed to retrieve data")

