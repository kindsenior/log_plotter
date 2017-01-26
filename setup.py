#!/usr/bin/env python

try: # install in catkin work space
    from distutils.core import setup
    from catkin_pkg.python_setup import generate_distutils_setup

    d = generate_distutils_setup(
        packages=['log_plotter'],
        package_dir={'': 'src'},
        scripts=['src/log_plotter/LogPlotter.py'],
    )
    setup(**d)
except: # install in /usr/local/
    print('catkin is not installed. use setuptools instead')
    from setuptools import setup, find_packages
    from os.path import join
    setup(name='log_plotter',
          version='0.0.0',
          description='log plotter for hrpsys',
          packages=[join('src', package) for package in find_packages(where='./src/')],
          entry_points="""
          [console_scripts]
          log-plotter-with-pyqtgraph = log_plotter:main
          """,)

