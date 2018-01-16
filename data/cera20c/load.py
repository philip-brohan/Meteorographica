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
The functions in this module provide the main way to load
CERA-20C data.
"""

import os
import os.path
import iris
import iris.time
import datetime
import numpy as np

from . import hourly_get_file_name
from . import translate_for_file_names
from . import monolevel_analysis
from . import monolevel_forecast

# Eliminate incomprehensible warning message
iris.FUTURE.netcdf_promote='True'

# Need to add coordinate system metadata so they work with cartopy
coord_s=iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS)

def is_in_file(variable,year,month,day,hour):
    """Is the variable available for this time?
       Or will it have to be interpolated?"""
    if hour%3==0 :
        return True 
    return False

def get_previous_field_time(variable,year,month,day,hour):
    """Get the latest time, before the given time,
                     for which there is saved data"""
    return {'year':year,'month':month,'day':day,'hour':int(hour/3)*3}

def get_next_field_time(variable,year,month,day,hour):
    """Get the earliest time, after the given time,
                     for which there is saved data"""
    dr = {'year':year,'month':month,'day':day,'hour':int(hour/3)*3+3}
    if dr['hour']>=24:
        d_next= ( datetime.date(dr['year'],dr['month'],dr['day']) 
                 + datetime.timedelta(1) )
        dr = {'year':d1.year,'month':d1.month,'day':d1.day,
              'hour':dr['hour']-24}
    return dr

def get_slice_at_hour_at_timestep(variable,year,month,day,hour,
                                  type='ensemble',fc_init=None):
    """Get the cube with the data, given that the specified time
       matches a data timestep."""
    if not is_in_file(variable,year,month,day,hour):
        raise ValueError("Invalid hour - data not in file")
    file_name=hourly_get_file_name(variable,year,month,day,hour,
                                   type=type,fc_init=fc_init)
    if type == 'normal' or type == 'standard.deviation':
        year=1981
        if month==2 and day==29:
            day=28
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
    if type=='ensemble':
        hslice.dim_coords[0].rename('member') # Consistency with 20CR
    return hslice

def get_slice_at_hour(variable,year,month,day,hour,
                      type='ensemble',fc_init=None):
    """Get the cube with the data, interpolating between timesteps
       if necessary."""
    if is_in_file(variable,year,month,day,hour):
        return(get_slice_at_hour_at_timestep(variable,year,
                                             month,day,
                                             hour,type=type,
                                             fc_init=fc_init))
    previous_step=get_previous_field_time(variable,year,month,
                                          day,hour)
    next_step=get_next_field_time(variable,year,month,
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
    s_previous=get_slice_at_hour_at_timestep(variable,
                                             previous_step['year'],
                                             previous_step['month'],
                                             previous_step['day'],
                                             previous_step['hour'],
                                             type=type,
                                             fc_init=fc_init)
    s_next=get_slice_at_hour_at_timestep(variable,
                                         next_step['year'],
                                         next_step['month'],
                                         next_step['day'],
                                         next_step['hour'],
                                         type=type,
                                         fc_init=fc_init)
 
    s_next=iris.cube.CubeList((s_previous,s_next)).merge_cube()
    s_next=s_next.interpolate([('time',dt_current)],iris.analysis.Linear())
    return s_next

