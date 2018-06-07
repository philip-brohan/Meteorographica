#!/usr/bin/env python

# Run an xfer job to extract a month's V3 data to $SCRATCH

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
tfile.write("#SBATCH --output=%s/slurm_output/v3_extraction-%d-%d-%%j.out\n" %
                (os.getenv('SCRATCH'),args.year,args.month))
tfile.write('#SBATCH -M escori\n')
tfile.write('#SBATCH -q xfer\n')
tfile.write('#SBATCH -t 12:00:00\n')
tfile.write("#SBATCH -J V3ft%04d%02d\n" % (args.year,args.month))
tfile.write('#SBATCH -L SCRATCH\n')
tfile.write('module load python\n')
tfile.write('./month_from_tape.py --startyear=%d --year=%d --month=%d --version=%d\n' % (args.startyear,args.year,args.month,args.version))
tfile.close
print tfile.name

	 
