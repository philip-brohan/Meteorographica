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

# Utility functions for file and variable name mapping for 20CR.

import version_2c
import version_3

# File name for data for a given variable and month
def _hourly_get_file_name(variable,year,month=6,
                          day=15,hour=12,
                          version=None):
    if vn=='2c':
        return version_2c._get_data_file_name(
                                 variable,year)
    if vn in ('4.5.1','4.5.2'):
        return version_3._get_data_file_name(
                                 variable,year,month)
       
    raise StandardError('Invalid version %s' % version)
