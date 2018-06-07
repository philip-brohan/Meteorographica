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

# Fetch 20CR V3-preliminary data from NERSC and store it on $SCRATCH.

import os
import subprocess
import getpass

from utils import _get_data_file_name

def _get_remote_file_name(variable,year,month,version='4.5.1'):
    """Get all data for one variable, for one month, from Philip's SCRATCH directory at NERSC.

    Data wil be stored locally in directory $SCRATCH/20CR, to be retrieved by :func:`load`. If the local file that would be produced already exists, this function does nothing.

    Args:
        variable (:obj:`str`): Variable to fetch (e.g. 'prmsl').
        year (:obj:`int`): Year to get data for.

    Raises:
        StandardError: If variable is not a supported value.
 
    |
    """

    remote_dir=("pbrohan@dtn02.nersc.gov:/global/cscratch1/sd/pbrohan/"+
                "20CRv3.final/version_%s") % version
    
    if variable=='observations':
        remote_file="%s/%04d/%02d/observations/" % (remote_dir,
                     year,month)
        return(remote_file) 

    remote_file="%s/%04d/%02d/%s.nc4" % (remote_dir,
                 year,month,variable)
    return(remote_file) 


def fetch(variable,year,month,version='4.5.1'):

    #V3 data not yet publically available
    if getpass.getuser() not in ('hadpb','philip','brohanp'):
        raise StandardError('Unsupported user: V3 fetch only works for Philip')
    
    local_file=_get_data_file_name(variable,
                                   year,month,
                                   version=version)

    if ((variable != 'observations') and os.path.isfile(local_file)): 
        # Got this data already
        return

    if not os.path.exists(os.path.dirname(local_file)):
        os.makedirs(os.path.dirname(local_file))

    remote_file=_get_remote_file_name(variable,year,month,version)

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

