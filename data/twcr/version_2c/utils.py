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
import os.path
import iris
import iris.time
import datetime
import numpy as np
import pandas

def _get_data_dir(version):
    """Return the root directory containing 20CR netCDF files"""
    g="%s/20CR/version_%s/" % (os.environ['SCRATCH'],version)
    return g

def _get_data_file_name(variable,year):
    """Return the name of the file containing data for the
       requested variable, at the specified time, from the
       20CR version."""
    base_dir=_get_data_dir(version)
    name="%s/%04d/%s.nc" % (base_dir,year,variable)
    return name

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

def get_slice_at_hour_at_timestep(variable,year,month,day,hour,version,
                                  type='ensemble'):
    """Get the cube with the data, given that the specified time
       matches a data timestep."""
    if not is_in_file(variable,version,hour):
        raise ValueError("Invalid hour - data not in file")
    file_name=get_data_file_name(variable,year,month,day,hour,
                                 version,type)
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
       raise StandardError("Data not available for %04d-%02d-%02d:%02d" % (year,
                               month,day,hour))

    # Enhance the names and metadata for iris/cartopy
    hslice.coord('latitude').coord_system=coord_s
    hslice.coord('longitude').coord_system=coord_s
    if type=='ensemble':
        hslice.dim_coords[0].rename('member') # Remove spaces in name
    return hslice

def get_slice_at_hour(variable,year,month,day,hour,version,
                      type='ensemble'):
    """Get the cube with the data, interpolating between timesteps
       if necessary."""
    if is_in_file(variable,version,hour):
        return(get_slice_at_hour_at_timestep(variable,year,
                                             month,day,
                                             hour,version,type))
    previous_step=get_previous_field_time(variable,year,month,
                                          day,hour,version)
    next_step=get_next_field_time(variable,year,month,
                                  day,hour,version)
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
                                             version,type)
    s_next=get_slice_at_hour_at_timestep(variable,
                                         next_step['year'],
                                         next_step['month'],
                                         next_step['day'],
                                         next_step['hour'],
                                         version,type)
    s_next=iris.cube.CubeList((s_previous,s_next)).merge_cube()
    s_next=s_next.interpolate([('time',dt_current)],iris.analysis.Linear())
    return s_next

def get_obs_1file(year,month,day,hour,version):
    """Retrieve all the observations for an individual assimilation run."""
    base_dir=get_data_dir(version)
    of_name=get_data_file_name('observations',year,month,day,hour,version)
    if not os.path.isfile(of_name):
        raise IOError("No obs file for given version and date")

    o=pandas.read_fwf(of_name,
                       colspecs=[(0,19),(20,23),(24,25),(26,33),(34,40),(41,46),(47,52),
                                 (53,61),(60,67),(68,75),(76,83),(84,94),(95,100),
                                 (101,106),(107,108),(109,110),(111,112),(113,114),
                                 (115,116),(117,127),(128,138),(139,149),(150,160),
                                 (161,191),(192,206)],          
                       header=None,
                       encoding="ascii",
                       names=['UID','NCEP.Type','Variable','Longitude','Latitude',
                               'Elevation','Model.Elevation','Time.Offset',
                               'Pressure.after.bias.correction',
                               'Pressure.after.vertical.interpolation',
                               'SLP','Bias',
                               'Error.in.surface.pressure',
                               'Error.in.vertically.interpolated.pressure',
                               'Assimilation.indicator',
                               'Usability.check',
                               'QC.flag',
                               'Background.check',
                               'Buddy.check',
                               'Mean.first.guess.pressure.difference',
                               'First.guess.pressure.spread',
                               'Mean.analysis.pressure.difference',
                               'Analysis.pressure.spread',
                               'Name','ID'],
                       converters={'UID': str, 'NCEP.Type': int, 'Variable' : str,
                                   'Longitude': float,'Latitude': float,'Elevation': int,
                                   'Model.Elevation': int, 'Time.Offset': float,
                                   'Pressure.after.bias.correction': float,
                                   'Pressure.after.vertical.interpolation': float,
                                   'SLP': float,'Bias': float,
                                   'Error.in.surface.pressure': float,
                                   'Error.in.vertically.interpolated.pressure': float,
                                   'Assimilation.indicator': int,
                                   'Usability.check': int, 'QC.flag': int,
                                   'Background.check': int, 'Buddy.check': int,
                                   'Mean.first.guess.pressure.difference': float,
                                   'First.guess.pressure.spread': float,
                                   'Mean.analysis.pressure.difference': float,
                                   'Analysis.pressure.spread': float,
                                   'Name': str, 'ID': str},
                       na_values=['NA','*','***','*****','*******','**********',
                                          '-99','9999','-999','9999.99','10000.0',
                                          '-9.99',
                                          '999999999999','9'],
                       comment=None)
    return(o)
 
def get_obs(start,end,version):
    """Retrieve all the observations between start and end"""
    base_dir=get_data_dir(version)
    result=None
    ct=start
    while(ct<end):
        if(int(ct.hour)%6!=0):
           ct=ct+datetime.timedelta(hours=1)
           continue 
        o=get_obs_1file(ct.year,ct.month,ct.day,ct.hour,version)
        dtm=pandas.to_datetime(o.UID.str.slice(0,10),format="%Y%m%d%H")
        o2=o[(dtm>=start) & (dtm<end)]
        if(result is None):
            result=o2
        else:
            result=pandas.concat([result,o2])
        ct=ct+datetime.timedelta(hours=1)
    return(result)
