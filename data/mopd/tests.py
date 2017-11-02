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
Test cases for the mopd module.

Run python on this file to run all the tests.
"""
import mopd
import os
import datetime
import unittest

class TestUM(unittest.TestCase):
 
    def test_name_validate(self):
        self.assertEqual(mopd.validate_dataset_name('mogreps-g'),
                         'mogreps-g')
        self.assertEqual(mopd.validate_dataset_name('MOGREPS-G'),
                         'mogreps-g')
        with self.assertRaises(StandardError):
            mopd.validate_dataset_name('MOGREPSG')

    def test_is_file_for(self):
        self.assertTrue(mopd.is_file_for('mogreps-g',
                                         2016,3,12,0,0,3))
        self.assertFalse(mopd.is_file_for('mogreps-g',
                                          2016,3,12,2,0,3))
        self.assertFalse(mopd.is_file_for('mogreps-g',
                                          2016,3,12,24,0,3))
        self.assertFalse(mopd.is_file_for('mogreps-g',
                                          2016,3,12,0,0,0))
        self.assertFalse(mopd.is_file_for('mogreps-g',
                                         2016,3,12,0,0,175))
        self.assertFalse(mopd.is_file_for('mogreps-g',
                                          2016,3,12,0,0,4))
        self.assertFalse(mopd.is_file_for('mogreps-g',
                                         2016,3,12,0,-1,3))
        self.assertFalse(mopd.is_file_for('mogreps-g',
                                         2016,3,12,0,12,3))
        self.assertTrue(mopd.is_file_for('mogreps-uk',
                                         2016,3,12,3,0,3))
        self.assertFalse(mopd.is_file_for('mogreps-uk',
                                          2016,3,12,5,0,3))
        self.assertFalse(mopd.is_file_for('mogreps-uk',
                                          2016,3,12,24,0,3))
        self.assertFalse(mopd.is_file_for('mogreps-uk',
                                          2016,3,12,3,0,0))
        self.assertFalse(mopd.is_file_for('mogreps-uk',
                                         2016,3,12,3,0,37))
        self.assertFalse(mopd.is_file_for('mogreps-uk',
                                          2016,3,12,3,0,4))
        self.assertFalse(mopd.is_file_for('mogreps-uk',
                                         2016,3,12,3,-1,3))
        self.assertFalse(mopd.is_file_for('mogreps-uk',
                                         2016,3,12,3,23,3))
        with self.assertRaises(StandardError):
            mopd.is_file_for('mogrepsg',
                              2016,3,12,0,0,0)

    def test_make_local_file_name(self):
        self.assertEqual(mopd.make_local_file_name('mogreps-g',
                                         2016,3,12,0,0,3),
         "%s/%s/%04d/%02d/%02d/%02d/prods_op_%s_%04d%02d%02d_%02d_%02d_%03d.nc" % 
         (os.getenv('SCRATCH'),'mogreps-g',2016,3,12,0,'mogreps-g',2016,3,12,0,0,3))
        sctmp = os.getenv('SCRATCH')
        with self.assertRaises(StandardError):
            sctmp = os.getenv('SCRATCH')
            del os.environ['SCRATCH']
            mopd.make_local_file_name('mogreps-g',
                                      2016,3,12,0,0,3)
        os.environ['SCRATCH']=sctmp

    def test_make_remote_url(self):
        self.assertEqual(mopd.make_remote_url('mogreps-g',
                                         2016,3,12,0,0,3),
         "https://s3.eu-west-2.amazonaws.com/%s/prods_op_%s_%04d%02d%02d_%02d_%02d_%03d.nc" % 
         ('mogreps-g','mogreps-g',2016,3,12,0,0,3))

    def test_convert_variable_name(self):
        self.assertEqual(mopd.convert_variable_name('mogreps-g','prmsl'),
                         'air_pressure_at_sea_level')
        self.assertEqual(mopd.convert_variable_name('mogreps-uk','uwnd.10m'),
                         'x_wind_0')
        with self.assertRaises(StandardError):
             mopd.convert_variable_name('mogreps-g','mslp')

    def test_get_forecast_date_from_validity_date(self):
        vdate=datetime.datetime(2016,3,12,7)
        self.assertEqual(mopd.get_forecast_date_from_validity_date('mogreps-g',vdate,3),            
                                                   datetime.datetime(2016,3,12,3)),
        self.assertEqual(mopd.get_forecast_date_from_validity_date('mogreps-g',vdate,3.25),            
                                                   datetime.datetime(2016,3,12,3)),
        self.assertEqual(mopd.get_forecast_date_from_validity_date('mogreps-uk',vdate,3.25),            
                                                   datetime.datetime(2016,3,12,3)),
        with self.assertRaises(StandardError):
             mopd.get_forecast_date_from_validity_date('mogreps-g',vdate,1)
        with self.assertRaises(StandardError):
             mopd.get_forecast_date_from_validity_date('mogreps-g',vdate,180)
        with self.assertRaises(StandardError):
             mopd.get_forecast_date_from_validity_date('mogreps-uk',vdate,38)
        with self.assertRaises(StandardError):
             mopd.get_forecast_date_from_validity_date('mogreps-w',vdate,3)

if __name__ == '__main__':
    unittest.main()

