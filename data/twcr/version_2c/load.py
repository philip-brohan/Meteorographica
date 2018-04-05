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

# Load 2c data from a local file

import os
import os.path
import iris
import iris.time
import datetime
import numpy as np
import pandas

from utils import _get_data_file_name

# Eliminate incomprehensible warning message
iris.FUTURE.netcdf_promote='True'

# Need to add coordinate system metadata so they work with cartopy
coord_s=iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS)

def _is_in_file(variable,hour):
    """Is the variable available for this time?
       Or will it have to be interpolated?"""
    if hour%6==0:
        return True
    return False

def _get_previous_field_time(variable,year,month,day,hour):
    """Get the latest time, before the given time,
                     for which there is saved data"""
    return {'year':year,'month':month,'day':day,'hour':int(hour/6)*6}

def _get_next_field_time(variable,year,month,day,hour):
    """Get the earliest time, after the given time,
                     for which there is saved data"""
    dr = {'year':year,'month':month,'day':day,'hour':int(hour/6)*6+6}
    if dr['hour']>=24:
        d_next= ( datetime.date(dr['year'],dr['month'],dr['day']) 
                 + datetime.timedelta(days=1) )
        dr = {'year':d_next.year,'month':d_next.month,'day':d_next.day,
              'hour':dr['hour']-24}
    return dr

def _get_slice_at_hour_at_timestep(variable,year,month,day,hour):
    """Get the cube with the data, given that the specified time
       matches a data timestep."""
    if not _is_in_file(variable,hour):
        raise ValueError("Invalid hour - data not in file")
    file_name=_get_data_file_name(variable,year)
    time_constraint=iris.Constraint(time=iris.time.PartialDateTime(
                                    year=year,
                                    month=month,
                                    day=day,
                                    hour=hour))
    try:
        with iris.FUTURE.context(cell_datetime_objects=True):
            hslice=iris.load_cube(file_name,
                                  time_constraint)
    except iris.exceptions.ConstraintMismatchError:
       raise StandardError("%s not available for %04d-%02d-%02d:%02d" % 
                            (variable,year,month,day,hour))

    # Enhance the names and metadata for iris/cartopy
    hslice.coord('latitude').coord_system=coord_s
    hslice.coord('longitude').coord_system=coord_s
    hslice.dim_coords[0].rename('member') # Remove spaces in name
    return hslice

def load(variable,year,month,day,hour):
    """Load requested data from disc, interpolating if necessary.

    Data must be available in directory $SCRATCH/20CR, previously retrieved by :func:`fetch`.

    Args:
        variable (:obj:`str`): Variable to fetch (e.g. 'prmsl')
        year (:obj:`int`): Year to get data for.
        month (:obj:`int`): Month to get data for (1-12).
        day (:obj:`int`): Day to get data for (1-31).
        hour (:obj:`float`): Hour to get data for (0-23.99). Note that this isn't an integer, for minutes and seconds, use fractions of an hour.

    Returns:
        :obj:`iris.cube.Cube`: Global field of variable at time.

    Note that 20CR data is only output every 3 hours (precip,wind) or 6 hours (prmsl), so if hour%6!=0, the result may be linearly interpolated in time. If you want data after 18:00 on the last day of a month, you will need to fetch the next month's data too, as it will be used in the interpolation.

    Raises:
        StandardError: Data not on disc - see :func:`fetch`

    |
    """
    if _is_in_file(variable,hour):
        return(_get_slice_at_hour_at_timestep(variable,year,
                                              month,day,
                                              hour))
    previous_step=_get_previous_field_time(variable,year,month,
                                           day,hour)
    next_step=_get_next_field_time(variable,year,month,
                                   day,hour)
    dt_current=datetime.datetime(year,month,day,int(hour),int((hour%1)*60))
    dt_previous=datetime.datetime(previous_step['year'],
                                  previous_step['month'],
                                  previous_step['day'],
                                  previous_step['hour'])
    dt_next=datetime.datetime(next_step['year'],
                              next_step['month'],
                              next_step['day'],
                              next_step['hour'])
    s_previous=_get_slice_at_hour_at_timestep(variable,
                                              previous_step['year'],
                                              previous_step['month'],
                                              previous_step['day'],
                                              previous_step['hour'])
    s_next=_get_slice_at_hour_at_timestep(variable,
                                          next_step['year'],
                                          next_step['month'],
                                          next_step['day'],
                                          next_step['hour'])
    # Iris won't merge cubes with different attributes
    s_previous.attributes=s_next.attributes
    s_next=iris.cube.CubeList((s_previous,s_next)).merge_cube()
    s_next=s_next.interpolate([('time',dt_current)],iris.analysis.Linear())
    return s_next

