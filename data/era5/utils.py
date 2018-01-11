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
Utility functions for file and variable name mapping for ERA5.

"""

import os

# Names of analysis and forecast variables supported
monolevel_analysis=('prmsl','air.2m','uwnd.10m','vwnd.10m','icec','sst')
monolevel_forecast=('prate')

# ERA5 uses different variable names from 20CR
def translate_for_variable_names(variable):

    if(variable=='prmsl'):
        return 'mslp'
    if(variable=='air.2m'):
        return 't2m'
    if(variable=='uwnd.10m'):
        return 'u10'
    if(variable=='vwnd.10m'):
        return 'v10'
    if(variable=='icec'):
        return 'ci'
    if(variable=='sst'):
        return 'sst'
    if(variable=='prate'):
        return 'tp'
    raise StandardError("Unsupported variable %s" % variable)

# ERA5 uses different file names from 20CR
def translate_for_file_names(variable):

    if(variable=='prmsl'):
        return 'mslp'
    if(variable=='air.2m'):
        return 't2m'
    if(variable=='uwnd.10m'):
        return '10u'
    if(variable=='vwnd.10m'):
        return '10v'
    if(variable=='icec'):
        return 'ci'
    if(variable=='sst'):
        return 'sst'
    if(variable=='prate'):
        return 'tp'
    raise StandardError("Unsupported variable %s" % variable)

# Directory to keep downloaded data in
def get_data_dir():
    scratch=os.getenv('SCRATCH')
    if scratch is None:
        raise StandardError("SCRATCH environment variable is undefined")
    base_file = "%s/ERA5" % scratch
    if os.path.isdir(base_file):
        return base.file
    raise StandardError("Scratch directory %s does not exist")

# File name for data for a given variable and month
def hourly_get_file_name(variable,year,month,day,hour,
                         stream='oper',fc.init=NULL,type='mean') {
    base_dir=get_data_dir()
    if type=='normal':
        file_name<-climatology_get_file_name(variable,month)
        if(file.exists(file.name)) return(file.name)
        stop(sprintf("No local data file %s",file.name))
     
    dir.name<-sprintf("%s/%s/hourly/%04d/%02d/",base.dir,stream,
                        year,month)
    file.name<-sprintf("%s/%s.nc",dir.name,variable)
    if(ERA5.get.variable.group(variable) == 'monolevel.forecast') {
      if(is.null(fc.init)) {
        fc.init<-18
        if(hour>=6 && hour<18) fc.init<-6
      }
      if(fc.init!=6 && fc.init!=18) {
        stop("Forcast initialisation time must be 6 or 18")
      }
      if(fc.init==6 && hour<6 && hour>0) {
        stop("Hour more than 18 hours after forecast initialisation")
      }
      if(fc.init==18 && hour<18 && hour>12) {
        stop("Hour more than 18 hours after forecast initialisation")
      }
      if(hour<fc.init) {
         dte<-ymd(sprintf("%04d-%02d-%02d",year,month,day))-days(1)
         dir.name<-sprintf("%s/%s/hourly/%04d/%02d",base.dir,stream,
                        year(dte),month(dte))
       }
       file.name<-sprintf("%s/%s.%02d.nc",dir.name,variable,fc.init)
    }
    if(file.exists(file.name)) return(file.name)
    stop(sprintf("No local data file %s",file.name))
}
