Meteorographica: python code for plotting weathermaps
=====================================================

This code library extends `SciTools <http://scitools.org.uk/>`_ (`Iris <http://scitools.org.uk/iris/docs/latest/index.html>`_ and `Cartopy <http://scitools.org.uk/cartopy/docs/latest/index.html>`_) in providing tools for plotting meteorological data. In particular it supports plotting synoptic charts - maps of instantanious surface weather, and indicating the uncertainties in those charts.

Installation instructions:

.. toctree::
   :maxdepth: 1

   install
 
Modules in the library:

.. toctree::
   :maxdepth: 2
 
   pressure
   wind
   precipitation
   observations
   background

Use of the package is best illustrated by example:

.. toctree::
   :maxdepth: 2
 
   examples/examples

|

Note that this is one person's personal library: I have no resources for support or extension beyond what is necessary for my own research. You are welcome to re-use any part of it (subject to the license, see below), but you would almost certainly be better advised to copy any bits you like and incoporate them into your own codebase than to rely on the stability of this.

The code in this library is licensed under the terms of the `GNU Lesser General Public License <https://www.gnu.org/licenses/lgpl.html>`_. The documentation under the terms of the `Open Government Licence <https://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/>`_.

