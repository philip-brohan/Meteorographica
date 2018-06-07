#!/usr/bin/env python

# Allocate a set of points using modified Bridson and plot them
import Meteorographica.weathermap as wm

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--lat_min", help="Min latitude",
                    type=float, default=-90.0)
parser.add_argument("--lat_max", help="Max latitude",
                    type=float, default=90.0)
parser.add_argument("--lon_min", help="Min longitude",
                    type=float, default=-180.0)
parser.add_argument("--lon_max", help="Max longitude",
                    type=float, default=180.0)
parser.add_argument("--scale", help="Month to extract",
                    type=int, default=5)
args = parser.parse_args()

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Circle

# Set aspect ratio from lat and lon ranges
aspect=(args.lat_max-args.lat_min)/(args.lon_max-args.lon_min)
fig=Figure(figsize=(10,10*aspect),  # Width, Height (inches)
           dpi=100,
           facecolor=(0.88,0.88,0.88,1),
           edgecolor=None,
           linewidth=0.0,
           frameon=False,
           subplotpars=None,
           tight_layout=None)
canvas=FigureCanvas(fig)
ax=fig.add_axes([0,0,1,1])
ax.set_xlim(args.lon_min,args.lon_max)
ax.set_ylim(args.lat_min,args.lat_max)

# Get the points
vp=wm.allocate_vector_points(initial_points=None,
                           lat_range=(args.lat_min,args.lat_max),
                           lon_range=(args.lon_min,args.lon_max),
                           scale=args.scale,
                           random_state=None,
                           max_points=10000)

# Plot the points
for i in range(0,len(vp['Age'])):
    ax.add_patch(Circle((vp['Longitude'][i],
                         vp['Latitude'][i]),
                        radius=1.0,
                        facecolor='red',
                        edgecolor='red',
                        alpha=1.0,
                        zorder=2))

fig.savefig('test_allocate_vector_points.png')
