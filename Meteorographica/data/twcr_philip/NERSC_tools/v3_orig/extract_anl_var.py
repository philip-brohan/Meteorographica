#!/usr/bin/env python

# Extract 20CRv3 analysis variable from the full output

import os
import sys
import subprocess
import tempfile
import datetime

# Version and month
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--startyear", help="Year run started",
                    type=int, required=True)
parser.add_argument("--year", help="Year to extract",
                    type=int, required=True)
parser.add_argument("--month", help="Month to extract",
                    type=int, required=True)
parser.add_argument("--version", help="Month to extract",
                    type=int,default=451)
parser.add_argument("--var", help="Variable to extract",
                    type=str, required=True)
args = parser.parse_args()

# Each variable needs a search which finds it (uniquely) in the grib
search_strings={
    'prmsl'   : 'PRMSL',
    'air.2m'  : 'TMP.*:2 m',
    'uwnd.10m': 'UGRD.*:10 m above gnd',
    'vwnd.10m': 'VGRD.*:10 m above gnd',
    'air.sfc' : 'TMP.*:sfc',
    'icec'    : 'ICEC'
}
if args.var not in search_strings:
    raise StandardError("Unsupported variable %s" % args.var)  

# Where to find the grib (and obs) files retrieved from hsi
working_directory="%s/20CRv3.working.orig/ensda_%04d/%04d/%02d" % (
                   os.getenv('SCRATCH'),args.startyear,
                   args.year,args.month)
if not os.path.isdir(working_directory):
    os.makedirs(working_directory)
# Where to put the final output files for this month
final_directory="%s/20CRv3.final/version_%1d.%1d.%1d/%04d/%02d" % (
                  os.getenv('SCRATCH'),int(args.version/100),
                  int((args.version%100)/10),int(args.version%10),
                  args.year,args.month)
if not os.path.isdir(final_directory):
    os.makedirs(final_directory)

# Use the wgrib utility for data extraction
wgrib='/global/homes/c/compo/bin/wgrib'

# Don't repeat pre-existing extractions
fn= "%s/%s.nc4" % (final_directory,args.var)
if os.path.isfile(fn):
    raise StandardError('Already done')

# Temporary file for staging extracted data
tfile=tempfile.NamedTemporaryFile(delete=False)

current_day=datetime.datetime(args.year,args.month,2,0)
while current_day.month==args.month:
    # Extract grids every 3 hours and concatenate to output
    subdir=None
    for hour in range(0,24,3):
        if hour%6==0: 
            subdir="%04d%02d%02d%02d" % (current_day.year,
              current_day.month,current_day.day,hour)
        for member in range(1,81):
            an_file_name= "%s/%s/pgrbanl_%04d%02d%02d%02d_mem%03d" % (
                            working_directory,subdir,
                            current_day.year,
                            current_day.month,current_day.day,
                            hour,member)
            if not os.path.exists(an_file_name):
                raise StandardError("Missing data %s" % an_file_name)

            proc = subprocess.Popen(
              "%s %s | grep '%s' | %s -i -grib %s -o %s; cat %s >> %s/%s.grb" % (
                                    wgrib,an_file_name,
                                    search_strings[args.var],
                                    wgrib,an_file_name,
                                    tfile.name,tfile.name,
                                    final_directory,args.var),
                                    shell=True)
            (out, err) = proc.communicate()
            if out is not None or err is not None:
                raise StandardError("Failed to extract %s from %s" % (
                                     args.var,an_file_name))
   
    current_day=current_day+datetime.timedelta(days=1)
os.remove(tfile.name)

# Convert to netCDF
proc = subprocess.Popen(
  "ncl_convert2nc %s.grb -i %s -o %s -nc4c -cl 5" % ( 
                        args.var,
                        final_directory,
                        final_directory),
                        shell=True)
(out, err) = proc.communicate()
if out is not None or err is not None:
    raise StandardError("Failed to convert %s to netCDF" % args.var)
# Strip out unnecessary dimensions that confuse iris
proc = subprocess.Popen("ncks -C -O -x -v ensemble0_info,initial_time1,initial_time1_encoded "+
                        "%s/%s.nc4 %s/%s.stripped.nc4" % (final_directory,args.var,
                                                          final_directory,args.var),
                        shell=True)
(out, err) = proc.communicate()
if out is not None or err is not None:
    raise StandardError("Failed to strip %s netCDF file" % args.var)
os.rename("%s/%s.stripped.nc4" % (final_directory,args.var),
          "%s/%s.nc4" % (final_directory,args.var))

