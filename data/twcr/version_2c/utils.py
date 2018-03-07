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

# Utility functions for version 2c

import os

def _get_data_dir():
    """Return the root directory containing 20CR netCDF files"""
    g="%s/20CR/version_%s/" % (os.environ['SCRATCH'],'2c')
    return g

def _get_data_file_name(variable,year):
    """Return the name of the file containing data for the
       requested variable, at the specified time, from the
       20CR version."""
    base_dir=_get_data_dir()
    name="%s/%04d/%s.nc" % (base_dir,year,variable)
    return name

