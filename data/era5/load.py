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

# The functions in this module provide the main way to load
# ERA5 data.

import os
import os.path
import iris
import iris.time
import datetime
import numpy as np

from utils import _hourly_get_file_name
from utils import _translate_for_file_names
from utils import monolevel_analysis
from utils import monolevel_forecast

# Eliminate incomprehensible warning message
iris.FUTURE.netcdf_promote='True'

# Need to add coordinate system metadata so they work with cartopy
coord_s=iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS)

def _is_in_file(variable,year,month,day,hour,stream='enda'):
    """Is the variable available for this time?
       Or will it have to be interpolated?"""
    if stream=='enda' and hour%3==0:
        return True
    if stream=='oper' and hour%1==0:
        return True
    return False

def _get_previous_field_time(variable,year,month,day,hour,stream='enda'):
    """Get the latest time, before the given time,
                     for which there is saved data"""
    if stream=='enda':
        return {'year':year,'month':month,'day':day,'hour':int(hour/3)*3}
    if stream=='oper':
        return {'year':year,'month':month,'day':day,'hour':int(hour)}
    raise StandardError("Unknown stream %s" % stream)

def _get_next_field_time(variable,year,month,day,hour,stream='enda'):
    """Get the earliest time, after the given time,
                     for which there is saved data"""  
    if stream=='enda':
       dr = {'year':year,'month':month,'day':day,'hour':int(hour/3)*3+3}
    elif stream=='oper':
       dr = {'year':year,'month':month,'day':day,'hour':int(hour)+1}
    else:
       raise StandardError("Unknown stream %s" % stream) 
    if dr['hour']>=24:
        d_next= ( datetime.date(dr['year'],dr['month'],dr['day']) 
                 + datetime.timedelta(days=1) )
        dr = {'year':d_next.year,'month':d_next.month,'day':d_next.day,
              'hour':dr['hour']-24}
    return dr

def _get_slice_at_hour_at_timestep(variable,year,month,day,hour,
                                   stream='enda',fc_init=None):
    """Get the cube with the data, given that the specified time
       matches a data timestep."""
    if not _is_in_file(variable,year,month,day,hour,stream=stream):
        raise ValueError("Invalid hour - data not in file")
    file_name=_hourly_get_file_name(variable,year,month,day,hour,
                                   stream=stream,fc_init=fc_init)
    if not os.path.isfile(file_name):
        raise StandardError(("%s for %04d/%02d not available"+
                             " might need era5.fetch") % (variable,
                                                             year,month))
    time_constraint=iris.Constraint(time=iris.time.PartialDateTime(
                                   year=year,
                                   month=month,
                                   day=day,
                                   hour=hour))
    try:
        with iris.FUTURE.context(cell_datetime_objects=True):
            hslice=iris.load_cube(file_name,
                                  time_constraint)
    # This isn't the right error to catch
    except iris.exceptions.ConstraintMismatchError:
       print("Data not available")

    # Enhance the names and metadata for iris/cartopy
    hslice.coord('latitude').coord_system=coord_s
    hslice.coord('longitude').coord_system=coord_s
    if stream=='enda':
        hslice.dim_coords[0].rename('member') # Consistency with 20CR
    return hslice

def load(variable,year,month,day,hour,
                      stream='enda',fc_init=None):
    """Load requested data from disc, interpolating if necessary.

    Data must be available in directory $SCRATCH/ERA5, previously retrieved by :func:`fetch`.

    Args:
        variable (:obj:`str`): Variable to fetch (e.g. 'prmsl')
        year (:obj:`int`): Year to get data for.
        month (:obj:`int`): Month to get data for (1-12).
        day (:obj:`int`): Day to get data for (1-31).
        hour (:obj:`float`): Hour to get data for (0-23.99). Note that this isn't an integer, for minutes and seconds, use fractions of an hour.
        fc_init (:obj:`int`): If not None; 6 or 18. See below.

    Returns:
        :obj:`iris.cube.Cube`: Global field of variable at time.

    Note that ERA5 data is only output every 3 hours (enda) or hour (oper), so if hour%3!=0, the result may be linearly interpolated in time. If you want data after 21:00 on the last day of a month, you will need to fetch the next month's data too, as it will be used in the interpolation.

    Precipitation data in ERA5 is a forecast field: twice a day (at 06:00 and 18:00) forecast data is calculated for the next 18 hours. So at 21:00, for example, there are 2 sets of precipitation available: a 3-hour forecast starting at 18 that day, and a 15-hour forecast starting at 06:00, and there is a discontinuity between the two fields. This function will always load the shortest lead-time forecast available unless fc_init is set (to 6 or 18) in which case it will load the forecast starting at the hour specified. You will only need this if you are making videos, or otherwise need time-continuous forecast fields, in which case you will need to be clever in smoothing over the discontinuity. For analysis fields (everything except prate), this issue does not arise and fc_init is ignored.

    Raises:
        StandardError: Data not on disc - see :func:`fetch`

    |
    """
    if _is_in_file(variable,year,month,day,hour,stream=stream):
        return(_get_slice_at_hour_at_timestep(variable,year,
                                              month,day,
                                              hour,stream=stream,
                                              fc_init=fc_init))
    previous_step=_get_previous_field_time(variable,year,month,
                                           day,hour,stream=stream)
    next_step=_get_next_field_time(variable,year,month,
                                   day,hour,stream=stream)
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
                                              previous_step['hour'],
                                              stream=stream,
                                              fc_init=fc_init)
    s_next=_get_slice_at_hour_at_timestep(variable,
                                          next_step['year'],
                                          next_step['month'],
                                          next_step['day'],
                                          next_step['hour'],
                                          stream=stream,
                                          fc_init=fc_init)
 
    # Iris won't merge cubes with different attributes
    s_previous.attributes=s_next.attributes
    s_next=iris.cube.CubeList((s_previous,s_next)).merge_cube()
    s_next=s_next.interpolate([('time',dt_current)],iris.analysis.Linear())
    return s_next

