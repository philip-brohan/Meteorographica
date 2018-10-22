"""Setup configuration for Meteorographica package.

"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path
from io import open  # 2.7 only
import glob

# Get the long description from the README file
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Meteorographica',
    version='0.0.1',
    description='Functions for plotting weathermaps',

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
    keywords='weather map',

    # Automatically find the software to be included
    packages=find_packages(),

    # Tests are in Meteorographica/tests organised as a module
    # (a unittest.TestSuite - just put __init__.py in all directories).
    # Name the module not the file here ('.' not '/').
    test_suite="Meteorographica.tests",

    # Other packages that your project depends on.
    install_requires=[
        'scitools-iris>=2.2',
        'cartopy>=0.16',
        'numpy>1.13',
        'scipy>0.18',
        'pandas>0.20',
        'scikit-learn>0.19',
        'matplotlib>1.5,<2.0',
        'ecmwf-api-client>1.4',
    ],

    # Command line script to get the map backgrounds
    entry_points={'console_scripts': [
        'Meteorographica.fetch_backgrounds = Meteorographica.scripts:fetch_backgrounds',
    ]},
   # List additional groups of dependencies here (e.g. development
    # dependencies). Users will be able to install these using the "extras"
    # syntax, for example:
    #
    #   $ pip install sampleproject[dev]
    #
    # Similar to `install_requires` above, these must be valid existing
    # projects.
    #extras_require={  # Optional
    #    'dev': ['check-manifest'],
    #    'test': ['coverage'],
    #},

    # Data files for the examples
    data_files=[('example_data',(glob.glob('examples/data/*.nc') +
                                 glob.glob('examples/data/*.pklz')))]


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
