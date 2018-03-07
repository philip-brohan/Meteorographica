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

# Fetch 20CR V2c data from NERSC and store it on $SCRATCH.

import os
import subprocess

from utils import _get_data_file_name

def _get_remote_file_name(variable,year):
    """Get all data for one variable, for one month, from 20CR archive at NERSC.

    Data wil be stored locally in directory $SCRATCH/20CR, to be retrieved by :func:`load`. If the local file that would be produced already exists, this function does nothing.

    Args:
        variable (:obj:`str`): Variable to fetch (e.g. 'prmsl').
        year (:obj:`int`): Year to get data for.

    Raises:
        StandardError: If variable is not a supported value.
 
    |
    """

    #remote_dir=("http://portal.nersc.gov/pydap/"+
    #            "20C_Reanalysis_version2c_ensemble/")
    remote_dir=("http://portal.nersc.gov/project/20C_Reanalysis/"+
                "20C_Reanalysis_version2c_ensemble/")
    
    if variable=='observations':
        remote_file=("http://portal.nersc.gov/m958/2c_observations/"+
                     "%04d.zip") % year
        return remote_file

    remote_file=None
    if variable=='prmsl':
        remote_file=("%s/analysis/prmsl/prmsl_%04d.nc" % (remote_dir,
                                                                 year))
    if variable=='air.2m':
        remote_file=("%s/first_guess/t2m/t2m_%04d.nc" % (remote_dir,
                                                                 year))
    if variable=='uwnd.10m':
        remote_file=("%s/first_guess/u10m/u10m_%04d.nc" % (remote_dir,
                                                                 year))
    if variable=='vwnd.10m':
        remote_file=("%s/first_guess/v10m/v10m_%04d.nc" % (remote_dir,
                                                                 year))
    if variable=='prate':
        remote_file=("%s/first_guess/prate/prate_%04d.nc" % (remote_dir,
                                                                 year))
    if(remote_file is None):
        raise StandardError("Unsupported variable %s" % variable)
    return(remote_file)

def fetch(variable,year):
    
    local_file=_get_data_file_name(variable,year)

    if os.path.isfile(local_file): 
        # Got this data already
        return

    if not os.path.exists(os.path.dirname(local_file)):
        os.makedirs(os.path.dirname(local_file))

    remote_file=_get_remote_file_name(variable,year)

    cmd="wget -O %s %s" % (local_file,remote_file)
    wg_retvalue=subprocess.call(cmd,shell=True)
    if wg_retvalue!=0:
        raise StandardError("Failed to retrieve data")

