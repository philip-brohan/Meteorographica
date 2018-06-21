# Assemble local copies of some data to be used in Meteorographica examples.
#
# Uses IRData (http://brohan.org/IRData/) to get the data.

import datetime
import iris
import IRData.twcr as twcr
import pickle
import gzip

dte=datetime.datetime(1987,10,16,6)
for var in ('prmsl','uwnd.10m','vwnd.10m','prate'):
    twcr.fetch(var,dte,version='2c')
    cube=twcr.load(var,dte,version='2c')
    fname="20CR2c.%04d%02d%02d%02d.%s.nc" % (
           dte.year,dte.month,dte.day,dte.hour,var)
    #iris.save(cube,fname,netcdf_format='NETCDF4',
    #          zlib=True,complevel=9)
twcr.fetch_observations(dte,version='2c')
obs=twcr.load_observations_fortime(dte,version='2c')
f=gzip.open("20CR2c.%04d%02d%02d%02d.observations.pklz" %
                        (dte.year,dte.month,dte.day,dte.hour), "wb" )
pickle.dump(obs,f)
f.close()
