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

# Handle observations for version 2c

import datetime
import os
import os.path
import subprocess
import zipfile
import pandas
import numpy

from utils import _get_data_dir
from load import _get_previous_field_time
from load import _get_next_field_time

def _observations_remote_file(year):
    return ("http://portal.nersc.gov/project/m958/2c_observations/"+
                 "%04d.zip") % year

def _observations_zip_file(year):
    return "%s/observations/%04d.zip" % (_get_data_dir(),year)

def _observations_file_name(year,month,day,hour,):
    return ("%s/observations/%04d/prepbufrobs_assim_%04d%02d%02d%02d.txt" % 
                            (_get_data_dir(),year,year,month,day,hour))

def fetch_observations(year):
    o_dir= "%s/observations/%04d" % (_get_data_dir(),year)
    if os.path.exists(o_dir):
        if len(os.listdir(o_dir)) >= 1460:
            return
    _download_observations(year)
    _unpack_downloaded_observations(year)

def _download_observations(year):
    remote_file=_observations_remote_file(year)
    local_file=_observations_zip_file(year)
    if os.path.isfile(local_file): 
        return
    if not os.path.exists(os.path.dirname(local_file)):
        os.makedirs(os.path.dirname(local_file))
    cmd="wget -O %s %s" % (local_file,remote_file)
    wg_retvalue=subprocess.call(cmd,shell=True)
    if wg_retvalue!=0:
        os.remove(local_file)
        raise StandardError("Failed to retrieve data")

def _unpack_downloaded_observations(year):
    local_file=_observations_zip_file(year)
    zf=zipfile.ZipFile(local_file)
    zf.extractall("%s/observations/" % _get_data_dir())
    os.remove(local_file)

def load_observations_1file(year,month,day,hour):
    of_name=_observations_file_name(year,month,day,hour)
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

def load_observations(start,end):
    result=None
    ct=start
    while(ct<end):
        if(int(ct.hour)%6!=0):
           ct=ct+datetime.timedelta(hours=1)
           continue 
        o=load_observations_1file(ct.year,ct.month,ct.day,ct.hour)
        dtm=pandas.to_datetime(o.UID.str.slice(0,10),format="%Y%m%d%H")
        o2=o[(dtm>=start) & (dtm<end)]
        if(result is None):
            result=o2
        else:
            result=pandas.concat([result,o2])
        ct=ct+datetime.timedelta(hours=1)
    return(result)

def load_observations_fortime(v_time):
    result=None
    if v_time.hour%6==0:
        result=load_observations_1file(v_time.year,v_time.month,
                                       v_time.day,v_time.hour)
        result['weight']=numpy.repeat(1,len(result.index))
        return result
    prev_time=v_time-datetime.timedelta(hours=v_time.hour%6)
    prev_weight=(6-v_time.hour%6)/6.0
    result=load_observations_1file(prev_time.year,prev_time.month,
                                   prev_time.day,prev_time.hour)
    result['weight']=numpy.repeat(prev_weight,len(result.index))
    next_time=prev_time+datetime.timedelta(hours=6)
    next_weight=1-prev_weight
    result2=load_observations_1file(next_time.year,next_time.month,
                                    next_time.day,next_time.hour)
    result2['weight']=numpy.repeat(next_weight,len(result2.index))
    result=pandas.concat([result,result2])
    return result
