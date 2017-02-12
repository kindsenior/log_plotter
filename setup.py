#!/usr/bin/env python
from xml.etree import ElementTree
import os

# read package.xml and get version
VERSION=ElementTree.parse("package.xml").getroot().find("version").text
SCRIPTDIR = os.path.abspath(os.path.dirname(__file__))

# get commit hash
from subprocess import check_output
try:
    GIT_REVISION = check_output(["git", "rev-parse", "HEAD"]).replace("\n","")
except:
    GIT_REVISION = ""

# write into version.py
with open(os.path.join(SCRIPTDIR, "src","log_plotter","version.py"),"w") as version_py:
    version_py.writelines("# THIS FILE IS GENERATED FROM LOG_PLOTTER SETUP.PY\n")
    version_py.writelines("version='{}'\n".format(VERSION))
    version_py.writelines("git_revision='{}'\n".format(GIT_REVISION))
   
# setup log_plotter using distutils
from distutils.core import setup
from setuptools import setup, find_packages
from os.path import join
setup(name='log_plotter',
      version=VERSION,
      description='log plotter for hrpsys',
      packages=['log_plotter'],
      package_dir={'': 'src'},
      scripts=['src/log_plotter/datalogger_plotter_with_pyqtgraph.py'],
)
