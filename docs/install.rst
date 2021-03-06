Installation
============

Known to work on with Python 3.6 on modern Linux and OS X systems. Not tested on anything else.

Relies on `SciTools <http://scitools.org.uk/>`_. So first install `Iris <http://scitools.org.uk/iris/docs/latest/index.html>`_ and `Cartopy <http://scitools.org.uk/cartopy/docs/latest/index.html>`_

One environment variable must be set:

* CARTOPY_USER_BACKGROUNDS (may be set during Cartopy installation) - the name of a directory to put plot background images in.

Also requires:

* `pandas <http://pandas.pydata.org>`_: Python package providing high-performance, easy-to-use data structures and data analysis tools.
* `scikit.learn <http://scikit-learn.org/stable>`_: Python package containing statistical modelliong and machine learning tools.
* `wget <https://www.gnu.org/software/wget/>`_: To download background data.
* `unzip <http://www.info-zip.org/mans/unzip.html>`_: To unpack the background data.
* `imagemagick convert <https://www.imagemagick.org/script/convert.php>`_. To make optimised backgrounds.

Then install the package from the source in `<https://github.com/philip-brohan/Meteorographica>`_.

Finally, run the package setup script to produce the plot backgrounds:

.. code-block:: sh

    Meteorographica.fetch_backgrounds

You should then be able to reproduce `the examples <examples/examples.html>`_.
