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

# Utility functions for weather mapping.

import os
import os.path

# Fetch the background data from Natural Earth
def fetch_backgrounds():
    """Fetch plot background data from Natural Earth.

    `Cartopy <http://scitools.org.uk/cartopy/docs/latest/index.html>`_ uses background images from `Natural Earth <http://www.naturalearthdata.com/>`_ for things like continent outlines on world maps - Meteorographica folows it in this. This function downloads some Natural Earth data (continent backgrounds) and modifies it to make ocean regions transparent for easy use in map plots.

    You should only have to run this function once as part of the set-up of this module.

    Requires three utility functions to be available: `wget <https://www.gnu.org/software/wget/>`_, `unzip <http://www.info-zip.org/mans/unzip.html>`_, and `imagemagick convert <https://www.imagemagick.org/script/convert.php>`_. It will create map background files in the directory specified by the CARTOPY_USER_BACKGROUNDS environment variable which should have been set during the installation of `Cartopy <http://scitools.org.uk/cartopy/docs/latest/index.html>`_.

    Raises:
        StandardError: Environment variable 'CARTOPY_USER_BACKGROUNDS' is not set

    |
    """
    
    bgdir=os.getenv('CARTOPY_USER_BACKGROUNDS')
    if bgdir is None:
        raise StandardError("CARTOPY_USER_BACKGROUNDS environment "
                            + "variable is undefined")
    if not os.path.isdir(bgdir):
        os.makedirs(bgdir)
    os.chdir(bgdir)

    if not os.path.isfile("GRAY_50M_SR_W_tpo.png"):
        if not os.path.isfile("GRAY_50M_SR_W.tif"):
            if not os.path.isfile("GRAY_50M_SR_W.zip"):
                os.system("wget http://www.naturalearthdata.com/http//www.naturalearthdata.com/"
                          + "download/50m/raster/GRAY_50M_SR_W.zip")
            os.system("unzip GRAY_50M_SR_W.zip")
        os.system("convert GRAY_50M_SR_W/GRAY_50M_SR_W.tif "
                  + "-transparent '#6a6a6a' "
                  + "GRAY_50M_SR_W_tpo.png")

    if not os.path.isfile("GRAY_LR_SR_W_tpo.png"):
        if not os.path.isfile("GRAY_LR_SR_W.tif"):
            if not os.path.isfile("GRAY_LR_SR_W.zip"):
                os.system("wget http://www.naturalearthdata.com/http//www.naturalearthdata.com/"
                          + "download/10m/raster/GRAY_LR_SR_W.zip")
            os.system("unzip GRAY_LR_SR_W.zip")
        os.system("convert GRAY_LR_SR_W/GRAY_LR_SR_W.tif "
                  + "-transparent '#6a6a6a' "
                  + "GRAY_LR_SR_W_tpo.png")

    if not os.path.isfile("GRAY_HR_SR_W_tpo.png"):
        if not os.path.isfile("GRAY_HR_SR_W.tif"):
            if not os.path.isfile("GRAY_HR_SR_W.zip"):
                os.system("wget http://www.naturalearthdata.com/http//www.naturalearthdata.com/"
                          + "download/10m/raster/GRAY_HR_SR_W.zip")
            os.system("unzip GRAY_HR_SR_W.zip")
        os.system("convert GRAY_HR_SR_W/GRAY_HR_SR_W.tif "
                  + "-transparent '#6a6a6a' "
                  + "GRAY_HR_SR_W_tpo.png")

    idx_txt='''{"__comment__": "JSON file specifying the image to use for a given type/name and resolution. Read in by cartopy.mpl.geoaxes.read_user_background_images.",
  "GreyT": {
    "__comment__": "Grey topography - land only ",
    "__source__": "http://www.naturalearthdata.com/downloads/10m-raster-data/10m-gray-earth/",
    "__projection__": "PlateCarree",
    "low": "GRAY_50M_SR_W_tpo.png",
    "50m": "GRAY_50M_SR_W_tpo.png",
    "med": "GRAY_LR_SR_W_tpo.png",
    "high": "GRAY_HR_SR_W_tpo.png",
    "10m": "GRAY_HR_SR_W_tpo.png"
   }
}'''
    if not os.path.isfile("images.json"):
        jf = open("images.json","w")
        jf.write(idx_txt)
        jf.close


