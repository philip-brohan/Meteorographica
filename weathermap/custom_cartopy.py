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
Custom cartopy stuff.        .

"""
from __future__ import (absolute_import, division, print_function)

import cartopy.mpl.geoaxes

import collections
import contextlib
import warnings
import weakref

import matplotlib as mpl
import matplotlib.artist
import matplotlib.axes
from matplotlib.image import imread
import matplotlib.transforms as mtransforms
import matplotlib.patches as mpatches
import matplotlib.path as mpath
import matplotlib.ticker as mticker
import numpy as np
import numpy.ma as ma
import shapely.geometry as sgeom

from cartopy import config
import cartopy.crs as ccrs
import cartopy.feature
import cartopy.img_transform
from cartopy.mpl.clip_path import clip_path
import cartopy.mpl.feature_artist as feature_artist
import cartopy.mpl.patch as cpatch
from cartopy.mpl.slippy_image_artist import SlippyImageArtist
from cartopy.vector_transform import vector_scalar_to_grid

_USER_BG_IMGS=cartopy.mpl.geoaxes._USER_BG_IMGS

# Fix the geoaxes.background_img call to allow user specification
#  of the axeis aspect.
def background_img(self, name='ne_shaded', resolution='low', extent=None,
                   cache=False, aspect='equal'):
    """
    Adds a background image to the map, from a selection of pre-prepared
    images held in a directory specified by the CARTOPY_USER_BACKGROUNDS
    environment variable. That directory is checked with
    func:`self.read_user_background_images` and needs to contain a JSON
    file which defines for the image metadata.

    Kwargs:

        * name - the name of the image to read according to the contents
                 of the JSON file. A typical file might have, for instance:
                 'ne_shaded' : Natural Earth Shaded Relief
                 'ne_grey' : Natural Earth Grey Earth

        * resolution - the resolution of the image to read, according to
                       the contents of the JSON file. A typical file might
                       have the following for each name of the image:
                       'low', 'med', 'high', 'vhigh', 'full'.

        * extent - using a high resolution background image, zoomed into
                   a small area, will take a very long time to render as
                   the image is prepared globally, even though only a small
                   area is used. Adding the extent will only render a
                   particular geographic region. Specified as
                   [longitude start, longitude end,
                    latitude start, latitude end].

                   e.g. [-11, 3, 48, 60] for the UK
                   or [167.0, 193.0, 47.0, 68.0] to cross the date line.

        * cache - logical flag as to whether or not to cache the loaded
                  images into memory. The images are stored before the
                  extent is used.
    """
    # read in the user's background image directory:
    if len(_USER_BG_IMGS) == 0:
        self.read_user_background_images()
    import os
    bgdir = os.getenv('CARTOPY_USER_BACKGROUNDS')
    if bgdir is None:
        bgdir = os.path.join(config["repo_data_dir"],
                             'raster', 'natural_earth')
    # now get the filename we want to use:
    try:
        fname = _USER_BG_IMGS[name][resolution]
    except KeyError:
        msg = ('Image "{}" and resolution "{}" are not present in '
               'the user background image metadata in directory "{}"')
        raise ValueError(msg.format(name, resolution, bgdir))
    # Now obtain the image data from file or cache:
    fpath = os.path.join(bgdir, fname)
    if cache:
        if fname in _BACKG_IMG_CACHE:
            img = _BACKG_IMG_CACHE[fname]
        else:
            img = imread(fpath)
            _BACKG_IMG_CACHE[fname] = img
    else:
        img = imread(fpath)
    if len(img.shape) == 2:
        # greyscale images are only 2-dimensional, so need replicating
        # to 3 colour channels:
        img = np.repeat(img[:, :, np.newaxis], 3, axis=2)
    # now get the projection from the metadata:
    if _USER_BG_IMGS[name]['__projection__'] == 'PlateCarree':
        # currently only PlateCarree is defined:
        source_proj = ccrs.PlateCarree()
    else:
        raise NotImplementedError('Background image projection undefined')

    if extent is None:
        # not specifying an extent, so return all of it:
        return self.imshow(img, origin='upper',
                           transform=source_proj,
                           extent=[-180, 180, -90, 90],aspect=aspect)
    else:
        # return only a subset of the image:
        # set up coordinate arrays:
        d_lat = 180.0 / img.shape[0]
        d_lon = 360.0 / img.shape[1]
        # latitude starts at 90N for this image:
        lat_pts = (np.arange(img.shape[0]) * -d_lat - (d_lat / 2.0)) + 90.0
        lon_pts = (np.arange(img.shape[1]) * d_lon + (d_lon / 2.0)) - 180.0

        # which points are in range:
        lat_in_range = np.logical_and(lat_pts >= extent[2],
                                      lat_pts <= extent[3])
        if extent[0] < 180 and extent[1] > 180:
            # we have a region crossing the dateline
            # this is the westerly side of the input image:
            lon_in_range1 = np.logical_and(lon_pts >= extent[0],
                                           lon_pts <= 180.0)
            img_subset1 = img[lat_in_range, :, :][:, lon_in_range1, :]
            # and the eastward half:
            lon_in_range2 = lon_pts + 360. <= extent[1]
            img_subset2 = img[lat_in_range, :, :][:, lon_in_range2, :]
            # now join them up:
            img_subset = np.concatenate((img_subset1, img_subset2), axis=1)
            # now define the extent for output that matches those points:
            ret_extent = [lon_pts[lon_in_range1][0] - d_lon / 2.0,
                          lon_pts[lon_in_range2][-1] + d_lon / 2.0 + 360,
                          lat_pts[lat_in_range][-1] - d_lat / 2.0,
                          lat_pts[lat_in_range][0] + d_lat / 2.0]
        else:
            # not crossing the dateline, so just find the region:
            lon_in_range = np.logical_and(lon_pts >= extent[0],
                                          lon_pts <= extent[1])
            img_subset = img[lat_in_range, :, :][:, lon_in_range, :]
            # now define the extent for output that matches those points:
            ret_extent = [lon_pts[lon_in_range][0] - d_lon / 2.0,
                          lon_pts[lon_in_range][-1] + d_lon / 2.0,
                          lat_pts[lat_in_range][-1] - d_lat / 2.0,
                          lat_pts[lat_in_range][0] + d_lat / 2.0]

        return self.imshow(img_subset, origin='upper',
                           transform=source_proj,
                           extent=ret_extent,aspect=aspect)
