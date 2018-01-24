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
Test cases for Meteorographica.data.era5.

"""

import os
import unittest
from Meteorographica.data import era5
 
class TestUM(unittest.TestCase):
 
    def setUp(self):
        pass
 
    def test_translate_for_variable_names(self):
        self.assertEqual(era5.translate_for_variable_names('prmsl'),
                         'msl')
        self.assertEqual(era5.translate_for_variable_names('prate'),
                         'tp')
        self.assertEqual(era5.translate_for_variable_names('uwnd.10m'),
                         'u10')
        with self.assertRaises(StandardError) as cm:
            era5.translate_for_variable_names('mslp')
        self.assertIn('Unsupported variable mslp',
                      cm.exception)

    def test_translate_for_file_names(self):
        self.assertEqual(era5.translate_for_file_names('prmsl'),
                         'msl')
        self.assertEqual(era5.translate_for_file_names('prate'),
                         'tp')
        self.assertEqual(era5.translate_for_file_names('uwnd.10m'),
                         '10u')
        with self.assertRaises(StandardError) as cm:
            era5.translate_for_file_names('mslp')
        self.assertIn('Unsupported variable mslp',
                      cm.exception)

    def test_get_data_dir(self):
        scratch=os.getenv('SCRATCH')
        del os.environ['SCRATCH']
        with self.assertRaises(StandardError) as cm:
            era5.get_data_dir()
        self.assertIn('SCRATCH environment variable is undefined',
                      cm.exception)
        os.environ['SCRATCH']=scratch
        
if __name__ == '__main__':
    unittest.main()
