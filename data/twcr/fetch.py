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
The functions in this module fetch 20CR data from NERSC.

This data is not publicly accessible yet - this will only
work for Philip.

"""
import version_2
import version_3
from . import get_version_from_ensda

def fetch_data_for_month(variable,year,month,version,
                                     type='ensemble'):
    vn=get_version_from_ensda(version)
    if vn==2:
        raise StandardError('Use "fetch_data_for_year" for V2.')
    if vn==3:
        return version_3.fetch_data_for_month(
                              variable,year,month,
                              type=type,
                              version=version)

def fetch_data_for_year(variable,year,month,version,
                                     type='ensemble'):
    vn=get_version_from_ensda(version)
    if vn==2:
        return version_2.fetch_data_for_year(
                              variable,year,
                              type=type,
                              version=version)

    if vn==3:
        return version_3.fetch_data_for_month(
                              variable,year,month,
                              type=type,
                              version=version)
