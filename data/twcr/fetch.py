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

# Functions for getting data from NERSC.

import version_2c
import version_3
import observations

def fetch(variable,year,month=1,day=1,version='none'):
    """Get data for one variable, from the 20CR archive at NERSC.

    Data wil be stored locally in directory $SCRATCH/20CR, to be retrieved by :func:`load`. If the local file that would be produced already exists, this function does nothing.

    For 20CR version 2c, the data is retrieved in calendar year blocks, and the 'month' and 'day' arguments are ignored. 

    Args:
        variable (:obj:`str`): Variable to fetch (e.g. 'prmsl').
        year (:obj:`int`): Year to get data for.
        month (:obj:`int`, optional): Month to get data for (1-12).
        day (:obj:`int`, optional): Day to get data for (1-31).
        version (:obj:`str`): 20CR version to retrieve data for.

    Raises:
        StandardError: If variable is not a supported value.
 
    |
    """

    if variable=='observations':
        return observations.fetch_observations(year,
                                  month=month,day=day,
                                  version=version)

    if version=='2c':
        return version_2c.fetch(variable,year)
    if version in ('4.5.1','4.5.2'):
        return version_3.fetch(variable,year,month,version)

    raise StandardError("Unsupported version %s" % version)
