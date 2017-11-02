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
The functions in this module fetch 20CR data from NERSC and
store it on $SCRATCH.

It requires scp access to private files
at NERSC - it will only work for Philip.
"""

import os
import subprocess

from . import get_data_file_name

def get_remote_file_name(variable,year,month,version,type,source=None):

    if (source is None):
        if (version[0]=='4'):
            source='scratch'
        elif (version=='3.5.1' or version=='3.2.1'):
            source='released'
        elif (version=='3.5.4'):
            source='scratch'
        else:
            source='m958'

    if (source=='released'):
        return get_remote_file_name_released(variable,year,month,
                                             version,type)
    if (source=='scratch'):
        return get_remote_file_name_scratch(variable,year,month,
                                            version,type)
    if (source=='m958'):
        return get_remote_file_name_m958(variable,year,month,
                                             version,type)
    raise StandardError("Unsupported source %s" % source)

def get_remote_file_name_m958(variable,year,month,version,type):

    if (variable=='observations'):
        remote_dir="pbrohan@dtn02.nersc.gov:/project/projectdirs/"+\
                   "m958/netCDF.data/20CR_v%s/" % version
        remote_file="%s/observations/%04d" % (remote_dir,year)
        return(remote_file) 

    remote_file=None
    if (type=='mean'):
        remote_dir="pbrohan@dtn02.nersc.gov:/project/projectdirs/"+\
                   "m958/netCDF.data/20CR_v%s/" % version
        remote_file="%s/hourly/%s/%s.%04d.nc" % (remote_dir,
                     variable,variable,year)

    if (type=='spread'):
        remote_dir="pbrohan@dtn02.nersc.gov:/project/projectdirs/"+\
                   "m958/netCDF.data/20CR_v%s/" % version
        remote_file="%s/hourly/%s/%s.%04d.spread.nc" % (remote_dir,
                     variable,variable,year)

    if (type=='first.guess.mean'):
        remote_dir="pbrohan@dtn02.nersc.gov:/project/projectdirs/"+\
                   "m958/netCDF.data/20CR_v%s/" % version
        remote_file="%s/first.guess.hourly/%s/%s.%04d.nc" % (remote_dir,
                     variable,variable,year)

    if (type=='first.guess.spread'):
        remote_dir="pbrohan@dtn02.nersc.gov:/project/projectdirs/"+\
                   "m958/netCDF.data/20CR_v%s/" % version
        remote_file="%s/first.guess.hourly/%s/%s.%04d.spread.nc" % (remote_dir,
                     variable,variable,year)

    if (type=='normal'):
        remote_dir="pbrohan@dtn02.nersc.gov:/project/projectdirs/"+\
                   "m958/netCDF.data/20CR_v%s/" % version
        remote_file="%s/hourly/normals/%s.%04d.nc" % (remote_dir,
                     variable,variable,year)

    if (type=='standard.deviation'):
        remote_dir="pbrohan@dtn02.nersc.gov:/project/projectdirs/"+\
                   "m958/netCDF.data/20CR_v%s/" % version
        remote_file="%s/hourly/standard.deviations/%s.%04d.nc" % (remote_dir,
                     variable,variable,year)

    if (remote_file is None):
        raise StandardError("Unsupported type %s" % type)
    return(remote_file)

def get_remote_file_name_scratch(variable,year,month,version,type):

    remote_dir="pbrohan@dtn02.nersc.gov:/global/cscratch1/sd/pbrohan"

    if (type=='mean'):
        raise IOError('No means stored on NERSC $SCRATCH')

    if (type=='normal'):
        raise IOError('No normals stored on NERSC $SCRATCH')

    if (type=='standard.deviation'):
        raise IOError('No standard.deviations stored on NERSC $SCRATCH')

    if(version[0]=='4'):
        remote_dir="%s/20CRv3.final/version_%s" % (remote_dir,version)
      
        if variable=='observations':
            remote_file="%s/observations/%04d/%02d/" % (remote_dir,
                         year,month)
            return(remote_file) 

        if type=='ensemble':
            remote_file="%s/hourly/%04d/%02d/%s.nc" % (remote_dir,
                         year,month,variable)
            return(remote_file) 

        if type=='first.guess.mean':
            remote_file="%s/first.guess.hourly/%04d/%02d/%s.nc" % (remote_dir,
                         year,month,variable)
            return(remote_file) 

        if type=='first.guess.spread':
            remote_file="%s/first.guess.hourly/%04d/%02d/%s.spread.nc" % (remote_dir,
                         year,month,variable)
            return(remote_file) 

        raise StandardError("Unsupported type %s" % type)
    else:
        remote_dir="%s/20CRv2.final/version_%s" % (remote_dir,version)
      
        if variable=='observations':
            remote_file="%s/observations/%04d/" % (remote_dir,
                         year)
            return(remote_file) 

        if type=='ensemble':
            remote_file="%s/ensembles/hourly/%s/%s.%04d.nc" % (remote_dir,
                         variable,variable,year)
            return(remote_file)
 
        if type=='first.guess.mean':
            remote_file="%s/first.guess.hourly/%s/%s.%04d.nc" % (remote_dir,
                         variable,variable,year)
            return(remote_file) 
 
        if type=='first.guess.spread':
            remote_file="%s/first.guess.hourly/%s/%s.%04d.spread.nc" % (remote_dir,
                         variable,variable,year)
            return(remote_file) 

        raise StandardError("Unsupported type %s" % type)
        

def get_remote_file_name_released(variable,year,month,version,type):
    """Location of the official v2 & v2c data at NERSC"""

    if(variable=='observations' or type=='mean' or type=='spread' or
                 type=='normal' or type=='standard.deviation'):
        return get_remote_file_name_m958(variable,year,month,
                                         version,type)

    remote_file=None
    if type=='ensemble':
       remote_dir="pbrohan@dtn02.nersc.gov:/project/projectdirs/"+\
                  "20C_Reanalysis/www/20C_Reanalysis_ensemble"
       if version=='3.5.1':
          remote_dir="pbrohan@dtn02.nersc.gov:/project/projectdirs/"+\
                  "20C_Reanalysis/www/20C_Reanalysis_version2c_ensemble"
       if variable=='prmsl':
          remote_file="%s/analysis/%s/%s_%04d.nc" % (remote_dir,
                        'prmsl','prmsl',year)
       if variable=='air.2m':
          remote_file="%s/analysis/%s/%s_%04d.nc" % (remote_dir,
                        't9950','t9950',year)
       if variable=='uwnd.10m':
          remote_file="%s/first_guess/%s/%s_%04d.nc" % (remote_dir,
                        'u10m','u10m',year)
       if variable=='vwnd.10m':
          remote_file="%s/first_guess/%s/%s_%04d.nc" % (remote_dir,
                        'v10m','v10m',year)
       if variable=='prate':
          remote_file="%s/first_guess/%s/%s_%04d.nc" % (remote_dir,
                        'prate','prate',year)
    if(remote_file is None):
        raise StandardError("Unsupported ensemble variable %s" % variable)
    return(remote_file)


def fetch_data_for_month(variable,year,month,
                         version,type='ensemble',source=None):
    """Version 3 specific - for version 2 use fetch_data_for_year."""
    
    if(version[0]!='4' and month is not None):
        raise StandardError("Use 'fetch_data_for_year' for version 2")
    if(month is None):
        month=1   # Arbitrary, v2 data is by year, so any month would do
    # Day and hour also set arbtrarily to 1 and 6
    local_file=get_data_file_name(variable,year,month,1,6,version,type)

    if ((variable != 'observations') and os.path.isfile(local_file)): 
        # Got this data already
        return

    if not os.path.exists(os.path.dirname(local_file)):
        os.makedirs(os.path.dirname(local_file))

    remote_file=get_remote_file_name(variable,year,month,version,type,source)

    if(variable=='observations'):
        # Multiple files - use rsync
        local_file=os.path.dirname(local_file)
        cmd="rsync -Lr %s/ %s" % (remote_file,local_file)
        #print(cmd)
        scp_retvalue=subprocess.call(cmd,shell=True) # Why need shell=True?
        if scp_retvalue==3:
            raise StandardError("Remote data not available")
        if scp_retvalue!=0:
            raise StandardError("Failed to retrieve data")
        
    else:
        # Single file - use scp
        cmd="scp %s %s" % (remote_file,local_file)
        #print(cmd)
        scp_retvalue=subprocess.call(cmd,shell=True)
        if scp_retvalue==6:
            raise StandardError("Remote data not available")
        if scp_retvalue!=0:
            raise StandardError("Failed to retrieve data")

def fetch_data_for_year(variable,year,
                         version,type='ensemble',source=None):
    """Version 2 series specific - for version 3 use fetch_data_for_month."""
    if(version[0]=='4'):
        raise StandardError("Use 'fetch_data_for_month' for version 3")
    
    return fetch_data_for_month(variable,year,None,
                         version,type,source)
