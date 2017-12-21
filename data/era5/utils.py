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
Utility functions for file and variable name mapping for ERA5.

"""

# Names of analysis and forecast variables supported
monolevel_analysis=('prmsl','air.2m','uwnd.10m','vwnd.10m','icec','sst')
monolevel_forecast=('prate')

# ERA5 uses different variable names from 20CR
def translate_for_variable_names(variable):

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
def translate_for_file_names(variable):

    if(variable=='prmsl'):
        return 'msl'
    if(variable=='air.2m'):
        return 't2m'
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

def get_data_dir:
