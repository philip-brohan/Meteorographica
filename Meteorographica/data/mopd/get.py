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
The functions in this module access Met Office public data from the
 informatics lab store on AWS. Uses $SCRATCH as a file cache.

See http://data.informaticslab.co.uk/.
"""

import os
import datetime
import iris
import iris.time
import re

# Eliminate incomprehensible warning message
iris.FUTURE.netcdf_promote='True'

# Map 20CR names to file variable names
Names={'mogreps-g': {
                     'prmsl'    : 'air_pressure_at_sea_level',
                     'air.2m'   : 'air_temperature_0',
                     'prate'    : 'stratiform_rainfall_rate',
                     'uwnd.10m' : 'x_wind_0',
                     'vwnd.10m' : 'y_wind_0'
                    },
       'mogreps-uk': {
                     'prmsl'    : 'air_pressure_at_sea_level',
                     'air.2m'   : 'air_temperature_1',
                     # No precip variable - use sum of rain and snow
                     'rain'     : 'stratiform_rainfall_rate',
                     'snow'     : 'stratiform_snowfall_rate',
                     'uwnd.10m' : 'x_wind_0',
                     'vwnd.10m' : 'y_wind_0'
                    }
}

def load(dataset_name, variable, 
         year, month, day, hour,
         realization, forecast_period,
         auto_fetch=True):
    """Load a field from the InformaticsLab MOGREPS data

       year, month, day, hour is the validity time of the field

       'hour' and 'forecast_period are real variables, not
       integers - will interpolate as necessary.

       'variable' uses the 20CR naming scheme: 'air.2m', 'prmsl',
          'prate', 'uwnd.10m', ...

       If 'auto_fetch' is True, fetch files from AWS as needed, if False,
        throw an exception if they are not already on local disc"""

def datetime_to_float(dataset_name,dt):
    """I'm having trouble with iris's date-selection methods.
       So take advantage of the fact that all the MOGREPS nc files
       have time stored as 'hours since 1970-01-01' and do
       my own conversion."""
    epoch = datetime.datetime.utcfromtimestamp(0)
    result = (dt - epoch).total_seconds()/3600
    # That should be 'hours since epoch'
    return result

def load_simple(dataset_name, variable, 
                      year, month, day, hour,
                      realization, forecast_period,
                      auto_fetch=False):
    """Load a field in the simple case where no interpolation
        is necessary - where the data at the given validity time and
        forecast period is on disc."""
    ihour=int(hour)
    iminute=int((hour%1)*60)
    vdate=datetime.datetime(year,month,day,ihour,iminute)
    fdate=get_forecast_date_from_validity_date(dataset_name,vdate,forecast_period)
    # Get the file with the data in
    if not is_file_for(dataset_name,fdate.year,fdate.month,fdate.day,
                       fdate.hour,realization,forecast_period):
        raise StandardError("Bad date for load_simple, data not on disc")
    file_name=make_local_file_name(dataset_name, fdate.year, fdate.month, 
                                   fdate.day, fdate.hour,
                                   realization, forecast_period)
    # Check file containing data on disc
    if not os.path.isfile(file_name):
        if auto_fetch:
            fetch_data(dataset_name,fdate.year,fdate.month,fdate.day,
                       fdate.hour,realization,forecast_period)
        else:
            raise StandardError("No Data for %s, realisation %d, forecast %d" %
                            (vdate, realization, forecast_period) + ' on disc.')
    # Get the field from the file - want one within 2 minutes
    hslice=load_specific(dataset_name,variable,file_name,
                         year,month,day,ihour,iminute)
    return hslice
     
def convert_variable_name(dataset_name,variable):
    """Get variable name in the data files from 20CR name."""
    dataset_name=validate_dataset_name(dataset_name)
    variable=variable.lower()
    if variable in Names[dataset_name]:
        return Names[dataset_name][variable]
    raise StandardError("No variable %s, in dataset %s" %
                            (variable, dataset_name))

def get_forecast_date_from_validity_date(dataset_name,vdate,forecast_period):
    """vdate is a datetime, forecast_period is in hours"""
    if forecast_period%1 != 0:
        forecast_period=int(forecast_period)+1
    fdate=vdate-datetime.timedelta(hours=forecast_period)
    if(dataset_name=='mogreps-g'):
        if(forecast_period < 3 or forecast_period > 174):
           raise StandardError("Forecast_period outside mogreps-g range of 3-174")
        if(fdate.hour%3 != 0):
           fdate=fdate-datetime.timedelta(hours=fdate.hour%3)
        return fdate
    if(dataset_name=='mogreps-uk'):
        if(forecast_period < 3 or forecast_period > 6):
           raise StandardError("Forecast_period outside mogreps-uk range of 3-36")
        if(fdate.hour%3 != 0):
           fdate=fdate+datetime.timedelta(hours=fdate.hour%3)
        return fdate
    raise StandardError("Unsupported dataset %s. " % dataset_name +
                        "Must be 'mogreps-g or mogreps-uk")

def is_single_field(dataset_name, variable, 
                    year, month, day, hour,
                    realization, forecast_period):
    """True if data requested is in one file - false if interpolation
       from multiple fields needed."""
    dataset_name=validate_dataset_name(dataset_name)
    if(validated_name == 'mogreps-g'):
        if(hour%1==0 and forecast_period%1==0):
            return True
        return False
    if(validated_name == 'mogreps-uk'):
        if(hour%1==0 and forecast_period%1==0):
            return True
        return False
    raise StandardError("Unsupported dataset %s. " % dataset_name)

def validate_dataset_name(dataset_name):
    validated_name = dataset_name.lower()
    if(validated_name != 'mogreps-g' and
       validated_name != 'mogreps-uk'):
        raise StandardError("Unsupported dataset %s. " % dataset_name +
                            "Must be 'mogreps-g or mogreps-uk")
    return validated_name

def is_file_for(dataset_name, year, month, day, hour, realization, forecast_period):
    """Is there a dump file for this set of data?"""
    dataset_name = validate_dataset_name(dataset_name)
    if dataset_name == 'mogreps-g':
        if hour%6 != 0 or hour < 0 or hour > 18:
            return False
        if realization < 0 or realization > 11:
            return False
        if (forecast_period%3 != 0 or forecast_period < 3 or
                                      forecast_period > 174):
            return False
        return True
    if dataset_name == 'mogreps-uk':
        if hour%6 != 3 or hour < 3 or hour > 21:
            return False
        if realization < 0 or realization > 22:
            return False
        if (forecast_period%3 != 0 or forecast_period < 3 or 
                                      forecast_period > 36):
            return False
        return True
    raise StandardError("Unsupported dataset %s. " % dataset_name +
                        "Must be mogreps-g or mogreps-uk")

def make_local_file_name(dataset_name, year, month, day, hour, realization, forecast_period):
    dataset_name = validate_dataset_name(dataset_name)
    template_string = "{}/{}/{:04d}/{:02d}/{:02d}/{:02d}/"
    if os.getenv('SCRATCH') is None:
        raise StandardError("SCRATCH environment variable is not defined")
    file_name = template_string.format(os.environ['SCRATCH'],dataset_name,
                                       year, month, day, hour)
    template_string = "prods_op_{}_{:04d}{:02d}{:02d}_{:02d}_{:02d}_{:03d}.nc"
    file_name = file_name + template_string.format(dataset_name, 
                                                   year, month, day, hour,
                                                   realization, forecast_period)
    return file_name

def make_remote_url(dataset_name, year, month, day, hour, realization, forecast_period):
    dataset_name = validate_dataset_name(dataset_name)
    template_string = "prods_op_{}_{:02d}{:02d}{:02d}_{:02d}_{:02d}_{:03d}.nc"
    file_name = template_string.format(dataset_name, year, month, day, hour,
                                       realization, forecast_period)
    url = "https://s3.eu-west-2.amazonaws.com/" + dataset_name + "/" + file_name
    return url

def fetch_data(dataset_name, year, month, day, hour, realization, forecast_period):
    dataset_name = validate_dataset_name(dataset_name)
    if not is_file_for(dataset_name, year, month, day, hour,
                       realization, forecast_period):
        raise StandardError("No data file at hour %d, realisation %d, forecast %d" %
                            (hour, realization, forecast_period))
    local_file_name = make_local_file_name(dataset_name, year, month, day, hour,
                                           realization, forecast_period)
    if os.path.isfile(local_file_name):
        return('Already fetched') # Already fetched
    local_dir = os.path.dirname(local_file_name)
    if not os.path.isdir(local_dir):
        os.makedirs(local_dir)
    remote_url = make_remote_url(dataset_name, year, month, day, hour,
                                  realization, forecast_period)
    # urllib.urlretrieve corrupted the file for some reason
    # so use wget - I like the progress bar anyway.
    os.system("wget -P %s %s" % (os.path.dirname(local_file_name),
                                 remote_url))

def load_specific(dataset_name, variable, file_name, 
                  year, month, day, hour, minute=0):
    """Because of the irregular structure of the netCDF files,
       and the peculiarity of iris, loading is fiddly and requires 
       variable-specific code."""
    vdate=datetime.datetime(year,month,day,hour,minute)
    if dataset_name == 'mogreps-g':
        if variable=='prmsl':
            if re.search('03.nc',file_name)!=None: # 3-hour data includes multiple times
                time_constraint=iris.Constraint(time=datetime_to_float('mogreps-g',vdate))
                variable_constraint=iris.Constraint(name='air_pressure_at_sea_level')
                hslice=iris.load_cube(file_name,
                              time_constraint & variable_constraint)
                return hslice
            else:
                variable_constraint=iris.Constraint(name='air_pressure_at_sea_level')
                hslice=iris.load_cube(file_name,variable_constraint)
                return hslice    
        if variable=='air.2m':
            variable_constraint=iris.Constraint(name='air_temperature')
            hslice=iris.load(file_name,variable_constraint)
            return hslice[3]
        if variable=='uwnd.10m':
            variable_constraint=iris.Constraint(name='x_wind')
            hslice=iris.load(file_name,variable_constraint)
            return hslice[2]
        if variable=='vwnd.10m':
            variable_constraint=iris.Constraint(name='y_wind')
            hslice=iris.load(file_name,variable_constraint)
            return hslice[2]
        if variable=='prate':
            variable_constraint=iris.Constraint(name='stratiform_rainfall_amount')
            h1=iris.load_cube(file_name,variable_constraint)
            variable_constraint=iris.Constraint(name='stratiform_snowfall_amount')
            h2=iris.load_cube(file_name,variable_constraint)
            return iris.analysis.maths.add(h1,h2)
        raise StandardError("Unsupported variable %s. " % variable)
    if dataset_name == 'mogreps-uk':
        if variable=='prmsl':
            time_constraint=iris.Constraint(time=datetime_to_float('mogreps-uk',vdate))
            variable_constraint=iris.Constraint(name='air_pressure_at_sea_level')
            hslice=iris.load_cube(file_name,
                          time_constraint & variable_constraint)
            return hslice
        if variable=='air.2m':
            time_constraint=iris.Constraint(time=datetime_to_float('mogreps-uk',vdate))
            variable_constraint=iris.Constraint(name='air_temperature')
            hslice=iris.load(file_name,
                                  time_constraint & variable_constraint)
            return hslice[3]
        if variable=='uwnd.10m':
            time_constraint=iris.Constraint(time=datetime_to_float('mogreps-uk',vdate))
            variable_constraint=iris.Constraint(name='x_wind')
            hslice=iris.load(file_name,
                                  time_constraint & variable_constraint)
            return hslice[2]
        if variable=='vwnd.10m':
            time_constraint=iris.Constraint(time=datetime_to_float('mogreps-uk',vdate))
            variable_constraint=iris.Constraint(name='y_wind')
            hslice=iris.load(file_name,
                                  time_constraint & variable_constraint)
            return hslice[2]
        if variable=='prate':
            time_constraint=iris.Constraint(time=datetime_to_float('mogreps-uk',vdate))
            variable_constraint=iris.Constraint(name='stratiform_rainfall_rate')
            h1=iris.load_cube(file_name,time_constraint & variable_constraint)
            variable_constraint=iris.Constraint(name='stratiform_snowfall_rate')
            h2=iris.load_cube(file_name,time_constraint & variable_constraint)
            return iris.analysis.maths.add(h1,h2)
        raise StandardError("Unsupported variable %s. " % variable)
    raise StandardError("Unsupported dataset %s. " % dataset_name +
                        "Must be mogreps-g or mogreps-uk")
    
