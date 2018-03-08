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

# Functions to process and manipulate iris cubes.

import copy

# Control the order of the vector dimensions of a cube, so the 
#  numpy array of data has the expected shape.
def cube_order_dimensions(cube,dims_list):
    """Reshape the data in an :class:`iris.cube.Cube` by re-ordering the dimensions.

    If the cube interface is not doing what I want, and I need to access the internal data array directly, then the exact shape of the array starts to matter, and a [latitude,longitude] array is not the same as a [longitude,latitude] one. This function sets the exact shape of the data array by specifying the order of the dimensions of the cube. Note that it does not modify the input cube, it returns a new one.

    Args:
        cube (:obj:`iris.cube.Cube`): The cube to have its data re-ordered.
        dims_list (:obj:`list` of :obj:`str`): Dimension names in desired order (e.g. "('Latitude','Longitude','member')").

    Returns:
        :obj:`iris.cube.Cube`: A new cube with the dimensions in the specified order.

    Raises:
        StandardError: Names in the dims_list do not match the names of the vector dimensions of the cube.

    |
    """ 

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
                      if (crds[index].long_name==dims_list[dim_i] or
                          crds[index].standard_name==dims_list[dim_i])][0]
        except IndexError:
            raise StandardError("Cube does not have vector dimension %s" %
                                 dims_list[dim_i])
    result=cube.copy()
    result.transpose(new_order=odr)
    return result
