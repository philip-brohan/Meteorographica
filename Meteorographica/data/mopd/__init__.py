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
A package for handling data from the MET Office public datasets (AWS).
(Currently that's MOGREPS-UK and MOGREPS-G).

Downloads data to a local filesystem ($SCRATCH) and supports access by
20CR variable name.

See http://data.informaticslab.co.uk/.

"""

from get import *
