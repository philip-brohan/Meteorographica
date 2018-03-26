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

# Handle observations for version 3-preliminary

import datetime
import os
import os.path
import subprocess
import pandas
import getpass

from utils import _get_data_dir

def _observations_remote_file(year,month,version):
    return (("pbrohan@dtn02.nersc.gov:/global/cscratch1/sd/pbrohan/"+
            "20CRv3.final/version_%s/%04d/%02d/observations/") %
             (version,year,month))

def _observations_file_name(year,month,day,hour,version):
    return ("%s/observations/%04d/%04d%02d%02d%02d_psobs.txt" % 
                            (_get_data_dir(version),year,year,month,day,hour))

def fetch_observations(year,month,version='4.5.1'):

    #V3 data not yet publically available
    if getpass.getuser() not in ('hadpb','philip','brohanp'):
        raise StandardError('Unsupported user: V3 fetch only works for Philip')

    o_dir= "%s/observations/%04d" % (_get_data_dir(version),year)
    if os.path.exists(o_dir):
        if len(os.listdir(o_dir)) >= 1460:
            return
    else:
        os.makedirs(o_dir)

    # Multiple files, use rsync
    r_dir=_observations_remote_file(year,month,version)
    cmd="rsync -Lr %s/ %s" % (r_dir,o_dir)
    scp_retvalue=subprocess.call(cmd,shell=True) # Why need shell=True?
    if scp_retvalue==3:
        raise StandardError("Remote data not available")
    if scp_retvalue!=0:
        raise StandardError("Failed to retrieve data")

def load_observations_1file(year,month,day,hour,version):
    """Retrieve all the observations for an individual assimilation run."""
    of_name=_observations_file_name(year,month,day,hour,version)
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



def load_observations(start,end,version):
    result=None
    ct=start
    while(ct<end):
        if(int(ct.hour)%6!=0):
           ct=ct+datetime.timedelta(hours=1)
           continue 
        o=load_observations_1file(ct.year,ct.month,ct.day,ct.hour,version)
        dtm=pandas.to_datetime(o.UID.str.slice(0,10),format="%Y%m%d%H")
        o2=o[(dtm>=start) & (dtm<end)]
        if(result is None):
            result=o2
        else:
            result=pandas.concat([result,o2])
        ct=ct+datetime.timedelta(hours=1)
    return(result)
