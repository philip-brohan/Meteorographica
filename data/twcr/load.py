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

# Load 20CR data from local files.

import version_2c
import version_3

def load(variable,year,month,day,hour,version):
    """Load requested data from disc, interpolating if necessary.

    Data must be available in directory $SCRATCH/20CR, previously retrieved by :func:`fetch`.

    Args:
        variable (:obj:`str`): Variable to fetch (e.g. 'prmsl')
        year (:obj:`int`): Year to get data for.
        month (:obj:`int`): Month to get data for (1-12).
        day (:obj:`int`): Day to get data for (1-31).
        hour (:obj:`float`): Hour to get data for (0-23.99). Note that this isn't an integer, for minutes and seconds, use fractions of an hour.
        version (:obj:`str`): 20CR version to load data from.

    Returns:
        :obj:`iris.cube.Cube`: Global field of variable at time.

    Note that 20CR data is only output every 6 hours (prmsl) or 3 hours, so if hour%3!=0, the result may be linearly interpolated in time. If you want data after 18:00 on the last day of a month, you will need to fetch the next month's data too, as it will be used in the interpolation.

    Raises:
        StandardError: Version number not supported, or data not on disc - see :func:`fetch`

    |
    """
    if version=='2c':
        return version_2c.load(variable,year,month,
                                day,hour)
    if version in ('4.5.1','4.5.2'):
        return version_3.load(variable,year,month,
                                day,hour,version)
    raise StandardError('Invalid version number %s' % version)

