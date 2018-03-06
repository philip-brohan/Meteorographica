#!/usr/bin/env python

# Extract surface variables from a month's V3 output
#  and convert to netCDF

import tempfile
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--startyear", help="Year run started",
                    type=int, required=True)
parser.add_argument("--year", help="Year to extract",
                    type=int, required=True)
parser.add_argument("--month", help="Month to extract",
                    type=int, required=True)
parser.add_argument("--version", help="Version to extract",
                    type=int,default=451)
args = parser.parse_args()

tfile=tempfile.NamedTemporaryFile(delete=False)
tfile.write('#!/bin/bash -l\n')
tfile.write("#SBATCH --output=%s/slurm_output/v3_conversion-%d-%d-%%j.out\n" %
                (os.getenv('SCRATCH'),args.year,args.month))
tfile.write('#SBATCH -p regular\n')
tfile.write('#SBATCH -C knl\n')
tfile.write('#SBATCH -N 1\n')
tfile.write('#SBATCH -t 7:30:00\n')
tfile.write("#SBATCH -J V3co%04d%02d\n" % (args.year,args.month))
tfile.write('#SBATCH -L SCRATCH\n')
tfile.write('module load ncl\n')
tfile.write('module load python\n')
tfile.write('./extract_anl_var.py --startyear=%d --year=%d --month=%d --version=%d --var=prmsl &\n' % (args.startyear,args.year,args.month,args.version))
tfile.write('./extract_anl_var.py --startyear=%d --year=%d --month=%d --version=%d --var=air.2m &\n' % (args.startyear,args.year,args.month,args.version))
tfile.write('./extract_anl_var.py --startyear=%d --year=%d --month=%d --version=%d --var=uwnd.10m &\n' % (args.startyear,args.year,args.month,args.version))
tfile.write('./extract_anl_var.py --startyear=%d --year=%d --month=%d --version=%d --var=vwnd.10m &\n' % (args.startyear,args.year,args.month,args.version))
tfile.write('./extract_anl_var.py --startyear=%d --year=%d --month=%d --version=%d --var=air.sfc &\n' % (args.startyear,args.year,args.month,args.version))
tfile.write('./extract_anl_var.py --startyear=%d --year=%d --month=%d --version=%d --var=icec &\n' % (args.startyear,args.year,args.month,args.version))
tfile.write('./extract_fg_var.py --startyear=%d --year=%d --month=%d --version=%d --var=prate &\n' % (args.startyear,args.year,args.month,args.version))
tfile.write('./extract_obs.py --startyear=%d --year=%d --month=%d --version=%d &\n' % (args.startyear,args.year,args.month,args.version))
tfile.write('wait\n')
tfile.close
print tfile.name

	 
