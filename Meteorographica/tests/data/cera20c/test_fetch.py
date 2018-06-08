import unittest
from mock import patch

import Meteorographica.data.cera20c as cera20c
import ecmwfapi
import os
 
class TestFetch(unittest.TestCase):
 
    def test_fetch_prmsl(self):
        with patch.object(ecmwfapi.ECMWFDataServer, 'retrieve', 
                                return_value=None) as mock_method: 
            cera20c.fetch('prmsl',1969,3)
        mock_method.assert_called_once_with(
                {'stream': 'enda', 
                 'format': 'netcdf',
                 'levtype': 'sfc', 
                 'number': '0/1/2/3/4/5/6/7/8/9',
                 'dataset': 'cera20c',
                 'grid': '1.25/1.25',
                 'expver': '1',
                 'date': '1969-03-01/to/1969-03-31',
                 'class': 'ep',
                 'target': '%s/CERA_20C/hourly/1969/03/prmsl.nc' % \
                             os.getenv('SCRATCH'),
                 'param': 'mslp',
                 'time': '00/03/06/09/12/15/18/21',
                 'type': 'an'})
 
if __name__ == '__main__':
    unittest.main()
