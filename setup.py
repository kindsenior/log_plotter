#!/usr/bin/env python
import log_plotter
VERSION=log_plotter.__version__

try: # install in catkin work space
    from distutils.core import setup
    from catkin_pkg.python_setup import generate_distutils_setup

    d = generate_distutils_setup(
        packages=['log_plotter'],
        package_dir={'': 'src'},
        scripts=['src/log_plotter/datalogger_plotter_with_pyqtgraph.py'],
        version=VERSION
    )
    setup(**d)
except: # install in /usr/local/
    print('catkin is not installed. use setuptools instead')
    from setuptools import setup, find_packages
    from os.path import join
    setup(name='log_plotter',
          version=VERSION,
          description='log plotter for hrpsys',
          packages=[join('src', package) for package in find_packages(where='./src/')],
          entry_points="""
          [console_scripts]
          datalogger-plotter-with-pyqtgraph = log_plotter:main
          """,)

