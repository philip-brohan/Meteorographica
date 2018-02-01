#!/usr/bin/env python

# Copy the observations files into output 

import os
import datetime
from shutil import copyfile

# Version and month
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--startyear", help="Ensda start year",
                    type=int, required=True)
parser.add_argument("--year", help="Year to extract",
                    type=int, required=True)
parser.add_argument("--month", help="Month to extract",
                    type=int, required=True)
parser.add_argument("--version", help="Month to extract",
                    type=int,default=451)
args = parser.parse_args()

# Where to find the grib (and obs) files retrieved from hsi
working_directory="%s/20CRv3.working/ensda_%04d/%04d/%02d" % (
                   os.getenv('SCRATCH'),args.startyear,
                   args.year,args.month)
if not os.path.isdir(working_directory):
    raise StandardError('No working directory')
# Where to put the final output files for this month
final_directory="%s/20CRv3.final/version_%1d.%1d.%1d/%04d/%02d" % (
                  os.getenv('SCRATCH'),int(args.version/100),
                  int((args.version%100)/10),int(args.version%10),
                  args.year,args.month)
if not os.path.isdir(final_directory):
    os.makedirs(final_directory)
if not os.path.isdir("%s/observations" % final_directory):
    os.makedirs("%s/observations" % final_directory)

current_day=datetime.datetime(args.year,args.month,1,0)
while current_day.month==args.month:
    # Copy the obs, every 6 hours
    for hour in range(0,24,6):
        obs_dir_name= "%s/%04d%02d%02d%02d" % (
                         working_directory,current_day.year,
                         current_day.month,current_day.day,
                         hour)
        for o_file in ('psobs.txt','psobs_prior.txt',
                                 'psobs_posterior.txt'):   
            if not os.path.exists("%s/%s" % (obs_dir_name,o_file)):
                raise StandardError("Missing data %s/%s" % (
                                         obs_dir_name,o_file))
            copyfile("%s/%s" % (obs_dir_name,o_file),
                     "%s/observations/%04d%02d%02d%02d_%s" % (
                      final_directory,current_day.year,
                         current_day.month,current_day.day,
                         hour,o_file))
   
    current_day=current_day+datetime.timedelta(days=1)

