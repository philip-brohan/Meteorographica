# Meteorographica example script

# Set up the figure and add the continents as background
# Overlay pressure spaghetti plot

import Meteorographica as mg
import iris

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import cartopy
import cartopy.crs as ccrs

import pkg_resources

# Define the figure (page size, background color, resolution, ...
aspect=16/9.0
fig=Figure(figsize=(22,22/aspect),              # Width, Height (inches)
           dpi=100,
           facecolor=(0.88,0.88,0.88,1),
           edgecolor=None,
           linewidth=0.0,
           frameon=False,                # Don't draw a frame
           subplotpars=None,
           tight_layout=None)
# Attach a canvas
canvas=FigureCanvas(fig)

# All mg plots use Rotated Pole: choose a rotation that shows the global
#  circulation nicely.
projection=ccrs.RotatedPole(pole_longitude=160.0,
                                pole_latitude=45.0,
                                central_rotated_longitude=-40.0)

# Define an axes to contain the plot. In this case our axes covers
#  the whole figure
ax = fig.add_axes([0,0,1,1],projection=projection)
ax.set_axis_off() # Don't want surrounding x and y axis
# Set the axes background colour
ax.background_patch.set_facecolor((0.88,0.88,0.88,1))

# Lat and lon range (in rotated-pole coordinates) for plot
extent=[-180.0,180.0,-90.0,90.0]
ax.set_extent(extent, crs=projection)
# Lat:Lon aspect does not match the plot aspect, ignore this and
#  fill the figure with the plot.
matplotlib.rc('image',aspect='auto')

# Draw a lat:lon grid
mg.background.add_grid(ax,
                       sep_major=5,
                       sep_minor=2.5,
                       color=(0,0.3,0,0.2))


# Add the land
land_img=ax.background_img(name='GreyT', resolution='low')

# Get pressure ensemble
edf=pkg_resources.resource_filename(
      pkg_resources.Requirement.parse('Meteorographica'),
                 'example_data/20CR2c.1987101606.prmsl.nc')
prmsl=iris.load_cube(edf)

mg.pressure.plot(ax,prmsl,scale=0.01,type='spaghetti',
                 resolution=0.25)

# Add a label showing the date
label="16th October 1987 at 06 GMT"
mg.utils.plot_label(ax,label,
                    facecolor=fig.get_facecolor())

# Render the figure as a png
fig.savefig('spaghetti.png')
