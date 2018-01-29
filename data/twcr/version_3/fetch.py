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
The functions in this module fetch 20CR V3 data from NERSC and
store it on $SCRATCH.

It requires scp access to private files
at NERSC - it will only work for Philip.
"""

import os
import subprocess

from . import get_data_file_name

def get_remote_file_name(variable,year,month,version,type='ensemble'):

    remote_dir="pbrohan@dtn02.nersc.gov:/global/cscratch1/sd/pbrohan"

    if (type=='mean'):
        raise IOError('No means stored on NERSC $SCRATCH')

    if (type=='normal'):
        raise IOError('No normals stored on NERSC $SCRATCH')

    if (type=='standard.deviation'):
        raise IOError('No standard.deviations stored on NERSC $SCRATCH')

    remote_dir="%s/20CRv3.final/version_%s" % (remote_dir,version)

    if variable=='observations':
        remote_file="%s/%04d/%02d/observations/" % (remote_dir,
                     year,month)
        return(remote_file) 

    if type=='ensemble':
        remote_file="%s/%04d/%02d/%s.nc4" % (remote_dir,
                     year,month,variable)
        return(remote_file) 

    raise StandardError("Unsupported type %s" % type)        


def fetch_data_for_month(variable,year,month,
                         version,type='ensemble',source=None):
    """Version 3 specific - for version 2 use fetch_data_for_year."""
    
    local_file=get_data_file_name(variable,year,month,day=15,hour=12,
                                        version=version,type=type)

    if ((variable != 'observations') and os.path.isfile(local_file)): 
        # Got this data already
        return

    if not os.path.exists(os.path.dirname(local_file)):
        os.makedirs(os.path.dirname(local_file))

    remote_file=get_remote_file_name(variable,year,month,version,type)

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
