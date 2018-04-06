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

# Functions for handling observations.

import version_2c
import version_3

def fetch_observations(year,month=None,day=None,version='none'):
    """Get observations from the 20CR archive at NERSC.

    Data wil be stored locally in directory $SCRATCH/20CR, to be retrieved by :func:`load_observations`. If the local files that would be produced already exists, this function does nothing.

    For 20CR version 2c, the data is retrieved in calendar year blocks, and the 'month' and 'day' arguments are ignored. 

    Args:
        year (:obj:`int`): Year to get data for.
        month (:obj:`int`, optional): Month to get data for (1-12).
        day (:obj:`int`, optional): Day to get data for (1-31).
        version (:obj:`str`): 20CR version to retrieve data for.

    Raises:
        StandardError: If variable is not a supported value.
 
    |
    """

    if version=='2c':
        return version_2c.fetch_observations(year)
    if version in ('4.5.1','4.5.2'):
        return version_3.fetch_observations(year,month,version)
    raise StandardError("Unsupported version %s" % version)

def load_observations_1file(year,month,day,hour,version='none'):
    """Load observations from disc, that were used in the assimilation run at the time specified.

    Data must be available in directory $SCRATCH/20CR, previously retrieved by :func:`fetch_observations`.

    Args:
        year (:obj:`int`): Year of assimilation run.
        month (:obj:`int`): Month of assimilation run (1-12)
        day (:obj:`int`): Day of assimilation run (1-31).
        hour (:obj:`int`): Hour of assimilation run (0-23).
        version (:obj:`str`): 20CR version to load data from.

    Returns:
        :obj:`pandas.DataFrame`: Dataframe of observations.

    Raises:
        StandardError: Version number not supported, or data not on disc - see :func:`fetch_observations`

    |
    """

    if version=='2c':
        return version_2c.load_observations_1file(
                                 year,month,day,hour)
    if version in ('4.5.1','4.5.2'):
        return version_3.load_observations_1file(year,month,day,hour,version)
    raise StandardError("Unsupported version %s" % version)

def load_observations(start,end,version='none'):
    """Load observations from disc, for the selected period

    Data must be available in directory $SCRATCH/20CR, previously retrieved by :func:`fetch`.

    Args:
        start (:obj:`datetime.datetime`): Get observations at or after this time.
        end (:obj:`datetime.datetime`): Get observations before this time.
        version (:obj:`str`): 20CR version to load data from.

    Returns:
        :obj:`pandas.DataFrame`: Dataframe of observations.


    Raises:
        StandardError: Version number not supported, or data not on disc - see :func:`fetch_observations`

    |
    """

    if version=='2c':
        return version_2c.load_observations(start,end)
    if version in ('4.5.1','4.5.2'):
        return version_3.load_observations(start,end,version)
    raise StandardError("Unsupported version %s" % version)

def load_observations_fortime(v_time,version='none'):
    """Load observations from disc, that contribute to fields ata given time

    Data must be available in directory $SCRATCH/20CR, previously retrieved by :func:`fetch`.

    At the times when assimilation takes place, all the observations used at that time are provided by :func:`load_observations_1file` - this function serves the same function, but for intermediate times, where fields are obtained by interpolation. It gets all the observations from each field used in the interpolation, and assigns a weight to each one - the same as the weight used in interpolating the fields.

    Args:
        v_time (:obj:`datetime.datetime`): Get observations associated with this time.
        version (:obj:`str`): 20CR version to load data from.

    Returns:
        :obj:`pandas.DataFrame`: same as from :func:`load_observations`, except with aded column 'weight' giving the weight of each observation at the given time.

    Raises:
        StandardError: Version number not supported, or data not on disc - see :func:`fetch_observations`

    |
    """

    if version=='2c':
        return version_2c.load_observations_fortime(v_time)
    if version in ('4.5.1','4.5.2'):
        return version_3.load_observations_fortime(v_time,version)
    raise StandardError("Unsupported version %s" % version)
