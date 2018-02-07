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
Functions to process and manipulate iris cubes.

"""

import copy

# Control the order of the vector dimensions of a cube, so the 
#  numpy array of data has the expected shape.
def cube_order_dimensions(cube,dims_list):
    crds2=cube.coords()
    crds=copy.deepcopy(crds2)
    # Keep only the vector dimensions
    for crdi in range(0,len(crds2)):
        if len(crds2[crdi].points)==1: crds.remove(crds2[crdi])
    if len(crds)!=len(dims_list):
        raise StandardError("Cube has %d vector dimensions and %d were specified" %
                             (len(crds),len(dims_list)))
    odr=range(0,len(dims_list))
    for dim_i in range(0,len(dims_list)):
        try:
            odr[dim_i]=[index for index in range(len(crds)) 
                      if crds[index].long_name==dims_list[dim_i]][0]
        except IndexError:
            raise StandardError("Cube does not have vector dimension %s" %
                                 dims_list[dim_i])
    result=cube.copy()
    result.transpose(new_order=odr)
    return result
