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
Utility functions for file and variable name mapping for 20CR.

"""

import os
import datetime
import re
import version_2
import version_3


# Get major version (2 or 3) from run code ('3.5.1' or similar)
# The 'version' parameter in all the function calls is actualy the run code
# This was probably a bad decision, but I'm not changing it now.
def get_version_from_ensda(version):
    version=str(version)
    if version=='2': version='3.2.1'
    if version=='2c': version='3.5.1'
    vm = re.compile('^\d\.\d\.\d$')
    if not vm.match(version):
        raise StandardError('Invalid version number %s' % version)
    if version[0]=='3': return 2
    if version[0]=='4': return 3
    raise StandardError('Invalid version number %s' % version)
   

# File name for data for a given variable and month
def hourly_get_file_name(variable,year,month,
                         day=15,hour=12,
                         type='ensemble',
                         version=None):
    vn=get_version_from_ensda(version)
    if vn==2:
        return version_2.get_data_file_name(
                              variable,year,month,
                              day=day,hour=hour,type=type,
                              version=version)
    if vn==3:
        return version_3.get_data_file_name(
                              variable,year,month,
                              day=day,hour=hour,type=type,
                              version=version)
    raise StandardError('Invalid version number %s' % version)
