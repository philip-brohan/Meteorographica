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

# Utility functions for file and variable name mapping for ERA5.

import os
import datetime

# Names of analysis and forecast variables supported
monolevel_analysis=('prmsl','air.2m','uwnd.10m','vwnd.10m','icec','sst')
monolevel_forecast=('prate')

# ERA5 uses different variable names from 20CR
def _translate_for_variable_names(variable):

    if(variable=='prmsl'):
        return 'msl'
    if(variable=='air.2m'):
        return 't2m'
    if(variable=='uwnd.10m'):
        return 'u10'
    if(variable=='vwnd.10m'):
        return 'v10'
    if(variable=='icec'):
        return 'ci'
    if(variable=='sst'):
        return 'sst'
    if(variable=='prate'):
        return 'tp'
    raise StandardError("Unsupported variable %s" % variable)

# ERA5 uses different file names from 20CR
def _translate_for_file_names(variable):

    if(variable=='prmsl'):
        return 'msl'
    if(variable=='air.2m'):
        return '2t'
    if(variable=='uwnd.10m'):
        return '10u'
    if(variable=='vwnd.10m'):
        return '10v'
    if(variable=='icec'):
        return 'ci'
    if(variable=='sst'):
        return 'sst'
    if(variable=='prate'):
        return 'tp'
    raise StandardError("Unsupported variable %s" % variable)

# Directory to keep downloaded data in
def _get_data_dir():
    scratch=os.getenv('SCRATCH')
    if scratch is None:
        raise StandardError("SCRATCH environment variable is undefined")
    base_file = "%s/ERA5" % scratch
    if os.path.isdir(base_file):
        return base_file
    raise StandardError("Scratch directory %s does not exist" % scratch)

# File name for data for a given variable and month
def _hourly_get_file_name(variable,year,month,
                         day=15,hour=12,
                         fc_init=None,
                         stream='enda'):
    base_dir=_get_data_dir()
    if type=='normal':
        file_name="%s/normals/%s/hourly/%02d/%s.nc" % (base_dir,stream,
                                                    month,variable)
        return file_name
     
    if type=='standard.deviation':
        file_name="%s/standard.deviations/%s/hourly/%02d/%s.nc" % (base_dir,
                                                 stream,month,variable)
        return file_name

    dir_name="%s/%s/hourly/%04d/%02d/" % (base_dir,stream,
                                       year,month)
    file_name="%s/%s.nc" % (dir_name,variable)
    if variable in monolevel_forecast:
        if fc_init==None:
            fc_init=18
            if hour>=6 and hour<18:
                fc.init=6
        if fc_init!=6 and fc_init!=18:
            raise StandardError(
             "Forcast initialisation time must be 6 or 18")
        if fc_init==6 and hour<6 and hour>0:
            raise StandardError(
          "Hour more than 18 hours after forecast initialisation")
        if fc_init==18 and hour<18 and hour>12:
            raise StandardError(
          "Hour more than 18 hours after forecast initialisation")
        if hour<fc_init:
            dte=(datetime.datetime(year,month,day) -
                           datetime.timedelta(days=1))
            dir_name="%s/%s/hourly/%04d/%02d" % (base_dir,stream,
                                                 dte.year,dte.month)
        file_name="%s/%s.%02d.nc" % (dir_name,variable,fc_init)

    return file_name
