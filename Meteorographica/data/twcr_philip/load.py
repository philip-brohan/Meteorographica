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
20CR data.
"""
import version_2
import version_3
from . import get_version_from_ensda

def get_slice_at_hour(variable,year,month,day,hour,version,
                      type='ensemble'):
    """Get the cube with the data, interpolating between timesteps
       if necessary."""
    vn=get_version_from_ensda(version)
    if vn==2:
        return version_2.get_slice_at_hour(
                              variable,year,month,
                              day,hour,type=type,
                              version=version)
    if vn==3:
        return version_3.get_slice_at_hour(
                              variable,year,month,
                              day,hour,type=type,
                              version=version)
    raise StandardError('Invalid version number %s' % version)

def get_obs_1file(year,month,day,hour,version):
    """Retrieve all the observations for an individual assimilation run"""
    vn=get_version_from_ensda(version)
    if vn==2:
        return version_2.get_obs_1file(year,month,day,hour,version=version)
    if vn==3:
        return version_3.get_obs_1file(year,month,day,hour,version=version)
    raise StandardError('Invalid version number %s' % version)

def get_obs(start,end,version):
    """Retrieve all the observations between start and end"""
    vn=get_version_from_ensda(version)
    if(vn==2):
        return version_2.get_obs(start,end,version)
    if(vn==3):
        return version_3.get_obs(start,end,version)
    raise StandardError('Invalid version number %s' % version)
