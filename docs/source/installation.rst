.. _installation-label:

Installation
============

Anaconda
--------
Packages for Anaconda can be installed via::

    conda install -c https://conda.anaconda.org/paulscherrerinstitute pcaspy

Binary Installers
-----------------
The binary packages are distributed at `PyPI <https://pypi.python.org/pypi/pcaspy>`_.
They have EPICS 3.14.12.4 libraries statically builtin.
If we do not have a *wheel* or *egg* package for your system, *pip* or *easy_install* will try to
build from source. And then you would need EPICS base installed, see :ref:`getting-epics`.

OS X
~~~~

Make sure you have `pip <https://pypi.python.org/pypi/pip>`_ and 
`wheel <https://pypi.python.org/pypi/wheel>`_  installed, and run::

    $ sudo pip install pcaspy

Windows
~~~~~~~

Make sure you have `pip <https://pypi.python.org/pypi/pip>`_ and
`wheel <https://pypi.python.org/pypi/wheel>`_  installed, and run::

    > C:\Python27\Scripts\pip.exe install pcaspy

Linux
~~~~~
PyPI does not allow upload linux-specific wheels package, yet (as of 2014).
The old *egg* format is used then::

    $ sudo easy_install pcaspy

Or install only for the current user::

    $ easy_install --user pcaspy


Source
------
The source can be downloaded in various ways:

  * The released source tarballs can be found at `PyPI <https://pypi.python.org/pypi/pcaspy>`_.

  * From the `git repository <https://github.com/paulscherrerinstitute/pcaspy>`_, 
    the source can be downloaded as a zip package. 

  * Clone the repository if you feel adventurous::

    $ git clone https://github.com/paulscherrerinstitute/pcaspy.git

Build
-----

.. _getting-epics:

Getting EPICS
~~~~~~~~~~~~~
In general please follow `the official installation instruction <http://www.aps.anl.gov/epics/base/R3-14/12-docs/README.html>`_. Here is a short guide,

- Get the source tarball from http://www.aps.anl.gov/epics/base/R3-14/12.php.
- Unpack it to a proper path.
- Set the following environment variables:

  - EPICS_BASE : the path containing the EPICS base source tree.
  - EPICS_HOST_ARCH : EPICS is built into static libraries on Windows.

    +---------+-------+--------------------+
    |    OS   | Arch  | EPICS_HOST_ARCH    |
    +=========+=======+====================+
    |         | 32bit | linux-x86          |
    | Linux   +-------+--------------------+
    |         | 64bit | linux-x86_64       |
    +---------+-------+--------------------+
    |         | 32bit | win32-x86-static   |
    | Windows +-------+--------------------+
    |         | 64bit | windows-x64-static |
    +---------+-------+--------------------+
    |         | PPC   | darwin-ppcx86      |
    |  OS X   +-------+--------------------+
    |         | Intel | darwin-x86         |
    +---------+-------+--------------------+

- Run ``make``.

.. note:: On windows, the Visual Studio version has to match that used to build Python.

          +------------------+-----------------------+
          | Python Version   | Visual Studio Version |
          +==================+=======================+
          | 2.6 - 2.7,       |                       |
          | 3.0 - 3.2        |  2008                 |
          +------------------+-----------------------+
          | 3.3 - 3.4        |  2010                 |
          +------------------+-----------------------+
          | 3.5              |  2015                 |
          +------------------+-----------------------+

          Mismatching may cause crashes!

Windows
~~~~~~~
- Python 2.6+ including 3.x (http://www.python.org/download/)
- SWIG 1.3.29+ is required. Get it from http://www.swig.org/download.html and unpack to ``C:\Program Files (x86)\SWIG\``.

Download the most recent source tarball, uncompress and run::

    > set PATH=%PATH%;C:\Program Files (x86)\SWIG\
    > C:\Python27\python.exe setup.py build install


Linux
~~~~~
- Python 2.6+ including 3.x
- Python headers (package name "python-dev" or similar)
- SWIG 1.3.29+ (package name "swig")

In the source directory, run::

    $ sudo python setup.py install

or install only for the current user::

    $ python setup.py build install --user

.. note:: You might need to pass *-E* flag to sudo to preserve the EPICS environment variables. If your user account
          is not allowed to do so, a normal procedure should be followed, ::

              $ su -
              # export EPICS_BASE=<epics base path>
              # export EPICS_HOST_ARCH=<epics host arch>
              # python setup.py install
            
OS X
~~~~
- SWIG (MacPorts package "swig-python")

In the source directory, run::

    $ sudo python setup.py install
