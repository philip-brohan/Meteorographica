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
20CR V3 data.
"""

import os
import os.path
import iris
import iris.time
import datetime
import numpy as np
import pandas
import warnings

# Eliminate incomprehensible warning message
iris.FUTURE.netcdf_promote='True'

# Need to add coordinate system metadata so they work with cartopy
coord_s=iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS)

def get_data_dir(version):
    """Return the root directory containing 20CR netCDF files"""
    g="%s/20CR/version_%s/" % (os.environ['SCRATCH'],version)
    if os.path.isdir(g):
        return g
    g="/project/projectdirs/m958/netCDF.data/20CR_v%s/" % version
    if os.path.isdir(g):
        return g
    raise IOError("No data found for version %s" % version)

def get_data_file_name(variable,year,month,day=None,hour=None,
                       version='4.5.1',type='ensemble'):
    """Return the name of the file containing data for the
       requested variable, at the specified time, from the
       20CR version."""
    base_dir=get_data_dir(version)
    if variable == 'observations':
        if (day is None or hour is None):
            raise StandardError("Observation files names need day and hour")
        if hour%6!=0:
            raise StandardError("Observation files only available every 6 hours")
        name="%s/observations/%04d/%02d/%04d%02d%02d%02d_psobs.txt" % (base_dir,
                  year,month,year,month,day,hour)
        return name    
    if type in ('mean','spread','ensemble','normal',
                   'standard.deviation','first.guess.mean',
                   'first.guess.spread'):
        name="%s/%s" % (base_dir,type)
        if (type != 'normal' and type !='standard.deviation'):
            name="%s/%04d" % (name,year)
        name="%s/%02d" % (name,month)
        name="%s/%s.nc4" % (name,variable)
        return name
    raise StandardError("Unsupported type %s" % type)

def is_in_file(variable,version,hour):
    """Is the variable available for this time?
       Or will it have to be interpolated?"""
    if hour%3==0:
        return True
    return False

def get_previous_field_time(variable,year,month,day,hour,version):
    """Get the latest time, before the given time,
                     for which there is saved data"""
    return {'year':year,'month':month,'day':day,'hour':int(hour/3)*3}

def get_next_field_time(variable,year,month,day,hour,version):
    """Get the earliest time, after the given time,
                     for which there is saved data"""
    dr = {'year':year,'month':month,'day':day,'hour':int(hour/3)*3+3}
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
    ic_time=iris.time.PartialDateTime(
                                   year=year,
                                   month=month,
                                   day=day,
                                   hour=hour)
    fc_time=0
    if hour%6!=0:
        ic_time=iris.time.PartialDateTime(
                                   year=year,
                                   month=month,
                                   day=day,
                                   hour=hour-3)
        fc_time=3

    coord_values={'latitude':lambda cell: 0 < cell < 90}
    ic_constraint=iris.Constraint(coord_values={
                   'initial time': lambda x: x==ic_time})
    fc_constraint=iris.Constraint(coord_values={
            'Forecast offset from initial time': lambda x: x==fc_time})
    try:
        with iris.FUTURE.context(cell_datetime_objects=True):
            with warnings.catch_warnings(): # Iris is v.fussy
                warnings.simplefilter("ignore")
                hslice=iris.load_cube(file_name,
                                  ic_constraint & fc_constraint)
    # This isn't the right error to catch
    except iris.exceptions.ConstraintMismatchError:
       raise StandardError("Data not available for %04d-%02d-%02d:%02d" % (year,
                               month,day,hour))

    # Enhance the names and metadata for iris/cartopy
    hslice.coord('latitude').coord_system=coord_s
    hslice.coord('longitude').coord_system=coord_s
    if type=='ensemble':
        hslice.dim_coords[0].rename('member') # Remove spaces in name
    # Need a validity time dimension for interpolation
    hslice.coord('initial time').rename('time')
    hslice.coord('time').points = (hslice.coord('time').points + 
            hslice.coord('Forecast offset from initial time').points)
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
    of_name=get_data_file_name('observations',year,month,day,hour,version)
    if not os.path.isfile(of_name):
        raise IOError("No obs file for given version and date")

    o=pandas.read_fwf(of_name,
                       colspecs=[(0,19),(20,23),(24,25),(26,33),(34,40),(41,46),
                                 (47,53),(54,61),(62,70),(71,76),(77,133)],
                       usecols=[0,1,2,3,4,5,6,7,8,9,10],
                       header=None,
                       encoding="ISO-8859-1",
                       names=['UID','NCEP.Type','Variable','Longitude','Latitude',
                              'Un1','Un2','Un3','Un4','Un5','Name'],
                       converters={'UID': str, 'NCEP.Type': int, 'Variable' : str,
                                   'Longitude': float, 'Latitude': float, 'Un1': int,
                                   'Un2': float, 'Un3': float, 'Un4': float,
                                   'Un5': float, 'Name': str},
                       na_values=['NA','*','***','*****','*******','**********',
                                          '-99','9999','-999','9999.99','10000.0',
                                          '-9.99','999999999999999999999999999999',
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
