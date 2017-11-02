# Meteorographica

Python software for weather data handling and plotting (builds on SciTools/Iris).

##  Meteorographica.data

One package for each of several data sources, with `fetch` methods for getting a copy of the data from a remote server to a local filesystem. and `load` methods for loading iris cubes from the fetched data.

1.  Meteorographica.data.twcr - Data from the 20th Century Reanalysis.
2.  Meteorographica.data.mopd - Met Office public data distributed through the informatics lab (MOGREPS-G and MOGREPS-UK).

