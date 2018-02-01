# Meteorographica

Python software for weather data handling and plotting (builds on SciTools/Iris).

This is a personal software library; it builds on SciTools/Iris and is licensed on the same terms, but it does not have the same level of documentation, support, testing, or stability.

You should take probably code from here and incoporate it into your own software, rather than using this library directly.

##  Meteorographica.data

One package for each of several data sources, with `fetch` methods for getting a copy of the data from a remote server to a local filesystem. and `load` methods for loading iris cubes from the fetched data. 

1.  Meteorographica.data.twcr - Data from the 20th Century Reanalysis.
2.  Meteorographica.data.cera20c - Data from the CERA20C Reanalysis.
3.  Meteorographica.data.era5 - Data from the ERA5 Reanalysis.
4.  Meteorographica.data.mopd - Met Office public data distributed through the informatics lab (MOGREPS-G and MOGREPS-UK).

##  Meteorographica.weathermap

Functions for plotting weather maps.

