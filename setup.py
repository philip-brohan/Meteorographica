"""Setup configuration for Meteorographica package.

"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path
from io import open  # 2.7 only

# Get the long description from the README file
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Meteorographica',
    version='0.0.1',
    description='A personal library for weather data',

    # From README - see above
    long_description=long_description,
    #long_description_content_type='text/x-rst',

    url='https://brohan.org/Meteorographica/',

    author='Philip Brohan',
    author_email='philip.brohan@metofice.gov.uk',

    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Atmospheric Science',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
    ],

    # Keywords for your project. What does your project relate to?
    keywords='weather map reanalysis 20cr cera20c era5',

    packages=find_packages(),

    # Other packages that your project depends on.
    # iris>2 - does not work - can't find any iris?
    install_requires=[
        'cartopy>0.15',
        'numpy>1.13',
        'scipy>0.18',
        'pandas>0.20',
        'scikit-learn>0.19',
        'matplotlib>1.5,<2.0',
        'ecmwf-api-client>1.4',
    ],

    # List additional groups of dependencies here (e.g. development
    # dependencies). Users will be able to install these using the "extras"
    # syntax, for example:
    #
    #   $ pip install sampleproject[dev]
    #
    # Similar to `install_requires` above, these must be valid existing
    # projects.
    extras_require={  # Optional
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },

    # Data files included in your package
    # Note - move the background files into this.
    #package_data={ 
    #    'Meteographica': ['*.dat'],
    #},

    # other relevant URLs.
    #project_urls={ 
    #    'Bug Reports': 'https://github.com/philip-brohan/Meteorographica/issues',
    #    'Source': 'https://github.com/philip-brohan/Meteorographica',
    #},
)
